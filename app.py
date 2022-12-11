from flask import Flask, request, redirect, jsonify, make_response
from flask_jwt_extended import create_access_token, JWTManager, get_jwt_identity, jwt_required
import sqlite3, uuid, hashlib, random
from werkzeug.security import generate_password_hash, check_password_hash

import config
import functions

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret"
jwt = JWTManager(app)


# регистрация пользователя
@app.route("/reg", methods=['POST'])
def register():
    login = str(request.json.get("login", None))
    password = str(request.json.get("password", None))
    password_hash = generate_password_hash(password)
    if functions.database_register(login, password_hash):
        return make_response('Пользователь зарегистрирован')
    else:
        return make_response('Не удалось зарегистрировать пользователя')


# авторизация пользователя
@app.route("/auth", methods=['POST'])
def authorization():
    login = str(request.json.get("login", None))
    password = str(request.json.get("password", None))
    unhash_password = check_password_hash(functions.password_from_db(login), password)
    if functions.check_user_is_correct(login) and unhash_password == True:
        token = create_access_token(identity=login)
        return make_response(f"Пользователь авторизован, {token}")
    else:
        return make_response('Неверный логин или пароль')


# добавление сокращенной ссылки
@app.route("/add_link", methods=['POST'])
@jwt_required()
def add_link():
    login = str(get_jwt_identity())
    full_link = str(request.json.get("full_link", None))
    short_link = str(request.json.get("short_link", None))
    access = 1
    if full_link != '':
        if short_link == '':
            user_link = hashlib.md5(full_link.encode()).hexdigest()[:random.randint(8, 12)]
            functions.add_new_link(full_link, user_link, access, login)
            return make_response("Ссылка успешно сохранена")
        else:
            functions.add_new_link(full_link, short_link, access, login)
            return make_response("Ссылка успешно сохранена")
    else:
        return make_response("Введите ссылку")


# просмотр списка ссылок, которые добавил пользователь
@app.route("/list_links", methods=['GET'])
@jwt_required()
def list_users_links():
    login = str(get_jwt_identity())
    if functions.get_list_user_links(login) != '':
        return functions.get_list_user_links(login)
    else:
        return make_response("У вас пока нет добавленных ссылок")


# удаление выбранной ссылки
@app.route("/del_link", methods=['POST'])
@jwt_required()
def delete():
    login = str(get_jwt_identity())
    short_link = str(request.json.get("short_link", None))
    if short_link != '':
        functions.del_link_from_db(login, short_link)
        return make_response("Ссылка успешно удалена")
    else:
        return make_response("Не удалось удалить ссылку")


# обновление имени выбранной ссылки
@app.route("/update_link", methods=['POST'])
@jwt_required()
def update_link():
    login = str(get_jwt_identity())
    old_link = str(request.json.get("old_link", None))
    new_link = str(request.json.get("new_link", None))
    if new_link != '':
        functions.update_link_from_db(login, new_link, old_link)
        return make_response("Ссылка успешно обновлена")
    elif new_link == '':
        link = hashlib.md5(old_link.encode()).hexdigest()[:random.randint(8, 12)]
        functions.update_link_from_db(login, link, old_link)
        return make_response("Ссылка успешно обновлена")
    else:
        return make_response("Не удалось обновить ссылку")


# изменение уровня доступа выбранной ссылки
@app.route("/update_access", methods=['POST'])
@jwt_required()
def update_access():
    login = str(get_jwt_identity())
    link = str(request.json.get("link", None))
    new_access = str(request.json.get("new_access", None))
    if link != '' and (new_access == '1' or new_access == '2' or new_access == '3'):
        functions.update_access_from_db(login, link, new_access)
        return make_response("Уровень доступа успешно изменен")
    else:
        return make_response("Не удалось изменить уровень доступа")


# подсчет переходов по конкретной ссылки
@app.route("/<short_link>")
def redirect(short_link):
    if functions.check_access(short_link) == 1:
        return str(f'Количество переходов по этой ссылке - {functions.redirect_db(short_link)}')
    elif functions.check_access(short_link) == 2:
        return check_3(short_link)
    elif functions.check_access(short_link) == 3:
        return check_2(short_link)
    else:
        return make_response("Ошибка перехода по ссылке")


# проверка условий для подсчета переходов по ссылки, если уровень доступа - 'private'
@jwt_required()
def check_3(short_link):
    login = str(get_jwt_identity())
    if functions.check_owner_link(login, short_link):
        return str(f'Количество переходов по этой ссылке - {functions.redirect_db(short_link)}')
    else:
        return make_response("Вы не являетесь владельцем этой ссылки, поэтому не можете перейти по ней")


# проверка условий для подсчета переходов по ссылки, если уровень доступа - 'protected'
@jwt_required()
def check_2(short_link):
    login = str(get_jwt_identity())
    if functions.check_user_is_correct(login) is not None:
        return str(f'Количество переходов по этой ссылке - {functions.redirect_db(short_link)}')
    else:
        return make_response("Вы не авторизовались")


if __name__ == '__main__':
    app.run()

# user7 - 111
# user8 - 888
