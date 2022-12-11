import sqlite3

# установление соединения с базой данных
connect = sqlite3.connect('database.db', check_same_thread=False)
cursor = connect.cursor()

# создание таблиц в базе данных
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


# добавление нового пользователя в базу данных
def database_register(login, password):
    res = cursor.execute('SELECT login, password FROM users WHERE login=? AND password=?', (login, password)).fetchone()
    if res is None:
        cursor.execute('INSERT INTO users(login, password) VALUES (?, ?)', (login, password))
        connect.commit()
        return True


# проверка хэшированного пароля
def password_from_db(login):
    return cursor.execute('SELECT password FROM users WHERE login=? ', (login,)).fetchone()[0]


# сверка введенного логина пользователя с его логином из базы данных
def check_user_is_correct(login):
    return cursor.execute('SELECT login FROM users WHERE login=?', (login,)).fetchone()


# добавление новой ссылки в базу данных
def add_new_link(full_link, short_link, access, login):
    cursor.execute('INSERT INTO links(full_link, short_link, access, redirect_count, user) VALUES (?, ?, ?, 0, ?)',
                   (full_link, short_link, access, login))
    connect.commit()


# вывод списка ссылок пользователя
def get_list_user_links(login):
    res = cursor.execute('SELECT short_link FROM links WHERE user = ?', (login,)).fetchall()
    name_links = ''
    for el in res:
        name_links += f'{el[0]}\n'
    return name_links


# удаление выбранной ссылки из базы данных
def del_link_from_db(login, short_link):
    cursor.execute('DELETE FROM links WHERE user = ? AND short_link = ?', (login, short_link))
    connect.commit()


# обновление имени выбранной ссылки
def update_link_from_db(login, new_link, old_link):
    cursor.execute('UPDATE links SET short_link = ? WHERE user = ? AND short_link = ?', (new_link, login, old_link))
    connect.commit()


# обновление уровня доступа выбранной ссылки
def update_access_from_db(login, link, new_access):
    cursor.execute('UPDATE links SET access = ? WHERE user = ? AND short_link = ?', (new_access, login, link))
    connect.commit()


# вывод уровня доступа ссылки
def check_access(short_link):
    res = cursor.execute('SELECT access FROM links WHERE short_link = ?', (short_link,)).fetchone()
    return res[0]


# подсчет количества переходов по конкретной ссылки
def redirect_db(short_link):
    count = cursor.execute('SELECT redirect_count FROM links WHERE short_link = ?', (short_link,)).fetchone()
    res = int(count[0]) + 1
    cursor.execute('UPDATE links SET redirect_count = ? WHERE short_link = ?', (res, short_link))
    connect.commit()
    return res


# проверка на владение конкретной ссылки пользователем
def check_owner_link(login, short_link):
    res = cursor.execute('SELECT user, short_link FROM links WHERE user=? AND short_link=?',
                         (login, short_link)).fetchone()
    if res is not None:
        return True
