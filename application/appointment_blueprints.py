import logging
from flask import Blueprint, jsonify, request, make_response

from db import get_db_connection
from models import Appointment
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
                                  start_time, end_time, price, is_finished=0, description=description)

    db = get_db_connection()
    appointments = db.execute("SELECT * FROM appointments WHERE master_user_name = ?", (master_user_name,))

    for appointment in appointments:
        if (Appointment(appointment["title"], appointment["master_user_name"],
                        appointment["client_user_name"], appointment["start_time"],
                        appointment["end_time"], appointment["price"], appointment["is_finished"],
                        description=appointment["description"], id=appointment["id"])
                .appointments_intersect(new_appointment)):

            return {"error": "TIME_IS_OCCUPIED"}, 400

    try:
        Appointment.insert_new_appointment(title, master_user_name, client_user_name,
                                           start_time, end_time, price, description, is_finished=0)
    except db.IntegrityError:
        return {"error": "DB_INSERT_FAILED"}, 500

    return jsonify(new_appointment.serialize_with_usernames), 201


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
        update_master_table(db, "price", price, username)

    return jsonify({"Updated": username}), 200


@blueprint.route("/", methods=["GET"])
def list_appointments():
    appointments = Appointment.get_all_appointments()
    return make_response(jsonify([appointment.serialize_with_usernames for appointment in appointments]), 200)


# getAppointmentsOfUser(userName: String): List<DataAppointment>
@blueprint.route("/<string:username>", methods=["GET"])
def list_appointments_of_user(username):
    appointments = Appointment.get_all_appointments_of_user(username)
    return make_response(jsonify([appointment.serialize_with_usernames for appointment in appointments]), 200)


@blueprint.route("/delete/<int:id>", methods=["DELETE"])
def delete_appointment(id):
    Appointment.delete_appointment(id)
    return make_response("APPOINTMENT_DELETED", 200)
