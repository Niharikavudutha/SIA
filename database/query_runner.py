# # # from .db_connection import get_connection

# # # def fetch_employees():
# # #     conn = get_connection()
# # #     cur = conn.cursor()
# # #     cur.execute("SELECT name, role, department FROM employees")
# # #     rows = cur.fetchall()
# # #     cur.close()
# # #     conn.close()
# # #     return rows

# # # def fetch_teams():
# # #     conn = get_connection()
# # #     cur = conn.cursor()
# # #     cur.execute("SELECT name, lead, members FROM teams")
# # #     rows = cur.fetchall()
# # #     cur.close()
# # #     conn.close()
# # #     return rows

# # # def fetch_policies(policy_type):
# # #     conn = get_connection()
# # #     cur = conn.cursor()
# # #     cur.execute("SELECT title, content FROM company_policies WHERE type = %s", (policy_type,))
# # #     rows = cur.fetchall()
# # #     cur.close()
# # #     conn.close()
# # #     return rows

# # from .db_connection import get_connection
# # import datetime

# # def get_employees_by_department(dept_name):
# #     try:
# #         conn = get_connection()
# #         cur = conn.cursor()
# #         cur.execute("""
# #             SELECT name FROM employees 
# #             WHERE LOWER(department) = LOWER(%s)
# #         """, (dept_name,))
# #         rows = cur.fetchall()
# #         cur.close()
# #         conn.close()
# #         return [r[0] for r in rows]
# #     except Exception as e:
# #         print(f"❌ DB Error (department): {e}")
# #         return []

# # def get_employees_by_birth_month(month_name):
# #     try:
# #         # month_num = list(calendar.month_name).index(month_name.capitalize())
# #         conn = get_connection()
# #         cur = conn.cursor()
# #         cur.execute("""
# #             SELECT name FROM employees 
# #             WHERE TO_CHAR(DOB, 'Month') ILIKE %s
# #         """, (month_name + '%',))
# #         rows = cur.fetchall()
# #         cur.close()
# #         conn.close()
# #         return [r[0] for r in rows]
# #     except Exception as e:
# #         print(f"❌ DB Error (birth month): {e}")
# #         return []

# # def get_total_employees():
# #     try:
# #         conn = get_connection()
# #         cur = conn.cursor()
# #         cur.execute("SELECT COUNT(*) FROM employees")
# #         count = cur.fetchone()[0]
# #         cur.close()
# #         conn.close()
# #         return count
# #     except Exception as e:
# #         print(f"❌ DB Error (total): {e}")
# #         return 0

# from .db_connection import get_connection
# import calendar
# import datetime

# def get_employees_by_department(department):
#     try:
#         conn = get_connection()
#         cur = conn.cursor()
#         cur.execute("SELECT name FROM employees WHERE LOWER(department) = LOWER(%s)", (department,))
#         rows = cur.fetchall()
#         cur.close()
#         conn.close()
#         return [row[0] for row in rows]
#     except Exception as e:
#         print("❌ DB Error (department):", e)
#         return []

# def get_employees_by_birth_month(month_name):
#     try:
#         month_num = list(calendar.month_name).index(month_name.capitalize())
#         conn = get_connection()
#         cur = conn.cursor()
#         query = "SELECT name FROM employees WHERE EXTRACT(MONTH FROM dob) = %s"
#         cur.execute(query, (month_num,))
#         rows = cur.fetchall()
#         cur.close()
#         conn.close()
#         return [row[0] for row in rows]
#     except ValueError:
#         return []
#     except Exception as e:
#         print("❌ DB Error (birth_month):", e)
#         return []

# def get_upcoming_birthdays(days_ahead=7):
#     try:
#         conn = get_connection()
#         cur = conn.cursor()
#         today = datetime.date.today()
#         end_date = today + datetime.timedelta(days=days_ahead)

