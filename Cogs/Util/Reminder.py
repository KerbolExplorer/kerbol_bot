import discord
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import asyncio
import sqlite3

class Reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not self.send_reminder.is_running():
            self.send_reminder.start()

        reminder_db = sqlite3.connect("reminders.db")
        reminder_cursor = reminder_db.cursor()
        sql = "SELECT name FROM sqlite_master WHERE type= 'table' AND name= 'Reminders'"
        reminder_cursor.execute(sql)
        result = reminder_cursor.fetchall()
        if not result:
            sql = "CREATE TABLE 'Reminders' (reminderId INTEGER, userId INTEGER, name TEXT, description TEXT, time TEXT, unixTime INTEGER)"
            reminder_cursor.execute(sql)
        reminder_db.commit()
        reminder_db.close()

    def get_time(self):
        return int(datetime.now(timezone.utc).timestamp())
    
    class Reminder_Modal(discord.ui.Modal, title="Create a Reminder"):
        name = discord.ui.TextInput(label="Reminder Name", max_length=100)
        description = discord.ui.TextInput(label="Description", style=discord.TextStyle.paragraph, required=False, max_length=2000)
        date = discord.ui.TextInput(label="Date & Time (DD-MM-YYYY HH:MM)", placeholder="e.g. 14-11-2025 14:30")
        user_timezone = discord.ui.TextInput(label="Timezone", placeholder="Z+1")

        async def on_submit(self, interaction: discord.Interaction):
            try:
                reminder_time = datetime.strptime(self.date.value, "%d-%m-%Y %H:%M")
            except ValueError:
                await interaction.response.send_message("The date is in an invalid format! Please use DD-MM-YYYY HH:MM", ephemeral=True)
                return
        
            tz_input = self.user_timezone.value.strip().upper()
            try:
                if not tz_input.startswith("Z") or len(tz_input) < 2:
                    raise ValueError("Invalid format")

                sign = tz_input[1]
                offset_hours = int(tz_input[2:])

                if sign == '+':
                    offset = timedelta(hours=offset_hours)
                elif sign == '-':
                    offset = timedelta(hours=-offset_hours)
                else:
                    raise ValueError("Invalid sign")

                user_tz = timezone(offset)
                aware_time = reminder_time.replace(tzinfo=user_tz)
                utc_time = aware_time.astimezone(timezone.utc)

            except ValueError:
                await interaction.response.send_message(
                    "Invalid time zone format!, please use zulu time (Z+1, Z-3). Use `/zulu_time` to know the current zulu time", ephemeral=True
                )
                return

            unix_time = int(utc_time.timestamp())

            if unix_time < int(datetime.now(timezone.utc).timestamp()):
                await interaction.response.send_message("You have selected a time from the past...", ephemeral=True)
                return

            reminder_db = sqlite3.connect("reminders.db")
            reminder_cursor = reminder_db.cursor()

            sql = "SELECT * FROM Reminders ORDER BY reminderId DESC LIMIT 1"
            reminder_cursor.execute(sql)
            reminder_id = reminder_cursor.fetchall()
            if reminder_id == []:
                reminder_id = 0
            else:
                reminder_id = (reminder_id[0][0] + 1)

            sql = "INSERT INTO Reminders (reminderId, userId, name, description, time, unixTime) VALUES (?, ?, ?, ?, ?, ?)"
            reminder_cursor.execute(sql, (reminder_id, interaction.user.id, self.name.value, self.description.value, reminder_time, unix_time))

            await interaction.response.send_message(f"Reminder **{self.name}**, successfully set! I'll notify you on {self.date}", ephemeral=True)
            reminder_db.commit()
            reminder_db.close()

    @app_commands.command(name="remindme", description="Have Solgaleo remind you of something")
    async def remindme(self, interaction:discord.Interaction):
        await interaction.response.send_modal(self.Reminder_Modal())

    @app_commands.command(name="quick_remind", description="Set a quick reminder for the immediate future")
    @app_commands.describe(title="The title of the reminder", time="How many seconds until I remind you")
    async def quick_remind(self, interaction:discord.Interaction, title:str, time:int):
            reminder_db = sqlite3.connect("reminders.db")
            reminder_cursor = reminder_db.cursor()

            if time < 60:
                await interaction.response.send_message("Reminders need to be at least 60 seconds away", ephemeral=True)
                return
            else:
                sql = "SELECT * FROM Reminders ORDER BY reminderId DESC LIMIT 1"
                reminder_cursor.execute(sql)
                reminder_id = reminder_cursor.fetchall()
                if reminder_id == []:
                    reminder_id = 0
                else:
                    reminder_id = (reminder_id[0][0] + 1)
                
                unix_time = self.get_time() + time
                formated_time = datetime.fromtimestamp(unix_time).strftime("%d-%m-%Y %H:%M")

                sql = "INSERT INTO Reminders (reminderId, userId, name, description, time, unixTime) VALUES (?, ?, ?, ?, ?, ?)"
                reminder_cursor.execute(sql, (reminder_id, interaction.user.id, title, "", formated_time, unix_time))
            
            await interaction.response.send_message(f"Reminder **{title}**, has been successfully set! I'll remind you in {time} seconds")
            reminder_db.commit()
            reminder_db.close()

    @app_commands.command(name="remind_list", description="Shows a list with all your current reminders")
    async def remind_list(self, interaction:discord.Interaction):
        reminder_db = sqlite3.connect("reminders.db")
        reminder_cursor = reminder_db.cursor()

        sql = "SELECT * FROM Reminders WHERE userId = ?"
        reminder_cursor.execute(sql, (interaction.user.id,))
        result = reminder_cursor.fetchall()
        if result == []:
            await interaction.response.send_message("You do not have any reminders", ephemeral=True)
        else:
            embed = discord.Embed(
                title="**Your Reminders**",
                color=0xf1c40f
            )
            reminders = ""
            for reminder in result:
                reminders += f"ID: {reminder[0]}, Title: {reminder[2]}, Date: {reminder[4]}\n"
            embed.description=reminders
            await interaction.response.send_message("Here are your reminders: ", embed=embed, ephemeral=True)
        
        reminder_db.close()

    @app_commands.command(name="remind_cancel", description="Cancels a chosen reminder")
    @app_commands.describe(
        id="The id of the reminder you wish to cancel. You can find this number by doing /remind_list",
        delete_all="Write anything here to delete all reminders"
        )
    async def remind_cancel(self, interaction:discord.Interaction, id: int, delete_all:str = "False"):
        reminder_db = sqlite3.connect("reminders.db")
        reminder_cursor = reminder_db.cursor()

        sql = "SELECT * FROM Reminders WHERE userId = ?"
        reminder_cursor.execute(sql, (interaction.user.id,))
        result = reminder_cursor.fetchall()
        if result == []:
            await interaction.response.send_message("You do not have any reminders", ephemeral=True)
        else:
            if delete_all != "False":
                sql = "DELETE FROM Reminders WHERE userId = ?"
                reminder_cursor.execute(sql, (interaction.user.id,))
                await interaction.response.send_message("All your reminders have been deleted", ephemeral=True)
            else:
                sql = "DELETE FROM Reminders WHERE userId = ? AND reminderId = ?"
                reminder_cursor.execute(sql, (interaction.user.id, id))
                await interaction.response.send_message(f"The request with id **{id}** has been deleted")

        reminder_db.commit()
        reminder_db.close()

    @tasks.loop(minutes=1)
    async def send_reminder(self):
        reminder_db = sqlite3.connect("reminders.db")
        reminder_cursor = reminder_db.cursor()
        sql = "SELECT * FROM Reminders"
        reminder_cursor.execute(sql)
        users = reminder_cursor.fetchall()
        current_time = self.get_time()

        if users != []:
            for user in users:
                if int(user[5]) < current_time:
                    user_target = await self.bot.fetch_user(user[1])

                    embed = discord.Embed(
                        title=f"**{user[2]}**",
                        color=0xf1c40f,
                    )

                    if user[3] == "":
                        embed.description = "No description"
                    else:
                        embed.description = user[3]

                    embed.set_footer(text=f"Targeted for {user[4]}")

                    await user_target.send(f"Hello!", embed=embed)
                    
                    sql = "DELETE FROM Reminders WHERE reminderId = ?"
                    reminder_cursor.execute(sql, (user[0],))
                    reminder_db.commit()
                else:
                    continue

        reminder_db = sqlite3.connect("reminders.db")
        reminder_cursor = reminder_db.cursor()



async def setup(bot):
    await bot.add_cog(Reminder(bot))