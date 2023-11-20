import logging
from datetime import datetime

from db import get_db_connection


class User:
    db = get_db_connection()

    def __init__(self, username, password, is_master, name, surname, created_account, **kwargs):
        self.username = username
        self.is_master = True if is_master == 1 else False
        self.name = name
        self.surname = surname
        self.password = password
        self.created_account = created_account
        self.average_rating = self.calculate_rating(username)
        self.completed_orders = self.calculate_completed_orders(username)

        if kwargs is not None:
            self.city = kwargs.get("city")

    def insert_new_user(self):
        try:
            self.db.execute(
                "INSERT INTO users (username, password, is_master, name, surname, created_account,"
                " completed_orders, average_rating, city) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (self.username, self.password, int(self.is_master), self.name, self.surname, self.created_account,
                 self.completed_orders, self.average_rating, self.city), )
            self.db.commit()
            # self.db.close()
        except self.db.IntegrityError:
            return {"error": f"USERNAME_ALREADY_EXISTS"}, 400

    @property
    def serialize_account(self):
        return {
            "username": self.username,
            "is_master": int(self.is_master),
            "name": self.name,
            "surname": self.surname,
            "city": self.city
        }

    @property
    def serialize_info(self):
        return {
            "username": self.username,
            "completed_orders": self.completed_orders,
            "average_rating": self.average_rating,
            "created_account": self.created_account
        }

    @staticmethod
    def get_all_users():
        db = get_db_connection()
        users = db.execute("SELECT * FROM users").fetchall()
        user_list = []
        for user in users:
            user_list.append(User(user["username"], user["password"], user["is_master"], user["name"],
                                  user["surname"], user["created_account"], city=user["city"],
                                  completed_orders=user["completed_orders"], average_rating=user["average_rating"]))
        # db.close()
        return user_list

    @staticmethod
    def get_user(username):
        db = get_db_connection()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        # db.close()

        if user is None:
            return {"error": "NO_SUCH_USER"}

        return User(user["username"], user["password"], user["is_master"], user["name"],
                    user["surname"], user["created_account"], city=user["city"],
                    completed_orders=user["completed_orders"], average_rating=user["average_rating"])

    @staticmethod
    def calculate_rating(username):
        db = get_db_connection()
        average_rating = db.execute("SELECT avg(appointments.rating) as average_rating "
                                    "FROM users INNER JOIN appointments "
                                    "ON users.username = appointments.master_user_name WHERE users.username = ?"
                                    "AND appointments.rating IS NOT NULL",
                                    (username,)).fetchone()
        return average_rating["average_rating"]

    @staticmethod
    def calculate_completed_orders(username):
        db = get_db_connection()
        completed_orders = db.execute("SELECT count(appointments.id) as completed_orders "
                                      "FROM appointments "
                                      "WHERE master_user_name = ?"
                                      "AND appointments.status = ?",
                                      (username, 'COMPLETED',)).fetchone()
        return completed_orders["completed_orders"]

    @staticmethod
    def delete_user(username):
        db = get_db_connection()

        db.execute("DELETE FROM users WHERE username = ?", (username,))
        db.execute("DELETE FROM appointments WHERE master_user_name = ? or client_user_name = ?",
                   (username, username,))
        db.commit()
        # db.close()


