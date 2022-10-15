import sqlite3
from collections import namedtuple
con = sqlite3.connect(':memory:')
con.row_factory = sqlite3.Row
cur = con.cursor()
print(con.execute("create table users(id integer, name text);"))
print(con.execute("insert into users values(0, 'A');"))
print(con.execute("insert into users values(1, 'B');"))
print(con.execute("select count(*) from users;").fetchone().keys())
print(con.execute("select count(*) num from users;").fetchone().keys())
print(con.execute("select count(*) num from users;").fetchone()['num'])
print(con.execute("select count(*) num from users;").fetchall())
#rows = con.execute("select count(*) from users;").fetchall() # ValueError: Type names and field names must be valid identifiers: 'count(*)'
#rows = con.execute("select count(*) num from users;").fetchall()
rows = con.execute("select count(*) num from users where id>=?;", (0,)).fetchall()
print(rows[0].keys())
print(rows[0])
print(rows[0][0])
#print(rows[0]['name']) #IndexError: No item with that key
Row = namedtuple('Row', rows[0].keys())
print([Row(*row) for row in rows])
#con.commit()
con.close()

