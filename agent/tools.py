from database.query_runner import fetch_employees, fetch_teams, fetch_policies
import random

def get_employee_info():
    return fetch_employees()

def get_team_info():
    return fetch_teams()

def get_policies_by_type(p_type):
    return fetch_policies(p_type)

# def tell_joke():
#     jokes = [
#         "Why did the developer go broke? Because he used up all his cache!",
#         "Why do programmers prefer dark mode? Because the light attracts bugs!",
#         "I told my computer I needed a break, and it said 'No problem, I’ll go to sleep.'"
#     ]
#     return random.choice(jokes)
from config.settings import GEMINI_API_KEY
import google.generativeai as genai

# Configure Gemini

joke_model = genai.GenerativeModel("models/gemini-1.5-flash")

def tell_joke(prompt_hint="Tell me a candid joke"):
    try:
        joke_prompt = f"""You are a very funny AI. Generate a super candid, witty, and laugh-out-loud joke. 
Be spontaneous, relevant, and fun. Prompt: {prompt_hint}"""
        response = joke_model.generate_content(joke_prompt)
        return response.text.strip()
    except Exception as e:
        return f"Sorry, I couldn't fetch a joke right now. ({e})"