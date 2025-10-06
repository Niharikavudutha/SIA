from datetime import datetime

def detect_intent(prompt):
    prompt = prompt.lower()
    if "weather" in prompt:
        return "weather"
    elif "news" in prompt:
        return "news"
    elif "score" in prompt or "cricket" in prompt:
        return "sports"
    elif "distance" in prompt:
        return "location"
    elif "total employees" in prompt or "employee count" in prompt:
        return "employee_count"
    elif "department" in prompt:
        return "department"
    elif "birthdays in" in prompt:
        return "birthdays"
    elif "upcoming birthday" in prompt:
        return "upcoming_birthdays"
    return "unknown"
from database.query_runner import (
    get_employee_by_name,
    get_days_until_birthday,
    get_days_since_joining,
    get_days_until_anniversary
)
 
def handle_employee_question(name, user_query):
    emp_data = get_employee_by_name(name)
    if not emp_data:
        return "I couldn't find your information in the system."
 
    # Unpack data
    emp_name, designation, gender, dob, doj, department, email, phone = emp_data
 
    query = user_query.lower()
 
    if "birthday" in query:
        days_left = get_days_until_birthday(dob)
        return f"Your birthday is in {days_left} day(s) on {dob.strftime('%d %B')}."
   
    elif "data of birth" in query or "dob" in query:
        return f"Your date of birth is {dob.strftime('%d %B %Y')}."
 
    elif "how long" in query or "been working" in query or "how many days have i been here" in query or "experiance in this company" in query:
        days, years, months = get_days_since_joining(doj)
        return f"You've been working here for {years} year(s), {months} month(s) — a total of {days} days."
 
    elif "anniversary" in query and "when" in query:
        return f"Your work anniversary is on {doj.strftime('%d %B')}."
 
    elif "how many days" in query and "anniversary" in query:
        days = get_days_until_anniversary(doj)
        return f"Your next work anniversary is in {days} day(s)."
 
    elif "joining" in query or "join" in query:
        return f"Your joining date is {doj.strftime('%d %B %Y')}."
   
    elif "designation" in query or "role" in query:
        return f"Your designation is {designation}."
 
    elif "email" in query:
        return f"Your official email is {email}."
 
    elif "contact" in query or "phone" in query:
        return f"Your contact number is {phone}."
 
    elif "department" in query:
        return f"You are in the {department} department."
 
    elif "about" in query or "details" in query or "info" in query or " my information" in query:
        return (f"Here is your profile:\n"
                f"Name: {emp_name}\n"
                f"Designation: {designation}\n"
                f"Department: {department}\n"
                f"Date of Birth: {dob.strftime('%d %B %Y')}\n"
                f"Gender: {gender}\n"
                f"Joining Date: {doj.strftime('%d %B %Y')}\n"
                f"Email: {email}\n"
                f"Contact: {phone}")
 
    else:
        return "I'm not sure how to help with that employee-related query."
