import cv2
import re
import numpy as np
import streamlit as st
from datetime import date
from PIL import Image
from insightface.app import FaceAnalysis
from databasePLSQL import fetch_all_employees, insert_employee, init_db

@st.cache_resource
def get_face_analysis_app():
    app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
    app.prepare(ctx_id=-1)
    return app

def cosine_similarity(a, b):
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def is_valid_name(name):
    return re.match(r"^[A-Za-z_ ]{1,100}$", name) is not None

def register_user():
    st.title("🧑‍💼 New Employee / Guest Registration")
    st.info("Fill the employee details and capture face data.")

    # --- Employee Details ---
    new_name = st.text_input("Full Name:")
    employee_id = st.text_input("Employee ID:")
    gender = st.selectbox("Gender", ["Select", "Male", "Female", "Other"])
    designation = st.text_input("Designation:")
    official_email = st.text_input("Official Email")
    contact_number = st.text_input("Contact Number")
    blood_group = st.text_input("Blood Group")
    department = st.text_input("Department")

    today = date.today()
    default_dob = date(1990, 1, 1)
    new_dob = st.date_input("Date of Birth", value=default_dob, min_value=date(1900, 1, 1), max_value=today)
    new_doj = st.date_input("Date of Joining",value=today,min_value=date(2013, 7, 30), max_value=today)

    current_address = st.text_area("Current Address")
    permanent_address = st.text_area("Permanent Address")

    is_special_guest = st.checkbox("Mark as Special Guest")

    st.divider()

    # --- Formal Photograph (Optional) ---
    st.subheader("📸 Upload or Capture Formal Photograph (Optional)")
    formal_photo_option = st.radio("Choose Formal Photo Input", ["Upload Image", "Capture Using Webcam"])
    formal_photograph = None

    if formal_photo_option == "Upload Image":
        uploaded_file = st.file_uploader("Upload Formal Photograph", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            formal_photograph = Image.open(uploaded_file)
            st.image(formal_photograph, caption="Formal Photo", use_column_width=True)
    else:
        if st.button("📷 Capture Formal Photograph"):
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            if ret:
                st.image(frame, caption="Formal Photograph", channels="BGR")
                formal_photograph = frame
            else:
                st.warning("⚠️ Failed to capture image from webcam.")

    st.divider()

    # --- Capture Face Data ---
    st.subheader("🧠 Capture Face for Recognition")
    if st.button("Start Face Camera"):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            st.error("❌ Unable to access camera.")
            return

        app = get_face_analysis_app()
        faces = app.get(frame)

        if not faces:
            st.warning("⚠️ No face detected. Try again.")
            return

        new_embedding = faces[0].normed_embedding
        face_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        x1, y1, x2, y2 = faces[0].bbox.astype(int)
        cv2.rectangle(face_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        st.image(face_frame, caption="Captured Face", channels="RGB")

        # Validate Inputs
        all_employees = fetch_all_employees()
        existing_ids = [emp['employee_id'] for emp in all_employees]
        existing_names = [emp['name'] for emp in all_employees]
        existing_embeddings = [emp['embedding'] for emp in all_employees if emp['embedding'] is not None]

        if not new_name or not employee_id:
            st.error("❌ Name and Employee ID are mandatory.")
            return
        if gender == "Select":
            st.error("❌ Please select gender.")
            return
        if not is_valid_name(new_name):
            st.error("❌ Invalid name format. Only letters/spaces/underscores allowed.")
            return
        if employee_id in existing_ids:
            st.warning(f"⚠️ Employee ID '{employee_id}' already exists.")
            return
        if new_name in existing_names:
            st.warning(f"⚠️ Name '{new_name}' already exists.")
            return

        # Face duplication check
        for emb in existing_embeddings:
            if cosine_similarity(new_embedding, emb) > 0.4:
                st.warning("⚠️ A similar face already exists in the database.")
                return

        # Final Insert
        success = insert_employee(
            employee_id=employee_id,
            name=new_name,
            dob=new_dob.strftime("%Y-%m-%d"),
            doj=new_doj.strftime("%Y-%m-%d"),
            gender=gender,
            designation=designation,
            official_email=official_email,
            contact_number=contact_number,
            blood_group=blood_group,
            department=department,
            current_address=current_address,
            permanent_address=permanent_address,
            is_special_guest=is_special_guest,
            formal_photograph=formal_photograph,
            full_image=frame,
            embedding=new_embedding
        )

        if success:
            st.success("✅ Registration successful.")
        else:
            st.error("❌ Failed to insert into database.")

# --- Main ---
if __name__ == "__main__":
    st.set_page_config(page_title="Register Face", layout="centered")
    init_db()
    register_user()