
import sys

from database import db

ALLOWED_ROLES = {"viewer", "editor", "admin"}


def set_user_role(email, role):
    if db is None:
        print("Database is not configured.")
        return

    if role not in ALLOWED_ROLES:
        print("Invalid role. Choose viewer, editor, or admin.")
        return

    email = email.strip().lower()

    result = db.users.update_one(
        {"email": email},
        {"$set": {"role": role}}
    )

    if result.matched_count == 0:
        print("User not found. Register the user first.")
    else:
        print(f"Role updated successfully: {email} -> {role}")
        print("Log in again to receive a token with the new role.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python set_user_role.py <email> <role>")
    else:
        set_user_role(sys.argv[1], sys.argv[2])