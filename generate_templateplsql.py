import os
from html2image import Html2Image
from datetime import datetime
from base64 import b64encode
from urllib.parse import quote_plus

from databasePLSQL import fetch_all_employees
from tts import speak_text

TEMPLATE_DIR = "templates"
OUTPUT_DIR = "output_cards"
HTML_TEMPLATE_PATH = os.path.join(TEMPLATE_DIR, "birthday_template.html")
WELCOME_TEMPLATE_PATH = os.path.join(TEMPLATE_DIR, "welcome_template.html")
GUEST_TEMPLATE_PATH = os.path.join(TEMPLATE_DIR, "special_guest_template.html")
CSS_PATH = os.path.join(TEMPLATE_DIR, "styles.css")
TECH_LOGO_PATH = os.path.join(TEMPLATE_DIR, "logos", "TechProjects.jpg")
CS_LOGO_PATH = os.path.join(TEMPLATE_DIR, "logos", "C&S.jpg")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def image_file_to_base64(path):
    with open(path, "rb") as img_file:
        return f"data:image/jpeg;base64,{b64encode(img_file.read()).decode()}"


def image_blob_to_base64(blob):
    if isinstance(blob, memoryview):
        blob = blob.tobytes()
    return f"data:image/jpeg;base64,{b64encode(blob).decode()}"


def fill_template(html_path, name, image_b64, is_birthday=True, is_guest=False, designation=None):
    with open(html_path, "r", encoding="utf-8") as file:
        html = file.read()

    tech_logo_b64 = image_file_to_base64(TECH_LOGO_PATH)
    cs_logo_b64 = image_file_to_base64(CS_LOGO_PATH)
    background_b64 = image_file_to_base64(os.path.join(TEMPLATE_DIR, "logos", "BGI.jpg"))
    background_src = f"data:image/jpeg;base64,{background_b64.split(',')[-1]}"  # Ensure only base64 data
    html = html.replace("[NAME]", name)
    html = html.replace("[TECHPROJECTS_LOGO]", tech_logo_b64)
    html = html.replace("[CS_LOGO]", cs_logo_b64)
    html = html.replace("[PHOTO_URL]", image_b64)
    html = html.replace("[BACKGROUND_IMAGE]", background_src)
    if not is_birthday and not is_guest and designation:
        html = html.replace("[DESIGNATION]", designation)

    filename = f"rendered_{name.replace(' ', '_')}.html"
    rendered_path = os.path.join(TEMPLATE_DIR, filename)
    with open(rendered_path, "w", encoding="utf-8") as f:
        f.write(html)

    return rendered_path


def render_to_image(html_file_path, name, event_type="birthday"):
    hti = Html2Image(output_path=OUTPUT_DIR)
    filename = f"{event_type}_{name.replace(' ', '_')}.png"
    hti.screenshot(
        html_file=html_file_path,
        css_file=CSS_PATH,
        save_as=filename,
        size=(1000, 600),
    )
    print(f"✅ Saved: {filename}")
    return os.path.join(OUTPUT_DIR, filename)


def generate_card_details(emp, already_greeted_fn, update_log_fn):
    from datetime import datetime, date

    name = emp.get("name")
    dob = emp.get("dob")
    doj = emp.get("doj")
    designation = emp.get("designation")
    is_guest = emp.get("is_special_guest", False)
    image_blob = emp.get("full_image") or emp.get("image")  # for DB or webcam cases

    if not name or not image_blob:
        return None

    image_b64 = image_blob_to_base64(image_blob)
    today = date.today()

    # 🌟 Special Guest
    if is_guest and not already_greeted_fn(f"{name}_guest"):
        update_log_fn(f"{name}_guest")
        return {
            "event": "Special Guest",
            "message": f"🎖️ Welcome special guest {name} to TechProjects!",
            "image_url": image_b64
        }

    # 👋 Joining Anniversary
    if doj:
        try:
            doj_obj = datetime.strptime(doj, "%Y-%m-%d").date()
            if (doj_obj.month, doj_obj.day) == (today.month, today.day) and not already_greeted_fn(f"{name}_join"):
                update_log_fn(f"{name}_join")
                return {
                    "event": "Welcome Aboard",
                    "message": f"👋 Welcome {name}, our new {designation}!",
                    "image_url": image_b64
                }
        except Exception as e:
            print("[ERROR] DOJ check failed:", e)

    # 🎉 Birthday
    if dob:
        try:
            dob_obj = datetime.strptime(dob, "%Y-%m-%d").date()
            if (dob_obj.month, dob_obj.day) == (today.month, today.day) and not already_greeted_fn(f"{name}_bday"):
                update_log_fn(f"{name}_bday")
                return {
                    "event": "Happy Birthday",
                    "message": f"🎉 Happy Birthday {name}! Wishing you joy and success ahead!",
                    "image_url": image_b64
                }
        except Exception as e:
            print("[ERROR] DOB check failed:", e)

    return None


def build_dynamic_url(event_data):
    """
    Takes dictionary with 'event', 'message', and 'image_url' and returns a URL to /template.
    """
    if not event_data:
        return None

    title = quote_plus(event_data["event"])
    message = quote_plus(event_data["message"])
    image = quote_plus(event_data["image_url"])
    return f"/template?title={title}&message={message}&image={image}"


def generate_templates_for_today():
    from face_recognitionplsql import load_log, update_log
    employees = fetch_all_employees()

    if not employees:
        print("⚠️ No employees found.")
        return

    for emp in employees:
        data = generate_card_details(emp, already_greeted_fn=lambda k: load_log().get(k) == str(datetime.now().date()), update_log_fn=update_log)
        if data:
            print("➡️ Launch in browser:", build_dynamic_url(data))
            speak_text(data["message"])


if __name__ == "__main__":
    from databasePLSQL import init_db
    init_db()
    generate_templates_for_today()
