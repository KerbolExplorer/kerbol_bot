import sqlite3

db = sqlite3.connect("db_exp.db")
cursor = db.cursor()

try:
    sql = "CREATE TABLE Usuarios (id INTEGER, xp INTEGER, level INTEGER, xp_next INTEGER)"
    cursor.execute(sql)
except sqlite3.OperationalError:
    pass
'''                                #0 1 2 3
sql = "INSERT INTO Usuarios (id, xp, level, xp_next) VALUES (?, ?, ?, ?)"
values = (621, 25, 2, 100)
cursor.execute(sql, (621, 25, 2, 100))
values = (622, 26, 2, 200)
cursor.execute(sql, (622, 26, 2, 200))        #id = 0
sql = "SELECT * FROM Usuarios"                #xp = 1
cursor.execute(sql)                           #level = 2
result = cursor.fetchall()                    #xp_next = 3
print(result)              #fetchall de toda la tabla devuelve [(id, xp, level, xp_next), (id, xp, level, 2, 200)....]
sample = [('Jack', 76), ('Beneth', 78), ('Cirus', 77), ('Faiz', 79)]
sample.sort(key=lambda a: a[1], reverse=True)
print(sample)'''