class Appointment:
    db = get_db_connection()

    def __init__(self, title, master_user_name, client_user_name, start_time, end_time, price, status, **kwargs):
        self.title = title
        self.master_user_name = User.get_user(master_user_name)
        self.client_user_name = User.get_user(client_user_name)
        self.start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        self.end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        self.price = price
        self.status = status

        if kwargs is not None:
            self.description = kwargs.get("description")

        if kwargs is not None:
            self.id = kwargs.get("id")

        if kwargs is not None:
            self.rating = kwargs.get("rating")

    @staticmethod
    def insert_new_appointment(title, master_user_name, client_user_name,
                               start_time, end_time, price, status, description, rating):
        db = get_db_connection()
        db.execute(
            "INSERT INTO appointments (title, master_user_name, client_user_name,"
            "price, start_time, end_time, status, description, rating)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (title, master_user_name, client_user_name, price, start_time, end_time, status, description, rating),
        )
        db.commit()
        # db.close()

    @staticmethod
    def get_all_appointments():
        db = get_db_connection()
        appointments = db.execute("SELECT * FROM appointments").fetchall()
        appointments_list = []
        for appointment in appointments:
            if (appointment["status"] != "COMPLETED") and (datetime.strptime(appointment["start_time"],
                                                                             "%Y-%m-%d %H:%M:%S") < datetime.now()):
                status = "CAN_COMPLETE"
            else:
                status = appointment["status"]

            appointments_list.append(Appointment(appointment["title"], appointment["master_user_name"],
                                                 appointment["client_user_name"], appointment["start_time"],
                                                 appointment["end_time"], appointment["price"],
                                                 status=status, rating=appointment["rating"],
                                                 description=appointment["description"], id=appointment["id"]))
        # db.close()
        return appointments_list

    @staticmethod
    def get_all_appointments_of_user(username):
        db = get_db_connection()
        appointments = db.execute("SELECT * FROM appointments WHERE master_user_name = ? or client_user_name = ?",
                                  (username, username,))

        appointments_list = []
        for appointment in appointments:
            if (appointment["status"] != "COMPLETED") and (datetime.strptime(appointment["start_time"],
                                                                             "%Y-%m-%d %H:%M:%S") < datetime.now()):
                status = "CAN_COMPLETE"
            else:
                status = appointment["status"]

            appointments_list.append(Appointment(appointment["title"], appointment["master_user_name"],
                                                 appointment["client_user_name"], appointment["start_time"],
                                                 appointment["end_time"], appointment["price"],
                                                 status=status, rating=appointment["rating"],
                                                 description=appointment["description"], id=appointment["id"]))
        # db.close()
        return appointments_list

    @staticmethod
    def get_appointment_id(master_user_name, client_user_name, start_time, end_time):
        db = get_db_connection()
        appointment_id = db.execute("SELECT id FROM appointments WHERE client_user_name = ? and master_user_name = ?"
                                    "and start_time = ? and end_time = ?",
                                    (client_user_name, master_user_name, start_time, end_time,)).fetchone()
        # db.close()
        return appointment_id["id"]

    @staticmethod
    def complete_appointment(id):
        db = get_db_connection()
        db.execute("""UPDATE appointments SET status = ? WHERE id = ?""", ("COMPLETED", id,))
        db.commit()
        appointment = db.execute("SELECT * FROM appointments WHERE id =?", (id,)).fetchone()
        return Appointment(appointment["title"], appointment["master_user_name"],
                           appointment["client_user_name"], appointment["start_time"],
                           appointment["end_time"], appointment["price"], appointment["status"],
                           description=appointment["description"], id=id, rating=appointment["rating"])

    @staticmethod
    def rate_appointment(id, rating):
        db = get_db_connection()
        db.execute("""UPDATE appointments SET rating = ? WHERE id = ?""", (rating, id,))
        db.commit()
        appointment = db.execute("SELECT * FROM appointments WHERE id =?", (id,)).fetchone()
        return Appointment(appointment["title"], appointment["master_user_name"],
                           appointment["client_user_name"], appointment["start_time"],
                           appointment["end_time"], appointment["price"], appointment["status"],
                           description=appointment["description"], id=id, rating=appointment["rating"])

    @staticmethod
    def delete_appointment(id):
        db = get_db_connection()
        db.execute("DELETE FROM appointments WHERE id =  ?", (id,))
        db.commit()
        # db.close()

    @property
    def serialize_without_usernames(self):
        return {
            "id": self.get_appointment_id(self.master_user_name.username, self.client_user_name.username,
                                          self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                                          self.end_time.strftime('%Y-%m-%d %H:%M:%S')),
            "title": self.title,
            "start_time": self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            "end_time": self.end_time.strftime('%Y-%m-%d %H:%M:%S'),
            "price": self.price,
            "description": self.description,
            "status": self.status,
            "rating": self.rating
        }

    @property
    def serialize_with_usernames(self):
        return {
            "id": self.get_appointment_id(self.master_user_name.username, self.client_user_name.username,
                                          self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                                          self.end_time.strftime('%Y-%m-%d %H:%M:%S')),
            "title": self.title,
            "master": self.master_user_name.serialize_account,
            "client": self.client_user_name.serialize_account,
            "start_time": self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            "end_time": self.end_time.strftime('%Y-%m-%d %H:%M:%S'),
            "price": self.price,
            "description": self.description,
            "status": self.status,
            "rating": self.rating
        }

    def insert_to_db(self):
        self.db.execute(
            "INSERT INTO appointments (title, master_user_name, client_user_name,"
            "price, start_time, end_time, status, description, rating)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (self.title, self.master_user_name.username, self.client_user_name.username, self.price,
             self.start_time.strftime('%Y-%m-%d %H:%M:%S'), self.end_time.strftime('%Y-%m-%d %H:%M:%S'),
             self.status, self.description, self.rating),
        )
        self.db.commit()

    def validate_status(self):
        if self.start_time < datetime.now():
            self.status = "CAN_COMPLETE"

    def set_rating(self, rating):
        self.rating = rating

    def appointments_intersect(self, new_appointment):
        return (((self.start_time > new_appointment.start_time) and (self.start_time < new_appointment.end_time))
                or ((new_appointment.start_time > self.start_time) and (new_appointment.start_time < self.end_time)))
