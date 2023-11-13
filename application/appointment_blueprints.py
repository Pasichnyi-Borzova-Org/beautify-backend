import logging
from flask import Blueprint, jsonify, request

from db import get_db_connection
from models import Appointment, User
from utils import update_master_table

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

blueprint = Blueprint("appointments", __name__, url_prefix="/appointments")


@blueprint.route("/", methods=["POST"])
def create_appointment():
    data = request.get_json(force=True)
    title = data.get("title")
    master_user_name = data.get("master_user_name")
    client_user_name = data.get("client_user_name")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    price = data.get("price")
    description = data.get("description") or None

    if not all([title, master_user_name, client_user_name, start_time, end_time, price]):
        logging.debug(all([title, master_user_name, client_user_name, start_time, end_time, price]))
        return {"error": "REQUIRED_FIELDS_ARE_MISSING"}, 400

    db = get_db_connection()
    try:
        cursor = db.execute(
            "INSERT INTO appointments (title, master_user_name, client_user_name, price, start_time, end_time, description)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, master_user_name, client_user_name, price, start_time, end_time, description),
        )
        db.commit()
    except db.IntegrityError:
        return {"error": f"Error occurred"}, 400

    return jsonify({"id": cursor.lastrowid}), 201


# tryCreateAppointment(appointment: DataAppointment): ?
@blueprint.route("/create", methods=["POST"])
def try_create_appointment():
    logging.info(request.get_json(force=True))
    data = request.get_json(force=True)
    title = data.get("title")
    master_user_name = data.get("master").get("username")
    client_user_name = data.get("client").get("username")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    price = data.get("price")
    description = data.get("description") or None

    if not all([title, master_user_name, client_user_name, start_time, end_time, price]):
        return {"error": "REQUIRED_FIELDS_ARE_MISSING"}, 400

    new_appointment = Appointment(title, master_user_name, client_user_name,
                                  start_time, end_time, price, description=description)

    db = get_db_connection()
    appointments = db.execute("SELECT * FROM appointments WHERE master_user_name = ?", (master_user_name,))

    for appointment in appointments:
        if Appointment(appointment["title"], appointment["master_user_name"],
                       appointment["client_user_name"], appointment["start_time"],
                       appointment["end_time"], appointment["price"],
                       description=appointment["description"], id=appointment["id"]).appointments_intersect(
            new_appointment
        ):
            return {"error": "TIME_IS_OCCUPIED"}, 400

    try:
        db.execute(
            "INSERT INTO appointments (title, master_user_name, client_user_name,"
            "price, start_time, end_time, description)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, master_user_name, client_user_name, price, start_time, end_time, description),
        )
        db.commit()
    except db.IntegrityError:
        return {"error": "DB_INSERT_FAILED"}, 500

    return jsonify({
        "id": Appointment.get_appointment_id(master_user_name, client_user_name, start_time, end_time),
        "title": title,
        "start_time": start_time,
        "end_time": end_time,
        "price": price,
        "description": description,
        "master": User.get_user(master_user_name).serialize_account,
        "client": User.get_user(client_user_name).serialize_account,
    }), 201


@blueprint.route("/master/<string:username>/", methods=["PUT"])
def update_master(username):
    data = request.get_json(force=True)
    username = data.get("username") or username
    title = data.get("title")
    client_user_name = data.get("client_user_name")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    price = data.get("price")
    db = get_db_connection()

    if client_user_name:
        update_master_table(db, "client_user_name", client_user_name, username)

    if title:
        update_master_table(db, "title", title, username)

    if start_time:
        update_master_table(db, "start_time", start_time, username)

    if end_time:
        update_master_table(db, "end_time", end_time, username)

    if price:
        logging.debug(price)
        update_master_table(db, "price", price, username)

    return jsonify({"Updated": username}), 200


@blueprint.route("/", methods=["GET"])
def list_appointments():
    db = get_db_connection()

    cursor = db.execute("SELECT * FROM appointments")
    appointments = cursor.fetchall()

    appointment_list = []
    for appointment in appointments:
        cursor = db.execute("SELECT * FROM users WHERE username = ?", (appointment["master_user_name"],))
        master = cursor.fetchone()
        cursor = db.execute("SELECT * FROM users WHERE username = ?", (appointment["client_user_name"],))
        client = cursor.fetchone()
        appointment_list.append(
            {
                "id": appointment["id"],
                "title": appointment["title"],
                "start_time": appointment["start_time"],
                "end_time": appointment["end_time"],
                "price": appointment["price"],
                "description": appointment["description"],
                "master": {
                    "username": master["username"],
                    "is_master": master["is_master"],
                    "name": master["name"],
                    "surname": master["surname"],
                    "city": master["city"]
                },
                "client": {
                    "username": client["username"],
                    "is_master": client["is_master"],
                    "name": client["name"],
                    "surname": client["surname"],
                    "city": client["city"]
                }
            }
        )

    return jsonify(appointment_list)


# getAppointmentsOfUser(userName: String): List<DataAppointment>
@blueprint.route("/<string:username>", methods=["GET"])
def list_appointments_of_user(username):
    db = get_db_connection()

    cursor = db.execute("SELECT * FROM appointments WHERE client_user_name = ? or master_user_name = ?",
                        (username, username,))
    appointments = cursor.fetchall()

    appointment_list = []
    for appointment in appointments:
        cursor = db.execute("SELECT * FROM users WHERE username = ?", (appointment["master_user_name"],))
        master = cursor.fetchone()
        cursor = db.execute("SELECT * FROM users WHERE username = ?", (appointment["client_user_name"],))
        client = cursor.fetchone()
        appointment_list.append(
            {
                "id": appointment["id"],
                "title": appointment["title"],
                "start_time": appointment["start_time"],
                "end_time": appointment["end_time"],
                "price": appointment["price"],
                "description": appointment["description"],
                "master": {
                    "username": master["username"],
                    "is_master": master["is_master"],
                    "name": master["name"],
                    "surname": master["surname"],
                    "city": master["city"]
                },
                "client": {
                    "username": client["username"],
                    "is_master": client["is_master"],
                    "name": client["name"],
                    "surname": client["surname"],
                    "city": client["city"]
                }
            }
        )

    return jsonify(appointment_list)


@blueprint.route("/delete/<int:id>", methods=["DELETE"])
def delete_appointment_for_master(id):
    db = get_db_connection()
    logging.info(id)
    db.execute("DELETE FROM appointments WHERE id =  ?", (id,))
    db.commit()
    db.close()

    return f"APPOINTMENT_DELETED", 204