#         query = """
#         SELECT name, dob FROM employees
#         WHERE TO_CHAR(dob, 'MM-DD') BETWEEN TO_CHAR(%s, 'MM-DD') AND TO_CHAR(%s, 'MM-DD')
#         """
#         cur.execute(query, (today, end_date))
#         rows = cur.fetchall()
#         cur.close()
#         conn.close()
#         return [f"{name} - {dob.strftime('%d %b')}" for name, dob in rows]
#     except Exception as e:
#         print("❌ DB Error (upcoming_birthdays):", e)
#         return []

# def get_total_employees():
#     try:
#         conn = get_connection()
#         cur = conn.cursor()
#         cur.execute("SELECT COUNT(*) FROM employees")
#         count = cur.fetchone()[0]
#         cur.close()
#         conn.close()
#         return count
#     except Exception as e:
#         print("❌ DB Error (count):", e)
#         return 0

from .db_connection import get_connection
import calendar
import datetime
 
def get_employee_by_name(name):
    """Fetch full info of a specific employee by name (case insensitive)."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT name, designation, gender, dob, doj, department, official_email, contact_number
            FROM employees
            WHERE LOWER(name) = LOWER(%s)
        """, (name,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row
    except Exception as e:
        print("❌ DB Error (employee_by_name):", e)
        return None
 
 
def get_days_until_birthday(dob):
    """Calculate days until next birthday."""
    try:
        today = datetime.date.today()
        this_year_birthday = dob.replace(year=today.year)
 
        # If birthday already passed this year, get next year's birthday
        if this_year_birthday < today:
            this_year_birthday = this_year_birthday.replace(year=today.year + 1)
 
        days_left = (this_year_birthday - today).days
        return days_left
    except Exception as e:
        print("❌ DOB Parse Error:", e)
        return None
 
def get_days_since_joining(doj):
    """Calculate how long (in days and years/months) the employee has been working."""
    try:
        today = datetime.date.today()
        delta = today - doj
        years = delta.days // 365
        months = (delta.days % 365) // 30
        return delta.days, years, months
    except Exception as e:
        print("❌ DOJ Parse Error:", e)
        return None, None, None
 
def get_days_until_anniversary(doj):
    """Calculate how many days until the employee's next work anniversary."""
    try:
        today = datetime.date.today()
        this_year_anniversary = doj.replace(year=today.year)
        if this_year_anniversary < today:
            this_year_anniversary = this_year_anniversary.replace(year=today.year + 1)
        return (this_year_anniversary - today).days
    except Exception as e:
        print("❌ Anniversary Parse Error:", e)
        return None
 
def get_employees_by_department(department):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT name FROM employees WHERE LOWER(department) = LOWER(%s)", (department,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [row[0] for row in rows]
    except Exception as e:
        print("❌ DB Error (department):", e)
        return []
 
def get_employees_by_birth_month(month_name):
    try:
        month_num = list(calendar.month_name).index(month_name.capitalize())
        conn = get_connection()
        cur = conn.cursor()
        query = "SELECT name FROM employees WHERE EXTRACT(MONTH FROM dob) = %s"
        cur.execute(query, (month_num,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [row[0] for row in rows]
    except ValueError:
        return []
    except Exception as e:
        print("❌ DB Error (birth_month):", e)
        return []
 
def get_upcoming_birthdays(days_ahead=7):
    try:
        conn = get_connection()
        cur = conn.cursor()
        today = datetime.date.today()
        end_date = today + datetime.timedelta(days=days_ahead)
 
        query = """
        SELECT name, dob FROM employees
        WHERE TO_CHAR(dob, 'MM-DD') BETWEEN TO_CHAR(%s, 'MM-DD') AND TO_CHAR(%s, 'MM-DD')
        """
        cur.execute(query, (today, end_date))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [f"{name} - {dob.strftime('%d %b')}" for name, dob in rows]
    except Exception as e:
        print("❌ DB Error (upcoming_birthdays):", e)
        return []
 
def get_total_employees():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM employees")
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return count
    except Exception as e:
        print("❌ DB Error (count):", e)
        return 0