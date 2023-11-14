import logging
from datetime import datetime
from flask import Blueprint, jsonify, request, make_response
from werkzeug.security import generate_password_hash, check_password_hash

from db import get_db_connection
from models import User
from utils import validate_password, update_user_table

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

blueprint = Blueprint("users", __name__, url_prefix="/users")


# registerUser(registerData: RegisterData):
@blueprint.route("/", methods=["POST"])
def create_user():
    data = request.get_json(force=True)
    username = data.get("username")
    password = data.get("password")
    is_master = data.get("is_master")
    name = data.get("name")
    surname = data.get("surname")
    created_account = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    city = data.get("city") or None
    completed_orders = data.get("completed_orders") or None
    average_rating = data.get("average_rating") or None

    if validate_password(password):

        encrypted_password = generate_password_hash(password)

        if not all([username, surname, str(is_master), password, name]):
            return {"error": "REQUIRED_FIELDS_ARE_MISSING"}, 400

        new_user = User(username, encrypted_password, is_master, name, surname, created_account,
                        completed_orders=completed_orders, average_rating=average_rating, city=city)
        new_user.insert_new_user()

        return jsonify({"data": new_user.serialize_account}), 201
    else:
        return {"error": "WEAK_PASSWORD"}


@blueprint.route("/<string:username>/", methods=["PUT"])
def update_user(username):
    data = request.get_json(force=True)
    password = data.get("password")
    is_master = data.get("is_master")
    name = data.get("name")
    surname = data.get("surname")
    city = data.get("city") or None
    completed_orders = data.get("completed_orders") or None
    average_rating = data.get("average_rating") or None
    db = get_db_connection()

    if username:
        update_user_table(db, "username", username, username)

    if password:
        update_user_table(db, "password", password, username)

    if is_master:
        update_user_table(db, "is_master", is_master, username)

    if name:
        update_user_table(db, "name", name, username)

    if surname:
        update_user_table(db, "surname", surname, username)

    if city:
        update_user_table(db, "city", city, username)

    if completed_orders:
        update_user_table(db, "completed_orders", completed_orders, username)

    if average_rating:
        update_user_table(db, "average_rating", average_rating, username)

    return jsonify({"Updated": username}), 200


# getAllUsers(): List<UserAccount>
@blueprint.route("/", methods=["GET"])
def list_users():
    users = User.get_all_users()
    return make_response(jsonify([user.serialize_account for user in users]), 200)


# getAccountByUsername(username: String): UserAccount
@blueprint.route("/<string:username>/account", methods=["GET"])
def get_user_account_info(username):
    user = User.get_user(username)
    return jsonify(user.serialize_account)


# getUserInfo(username: String): DataUserInfo
@blueprint.route("/<string:username>/info", methods=["GET"])
def get_user_info(username):
    user = User.get_user(username)
    return jsonify(user.serialize_info)


# loginUser(username: String, password: String): Result<UserAccount>
@blueprint.route("/login", methods=["GET", "POST"])
def login_user():
    data = request.get_json(force=True)
    username = data.get("username")
    password_from_request = data.get("password")
    user = User.get_user(username)

    if isinstance(user, User) and check_password_hash(user.password, password_from_request):
        return make_response(jsonify(user.serialize_account), 200)

    return make_response(jsonify({"error": "NO_SUCH_USER"}), 404)


@blueprint.route("/delete/<string:username>", methods=["DELETE"])
def delete_user(username):
    User.delete_user(username)
    return f"User {username} deleted", 204
