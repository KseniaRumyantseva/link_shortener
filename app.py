from flask import Flask, request, redirect, jsonify, make_response
from flask_jwt_extended import create_access_token, JWTManager, get_jwt_identity, jwt_required
import sqlite3, uuid, hashlib, random
from werkzeug.security import generate_password_hash, check_password_hash

import config
import functions

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret"
jwt = JWTManager(app)


@app.route("/")
def hello_world():
    return "Hello World!"


@app.route("/reg", methods=['POST'])
def register():
    login = str(request.json.get("login", None))
    password = str(request.json.get("password", None))
    password_hash = generate_password_hash(password)
    if functions.database_register(login, password_hash):
        return make_response('Пользователь зарегистрирован')
    else:
        return make_response('Не удалось зарегистрировать пользователя')


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


@app.route("/list_links", methods=['POST'])
@jwt_required()
def list_users_links():
    login = str(get_jwt_identity())
    if functions.get_list_user_links(login) != '':
        return functions.get_list_user_links(login)
    else:
        return make_response("У вас пока нет добавленных ссылок")


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


@app.route("/update_link", methods=['POST'])
@jwt_required()
def update():
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


@app.route("/<short_link>")
def redirect(short_link):
    return str(f'Количество переходов по этой ссылке - {functions.redirect_db(short_link)}')


if __name__ == '__main__':
    app.run()


# user7 - 111
# user8 - 888