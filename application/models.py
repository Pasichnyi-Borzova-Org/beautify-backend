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

        if kwargs is not None:
            self.city = kwargs.get("city")

        if kwargs is not None:
            self.completed_orders = kwargs.get("completed_orders")

        if kwargs is not None:
            self.average_rating = kwargs.get("average_rating")

    def insert_new_user(self):
        try:
            self.db.execute(
                "INSERT INTO users (username, password, is_master, name, surname, created_account,"
                " completed_orders, average_rating, city) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (self.username, self.password, int(self.is_master), self.name, self.surname, self.created_account,
                 self.completed_orders, self.average_rating, self.city), )
            self.db.commit()
            self.db.close()
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
        db.close()
        return user_list

    @staticmethod
    def get_user(username):
        db = get_db_connection()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        db.close()
        return User(user["username"], user["password"], user["is_master"], user["name"],
                    user["surname"], user["created_account"], city=user["city"],
                    completed_orders=user["completed_orders"], average_rating=user["average_rating"])


class Appointment:
    db = get_db_connection()

    def __init__(self, title, master_user_name, client_user_name, start_time, end_time, price, **kwargs):
        self.title = title
        self.master_user_name = User(master_user_name)
        self.client_user_name = User(client_user_name)
        self.start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        self.end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        self.price = price
        if kwargs is not None:
            self.description = kwargs.get("description")

        if kwargs is not None:
            self.id = kwargs.get("id")

    def appointments_intersect(self, new_appointment):
        return (((self.start_time > new_appointment.start_time) and (self.start_time < new_appointment.end_time))
                or ((new_appointment.start_time > self.start_time) and (new_appointment.start_time < self.end_time)))
