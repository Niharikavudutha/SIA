import re
import datetime
from config.settings import GEMINI_API_KEY
import google.generativeai as genai
from retriever.doc_retriever import search_similar_documents
from database.query_runner import (
    get_employees_by_department,
    get_employees_by_birth_month,
    get_total_employees,
    get_upcoming_birthdays,
)

# ✅ Import real-time intent and APIs
from modules import weather, news, sports, location
from intent_handler import detect_intent

# ✅ Configure Gemini model
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash")

# ✅ Database query handler
def match_and_run_database_query(prompt):
    prompt_lower = prompt.lower()

    # ✅ Department
    match = re.search(r"(employees|team|members).* (in|under) (\w+) department", prompt_lower)
    if match:
        dept = match.group(3)
        members = get_employees_by_department(dept)
        if members:
            return f"The employees in the {dept.capitalize()} department are:\n- " + "\n- ".join(members)
        return f"No employees found in {dept.capitalize()} department."

    # ✅ Birthdays in specific month
    match = re.search(r"(birthdays|birthday).* in (\w+)", prompt_lower)
    if match:
        month = match.group(2)
        people = get_employees_by_birth_month(month)
        if people:
            return f"🎂 Employees with birthdays in {month.capitalize()}:\n- " + "\n- ".join(people)
        return f"No birthdays found in {month.capitalize()}."

    # ✅ Birthdays this month
    if "birthday" in prompt_lower and "this month" in prompt_lower:
        current_month = datetime.datetime.now().strftime("%B")
        people = get_employees_by_birth_month(current_month)
        if people:
            return f"🎉 Employees with birthdays in {current_month}:\n- " + "\n- ".join(people)
        return f"No employee birthdays in {current_month}."

    # ✅ Upcoming birthdays
    if "upcoming birthday" in prompt_lower or "next birthdays" in prompt_lower:
        upcoming = get_upcoming_birthdays()
        if upcoming:
            return f"🎈 Upcoming birthdays in the next 7 days:\n- " + "\n- ".join(upcoming)
        return "No upcoming birthdays in the next week."

    # ✅ Total employees
    if re.search(r"how many employees|total employees|employee count", prompt_lower):
        count = get_total_employees()
        return f"There are currently {count} employees in the company."

    return None

# ✅ Final master function
def chat_with_agent(prompt):
    prompt_lower = prompt.lower()
    intent = detect_intent(prompt_lower)

    # 🎯 Real-time API intent handlers
    if intent == "weather":
        city = re.sub(r"(weather|temperature|climate|in)", "", prompt_lower).strip()
        return weather.get_weather(city or "your city")

    elif intent == "news":
        topic = re.sub(r"(news|headlines|latest)", "", prompt_lower).strip()
        return news.get_news(topic or "technology")

    elif intent == "sports":
        return sports.get_live_cricket_score()

    elif intent == "location":
        match = re.search(r"from (.+?) to (.+)", prompt_lower)
        if match:
            start = match.group(1).strip()
            end = match.group(2).strip()
            return location.get_distance_info(start, end)
        else:
            return "Please provide the location query like: 'distance from Hyderabad to Delhi'."

    elif intent == "exit":
        return "👋 Thank you! Have a great day."

    # 1️⃣ RAG document retrieval
    docs = search_similar_documents(prompt)
    context = "\n".join(docs) if docs else ""

    if context:
        relevance_prompt = f"""
You're an assistant. Check if these docs help answer the question.

Question: "{prompt}"

Documents:
\"\"\"{context}\"\"\"

Is the context relevant? Reply "yes" or "no".
"""
        response = model.generate_content(relevance_prompt)
        if "yes" in response.text.lower():
            answer_prompt = f"""
You are a smart assistant at TechProjects. Use the following documents to answer the user's question.

Documents:
\"\"\"{context}\"\"\"

Question: {prompt}
"""
            final = model.generate_content(answer_prompt)
            return final.text.strip()

    # 2️⃣ Check database
    db_answer = match_and_run_database_query(prompt)
    if db_answer:
        return db_answer

    # 3️⃣ Fallback Gemini LLM
    generic = model.generate_content(f"Answer clearly and helpfully:\n\n{prompt}")
    return generic.text.strip()
print("Gemini key being used:", GEMINI_API_KEY)