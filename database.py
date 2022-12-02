
import sqlite3

connect = sqlite3.connect('database.db', check_same_thread=False)
cursor = connect.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS "users" (
	"id"	INTEGER NOT NULL,
	"login"	TEXT NOT NULL,
	"password" TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);''')

cursor.execute('''CREATE TABLE IF NOT EXISTS "links" (
	"id"	INTEGER NOT NULL,
	"full_link"	TEXT NOT NULL,
	"short_link" TEXT NOT NULL,
	"access" INTEGER NOT NULL,
	"redirect_count" INTEGER NOT NULL,
	"user" INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);''')

connect.commit()