import streamlit as st
from datetime import datetime, date
import io, os, base64, uuid, time, tempfile
from PIL import Image
import numpy as np
import cv2
import speech_recognition as sr
from gtts import gTTS
from databasePLSQL import (
    init_db, fetch_all_employees, get_employee_by_name, remove_employee,
    get_all_employee_names, update_employee_name, update_employee_dob
)
from databasePLSQL import update_employee_all_fields, update_employee_columns
from face_recognitionplsql import load_face_app, cosine_similarity, run_recognition
from register_faceplsql import register_user
from scraper import get_todays_observances
from agent.bp2 import chat_with_agent

# Initialize DB
init_db()

# --- Page Config ---
st.set_page_config(page_title="Smart Greet Panel", layout="wide")
st.title("🎉 Welcome to Smart Greet Panel")

# --- Sidebar Navigation ---
mode = st.sidebar.selectbox("Choose Mode", [
    "AI Chat + Face Recognition",
    "Register New Face",
    "View Today's Observances",
    "Show Today's Birthdays",
    "Show All Users",
    "Show User Details",
    "Edit User Details",
    "Remove User"
])

# ========== PAGE 1: AI Chat + Face Recognition ==========
if mode == "AI Chat + Face Recognition":
    st.header("🧠 Smart Greet + AI Chat Assistant")

    session_key = "recognized_user"
    if session_key not in st.session_state:
        st.session_state[session_key] = None

    app = load_face_app()
    recognized_user = st.session_state[session_key]
    placeholder = st.empty()

    cap = cv2.VideoCapture(0)
    if not recognized_user:
        st.info("🔍 Scanning for face...")
        for _ in range(30):
            ret, frame = cap.read()
            if not ret:
                continue
            faces = app.get(frame)
            if faces:
                emb = faces[0].normed_embedding
                all_emps = fetch_all_employees()
                for emp in all_emps:
                    if emp['embedding'] is None:
                        continue
                    sim = cosine_similarity(emp['embedding'], emb)
                    if sim > 0.5:
                        recognized_user = emp['name']
                        st.session_state[session_key] = recognized_user
                        greeting_msg = f"Hello {recognized_user}! How can I assist you today?"
                        st.success(f"👋 {greeting_msg}")
                        tts = gTTS(text=greeting_msg, lang="en")
                        temp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}.mp3")
                        tts.save(temp_path)
                        with open(temp_path, "rb") as f:
                            audio_data = f.read()
                            b64 = base64.b64encode(audio_data).decode()
                        audio_html = f"""
                            <audio autoplay>
                                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                            </audio>
                        """
                        st.markdown(audio_html, unsafe_allow_html=True)
                        break
                if recognized_user:
                    break
        if not recognized_user:
            st.warning("😕 Face not recognized. Please try again.")
        cap.release()
    else:
        st.success(f"Welcome back, {recognized_user}! Ask your question below.")

    def transcribe_audio():
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎤 Listening... Speak now...")
            audio = recognizer.listen(source, phrase_time_limit=8)
        try:
            with st.spinner("🧠 Transcribing..."):
                text = recognizer.recognize_google(audio)
                st.success(f"🗣️ You said: {text}")
                return text
        except sr.UnknownValueError:
            st.warning("❌ Could not understand audio.")
        except sr.RequestError as e:
            st.error(f"❌ STT error: {e}")
        return ""

    def generate_autoplay_audio_html(text, lang="en"):
        tts = gTTS(text=text[:300], lang=lang)
        temp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}.mp3")
        tts.save(temp_path)
        with open(temp_path, "rb") as f:
            audio_data = f.read()
            b64 = base64.b64encode(audio_data).decode()
        os.remove(temp_path)
        return f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """

    if recognized_user:
        input_mode = st.radio("Choose input method:", ["Type", "Speak"])
        prompt = ""

        if input_mode == "Type":
            prompt = st.text_input("Type your question:")
        else:
            if st.button("🎤 Speak Now"):
                prompt = transcribe_audio()

        if prompt:
            with st.spinner("🤖 Thinking..."):
                try:
                    response = chat_with_agent(prompt)
                    st.markdown("### 🤖 Response:")
                    st.success(response)
                    st.markdown(generate_autoplay_audio_html(response), unsafe_allow_html=True)
                except Exception as e:
                    st.error("❌ Error generating response.")
                    st.exception(e)

        if st.button("🔁 Logout & Recognize New User"):
            st.session_state[session_key] = None
            st.rerun()

# ========== PAGE 2 ==========
elif mode == "Register New Face":
    st.header("🧑‍💼 Register New Face")
    register_user()

# ========== PAGE 3 ==========
elif mode == "View Today's Observances":
    st.header("📅 Today's National/International Observances")
    obs = get_todays_observances()
    if obs:
        for o in obs:
            if o.get('image'):
                st.image(o['image'], width=100)
            st.markdown(f"**{o['title']}**")
    else:
        st.info("No observances found for today.")

# ========== PAGE 4 ==========
elif mode == "Show Today's Birthdays":
    st.subheader("🎂 Birthday Dashboard")
    today = date.today()
    employees = fetch_all_employees() # Changed from fetch_all_faces

    birthday_people = []
    upcoming_birthdays = []

    if employees:
        for emp in employees:
            name = emp.get('name')
            dob_str = emp.get('dob') # dob from DB might be a string (e.g., '1990-01-01')
            full_image = emp.get('full_image') # image blob (bytes)
            
            if not (name and dob_str):
                st.warning(f"⚠️ Missing name or DOB for an employee record (ID: {emp.get('employee_id')}). Skipping.")
                continue

            try:
                # Ensure dob_str is parsed correctly, assuming '%Y-%m-%d' format from DB
                dob_obj = datetime.strptime(dob_str, "%Y-%m-%d").date()
                
                # Check for today's birthday
                if (dob_obj.month, dob_obj.day) == (today.month, today.day):
                    birthday_people.append(emp)
                # Check for upcoming birthdays this month
                elif dob_obj.month == today.month and dob_obj.day > today.day:
                    upcoming_birthdays.append((dob_obj.day, emp))
            except ValueError: # Catch specific parsing errors for DOB string
                st.warning(f"⚠️ Date format error for {name} (DOB: '{dob_str}'). Please ensure it's YYYY-MM-DD.")
            except Exception as e:
                st.warning(f"⚠️ An unexpected error occurred for {name}: {e}")

    if birthday_people:
        st.markdown("### 🎉 People celebrating today:")
        for person in birthday_people:
            with st.container(border=True): # Using border for better visual separation
                st.markdown(f"### 🧑‍🎂 {person['name']}")
                st.markdown(f"🎂 **DOB:** {person['dob']}")
                if person.get("full_image"):
                    try:
                        img = Image.open(io.BytesIO(person["full_image"]))
                        st.image(img, width=200, caption=f"Photo of {person['name']}")
                    except Exception as e:
                        st.warning(f"⚠️ Unable to display image for {person['name']}: {e}")
                st.markdown("---")
    else:
        st.info("🎈 No birthdays today.")

    if upcoming_birthdays:
        st.markdown("### 📅 Upcoming Birthdays This Month:")
        # Sort by day of month
        for day, person in sorted(upcoming_birthdays, key=lambda x: x[0]):
            with st.container(border=True):
                st.markdown(f"🎁 **{person['name']}** – 🎂 {person['dob']}")
                if person.get("full_image"):
                    try:
                        img = Image.open(io.BytesIO(person["full_image"]))
                        st.image(img, width=150, caption=f"Photo of {person['name']}")
                    except Exception as e:
                        st.warning(f"⚠️ Unable to display image for {person['name']}: {e}")
                st.markdown("---")
    else:
        st.info("📭 No more birthdays this month.")


# ========== PAGE 5 ==========
elif mode == "Show All Users":
    st.subheader("📋 All Registered Users")
    all_employee_names = get_all_employee_names() # Get just the names for listing

    if all_employee_names:
        for name_tuple in all_employee_names: # get_all_employee_names returns list of tuples (name,)
            name = name_tuple[0]
            employee = get_employee_by_name(name) # Fetch full details for each
            
            if not employee:
                st.warning(f"⚠️ Could not retrieve details for {name}.")
                continue

            with st.container(border=True):
                st.markdown(f"### 👤 {employee['name']}")
                st.markdown(f"**DOB:** {employee['dob']}")
                if employee.get("full_image"):
                    try:
                        img = Image.open(io.BytesIO(employee["full_image"]))
                        st.image(img, width=200, caption=f"Photo of {employee['name']}")
                    except Exception as e:
                        st.warning(f"⚠️ Unable to load image for {employee['name']}: {e}")
                st.markdown("---")
    else:
        st.info("No users found in the database.")


# ========== PAGE 6 ==========
elif mode == "Show User Details":
    st.subheader("🔎 View User Details")
    all_employee_names = [u[0] for u in get_all_employee_names()] # Extract names from tuples

    if not all_employee_names:
        st.info("No users registered yet. Please register a new face first.")
    else:
        selected_user_name = st.selectbox("Select user", all_employee_names)

        if st.button("Show Details"):
            employee = get_employee_by_name(selected_user_name)
            if employee:
                col1, col2 = st.columns([1, 2])
                with col1:
                    if employee.get("full_image"):
                        try:
                            img = Image.open(io.BytesIO(employee["full_image"]))
                            st.image(img, caption="Registered Face", width=250)
                        except Exception as e:
                            st.warning(f"No face image found or error loading image: {e}")
                    else:
                        st.warning("No face image found.")
                with col2:
                    st.markdown(f"**👤 Name:** {employee['name']}")
                    st.markdown(f"**🎂 DOB:** {employee['dob']}")
                    # You might display other details here if your employee dict has them (e.g., embedding status)
            else:
                st.error(f"User '{selected_user_name}' not found in database.")

# ========== PAGE 7 ==========
elif mode == "Edit User Details":
    st.subheader("✏️ Edit User Details")
    all_employee_names = [u[0] for u in get_all_employee_names()]  # Extract names from tuples

    if not all_employee_names:
        st.info("No users registered yet to edit.")
    else:
        selected_user_name = st.selectbox("Select user to edit", all_employee_names)

        emp_data = get_employee_by_name(selected_user_name)
        if not emp_data:
            st.warning("User not found.")
            st.stop()

        # Editable fields
        new_name = st.text_input("Name", value=emp_data.get("name", ""))
        new_designation = st.text_input("Designation", value=emp_data.get("designation", ""))
        new_gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(emp_data.get("gender", "Male")))

        # DOB and DOJ: ensure full date range
        dob_val = emp_data.get("dob")
        doj_val = emp_data.get("doj")

        try:
            dob_date = datetime.strptime(dob_val, "%Y-%m-%d").date() if dob_val else date(1990, 1, 1)
        except:
            dob_date = date(1990, 1, 1)
        try:
            doj_date = datetime.strptime(doj_val, "%Y-%m-%d").date() if doj_val else date.today()
        except:
            doj_date = date.today()

        new_dob = st.date_input("Date of Birth", value=dob_date, min_value=date(1900, 1, 1), max_value=date.today())
        new_doj = st.date_input("Date of Joining", value=doj_date, min_value=date(1900, 1, 1), max_value=date.today())

        new_email = st.text_input("Official Email", value=emp_data.get("official_email", ""))
        new_phone = st.text_input("Contact Number", value=emp_data.get("contact_number", ""))
        new_blood = st.text_input("Blood Group", value=emp_data.get("blood_group", ""))
        new_dept = st.text_input("Department", value=emp_data.get("department", ""))
        new_current_addr = st.text_area("Current Address", value=emp_data.get("current_address", ""))
        new_perm_addr = st.text_area("Permanent Address", value=emp_data.get("permanent_address", ""))
        is_guest = st.checkbox("Is Special Guest?", value=emp_data.get("is_special_guest", False))

        # --- IMAGE SECTION ---
        st.markdown("### 🖼️ Profile Picture")
        import numpy as np
        import cv2
        from PIL import Image

        image_blob = emp_data.get("full_image")
        new_image = None

        if image_blob:
            npimg = np.frombuffer(image_blob, dtype=np.uint8)
            img_bgr = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            st.image(img_rgb, caption="Current Photo", use_column_width=True)
        else:
            st.info("No photo currently stored for this user.")

        update_photo = st.radio("Do you want to update the photo?", ["No", "Yes"], index=0)

        if update_photo == "Yes":
            method = st.radio("Choose image update method:", ["Upload", "Capture from Camera"])
            if method == "Upload":
                uploaded = st.file_uploader("Upload new image", type=["jpg", "jpeg", "png"])
                if uploaded:
                    img_pil = Image.open(uploaded)
                    st.image(img_pil, caption="New Uploaded Image", use_column_width=True)
                    new_image = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
            elif method == "Capture from Camera":
                camera_image = st.camera_input("Capture from webcam")
                if camera_image:
                    img_pil = Image.open(camera_image)
                    st.image(img_pil, caption="New Captured Image", use_column_width=True)
                    new_image = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

        if st.button("💾 Update User Details"):
            from databasePLSQL import update_employee_all_fields, update_employee_columns

            success_fields = update_employee_all_fields(
                old_name=selected_user_name,
                new_name=new_name,
                designation=new_designation,
                gender=new_gender,
                dob=new_dob.strftime("%Y-%m-%d"),
                doj=new_doj.strftime("%Y-%m-%d"),
                official_email=new_email,
                contact_number=new_phone,
                blood_group=new_blood,
                department=new_dept,
                current_address=new_current_addr,
                permanent_address=new_perm_addr,
                is_special_guest=is_guest
            )

            success_image = True
            if update_photo == "Yes" and new_image is not None:
                success_image = update_employee_columns(
                    employee_id=emp_data["employee_id"],
                    full_image=new_image
                )

            if success_fields and success_image:
                st.success("✅ User details updated successfully.")
                st.rerun()
            else:
                st.error("❌ Failed to update user details.")

# ========== PAGE 8 ==========
elif mode == "Remove User":
    st.subheader("🗑️ Remove User")
    all_employee_names = [u[0] for u in get_all_employee_names()] # Extract names from tuples

    if not all_employee_names:
        st.info("No users registered yet to remove.")
    else:
        selected_user_name = st.selectbox("Select user to remove", all_employee_names)

        if st.button(f"Permanently Remove {selected_user_name}"):
            remove_employee(selected_user_name) # Call PostgreSQL remove
            st.success(f"User '{selected_user_name}' has been removed.")
            st.rerun() # Rerun to refresh the selectbox