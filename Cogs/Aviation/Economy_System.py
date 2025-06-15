import discord
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime, timezone
import sqlite3
import os

DB_AIRLINE_PATH = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "airlines.db")
DB_BANK_PATH = os.path.join(os.path.dirname(__file__), "Aviation_Databases", "bank.db")

MAX_LOAN = 5000000
INTEREST = 1.1



class Bank(commands.Cog):
    def __init__(self, bot:discord.Client):
        self.bot = bot

        if not self.pay_loan.is_running():
            self.pay_loan.start()

        db = sqlite3.connect(DB_BANK_PATH)
        cursor = db.cursor()

        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='Loans'"
        cursor.execute(sql)
        result = cursor.fetchall()
        if not result:
            sql = "CREATE TABLE IF NOT EXISTS 'Loans' (airlineId INTEGER, loan INTEGER, remaining INTEGER, interest FLOAT, payments INTEGER, next INTEGER)"
            cursor.execute(sql)
        db.commit()
        db.close()


    @app_commands.command(name="loan", description="Allows you to take a loan for your airline")
    @app_commands.describe(amount="The amount of money you want to take, the maximum for any airline is 5M")
    async def loan(self, interaction:discord.Interaction, amount:int):
        await interaction.response.defer()

        if amount > MAX_LOAN:
            await interaction.followup.send("You cannot take out more than 5 million")
            return
        elif amount < 1000:
            await interaction.followup.send("You need to take out more than 1000")
            return

        airline_db = sqlite3.connect(DB_AIRLINE_PATH)
        airline_cursor = airline_db.cursor()

        sql = "SELECT airlineId, money FROM Airline where owner = ?"
        airline_cursor.execute(sql, (interaction.user.id,))
        airline_data = airline_cursor.fetchone()

        if airline_data == None:
            await interaction.followup.send("You do not own an airline")
            airline_db.close()
            return
        
        airline_id = airline_data[0]

        db = sqlite3.connect(DB_BANK_PATH)
        cursor = db.cursor()

        sql = "SELECT * FROM Loans WHERE airlineId = ?"
        cursor.execute(sql, (airline_id,))

        airline_loan = cursor.fetchone()
        has_loan = False

        if airline_loan:
            has_loan = True
            if airline_loan[1] +  amount > MAX_LOAN:
                await interaction.followup.send("You cannot have your loan exceed 5 million")
                return
            else:
                raw_loan = airline_loan[1] + amount
        else:
            raw_loan = amount

        if raw_loan <= 1_000_000:
            interest_rate = 1.05
            payment_rate = 0.025
        elif raw_loan <= 2_500_000:
            interest_rate = 1.08
            payment_rate = 0.02
        elif raw_loan <= 4_000_000:
            interest_rate = 1.10
            payment_rate = 0.015
        else:
            interest_rate = 1.12
            payment_rate = 0.01

        total_repayable = int(raw_loan * interest_rate)
        payment_amount = int(total_repayable * payment_rate)

        user = interaction.user.id

        class Buttons(discord.ui.View):
            def __init__(self, *, timeout = 180):
                super().__init__(timeout=timeout)

            @discord.ui.button(label="✅", style=discord.ButtonStyle.green)
            async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if interaction.user.id != user:
                    await interaction.response.defer(ephemeral=True)
                    await interaction.followup.send("You are not the person getting this loan", ephemeral=True)
                    return

                await self.disable_buttons(self, interaction)
                next = int(datetime.now(timezone.utc).timestamp()) + 86400
                if has_loan:
                    sql = "UPDATE Loans SET loan = ?, remaining = ?, interest = ?, payments = ?"
                    cursor.execute(sql, (raw_loan, total_repayable, interest_rate, payment_amount))
                else:
                    sql = "INSERT INTO Loans (airlineId, loan, remaining, interest, payments, next) VALUES (?, ?, ?, ?, ?, ?)"
                    cursor.execute(sql, (airline_id, amount, total_repayable, interest_rate, payment_amount, next))

                new_balance = airline_data[1] + amount

                sql = "UPDATE Airline SET money = ? WHERE airlineId = ?"
                airline_cursor.execute(sql, (new_balance, airline_id))
                await interaction.followup.send("Loan taken sucesfully!")
                db.commit()
                db.close()
                airline_db.commit()
                airline_db.close()
            
            @discord.ui.button(label="❌", style=discord.ButtonStyle.red)
            async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if interaction.user.id != user:
                    await interaction.response.defer(ephemeral=True)
                    await interaction.followup.send("You are not the person getting this loan", ephemeral=True)
                    return

                await self.disable_buttons(self, interaction)

                await interaction.followup.send("The process has been cancelled.")
                db.close()
                airline_db.close()
                
            async def disable_buttons(self, child:discord.ui.Button, interaction: discord.Interaction):
                for child in self.children:
                    child.disabled = True
                await interaction.message.edit(view=self)

        if has_loan:
            embed = discord.Embed(
                title="New Loan information",
                color=0xf1c40f,
                description="Payments are taken daily"
            )

            embed.add_field(name="Amount to take", value=amount)
            embed.add_field(name="Interest", value=interest_rate)
            embed.add_field(name="New total pay", value=total_repayable)
            embed.add_field(name="New payment amount", value=payment_amount)
            embed.set_footer(text="You already had a loan, so this loan has been added to it")

        else:    
            embed = discord.Embed(
                title="Loan information",
                color=0xf1c40f,
                description="Payments are taken daily"
            )

            embed.add_field(name="Amount to take", value=amount)
            embed.add_field(name="Interest", value=interest_rate)
            embed.add_field(name="Total to pay", value=total_repayable)
            embed.add_field(name="Payment amount", value=payment_amount)
            embed.set_footer(text="Total to pay will be added onto your previous loan if you had one.")


        await interaction.followup.send(embed=embed, view=Buttons())
    
    @tasks.loop(minutes=10)
    async def pay_loan(self):
        bank_db = sqlite3.connect(DB_BANK_PATH)
        bank_cursor = bank_db.cursor()
        airline_db = sqlite3.connect(DB_AIRLINE_PATH)
        airline_cursor = airline_db.cursor()
        sql = "SELECT * FROM Loans"
        bank_cursor.execute(sql)
        users = bank_cursor.fetchall()

        current_time = int(datetime.now(timezone.utc).timestamp())

        if users != []:
            for user in users:
                if int(user[5]) < current_time:
                    sql = "SELECT owner, money FROM Airline WHERE airlineId = ?"
                    airline_cursor.execute(sql, (user[0],))
                    airline_info = airline_cursor.fetchone()   

                    new_money = airline_info[1] - user[4]
                    sql = "UPDATE Airline SET money = ? WHERE airlineId = ?"
                    airline_cursor.execute(sql, (new_money, user[0]))


                    remaining = user[2] - user[4]

                    user_target = await self.bot.fetch_user(int(airline_info[0]))

                    if remaining <= 0:
                        sql = "DELETE FROM Loans WHERE airlineId = ?"
                        bank_cursor.execute(sql, (user[0],))
                        await user_target.send("Hey there, the loan you have taken has been fully paid off!")
                    else:
                        sql = "UPDATE Loans SET remaining = ?, next = ? WHERE airlineId = ?"
                        next = int(datetime.now(timezone.utc).timestamp()) + 86400
                        bank_cursor.execute(sql, (remaining, next, user[0]))
                        await user_target.send(f"Hey there, the daily payment of the loan has been sucessfully done")
                else:
                    continue

        bank_db.commit()
        airline_db.commit()
        airline_db.close()
        bank_db.close()




async def setup(bot):
    await bot.add_cog(Bank(bot))