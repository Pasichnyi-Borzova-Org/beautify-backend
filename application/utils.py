import re

from flask import Response


def validate_password(password):
    if len(password) < 8:
        return False

    if not re.search(r'[A-Z]', password):
        return False

    if not re.search(r'[a-z]', password):
        return False

    if not re.search(r'\d', password):
        return False

    if not re.search(r'[!@#$%^&*()_,.?":{}|<>]', password):
        return False

    return True


def update_user_table(db, field_name, field_value, username):
    try:
        db.execute(
            f"UPDATE users SET {field_name}=? WHERE username = ?",
            (field_value, username,),
        )
        db.commit()
    except db.IntegrityError:
        return {"error": "Update error occurred"}, 400


def update_master_table(db, field_name, field_value, username):
    try:
        db.execute(
            f"UPDATE appointments SET {field_name}=? WHERE master_user_name = ?",
            (field_value, username,),
        )
        db.commit()
    except db.IntegrityError:
        return {"error": "Update error occurred"}, 400