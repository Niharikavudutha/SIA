def is_admin(user_role):
    return user_role == "admin"

def is_employee(user_role):
    return user_role in ["employee", "admin"]

