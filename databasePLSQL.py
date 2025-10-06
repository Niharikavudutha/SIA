import psycopg2
import numpy as np
import cv2
import requests
import re # For regular expressions to parse Drive links
from datetime import date, datetime # Import datetime for parsing DOB strings

# --- Database Configuration ---

DB_CONFIG = {
    'dbname': 'chatbot', # Keep as is, if your actual DB name has a space
    'user': 'postgres',
    'password': 'Tech@123',
    'host': '10.10.3.73',
    'port': '5432'
}

# --- Database Connection Function ---

def get_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        # print("Database connection established successfully.") # Uncomment for debugging
        return conn
    
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        raise # Re-raise the exception to indicate a critical failure

# --- Database Initialization (Table Creation) ---

def init_db():
    """
    Initializes the database by creating the 'employees' table if it doesn't already exist.
    Includes 'formal_photograph' column.
    Uses BYTEA for binary data (images, embeddings) and BOOLEAN for boolean flags.
    """
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id SERIAL PRIMARY KEY,
                employee_id TEXT UNIQUE,
                name TEXT NOT NULL,
                designation TEXT,
                gender TEXT,
                dob DATE NOT NULL,
                doj DATE,
                official_email TEXT,
                contact_number TEXT,
                blood_group TEXT,
                department TEXT,
                current_address TEXT,
                permanent_address TEXT,
                formal_photograph TEXT,          -- Re-included formal_photograph
                full_image BYTEA,                -- Made nullable for initial processing if needed
                embedding BYTEA,                 -- Made nullable for initial processing if needed
                is_special_guest BOOLEAN DEFAULT FALSE
            )
        ''')
        conn.commit()
        print("Table 'employees' checked/created successfully.")
        # 2. Sync SERIAL sequence with max(id)
        c.execute("""
            SELECT setval(
                pg_get_serial_sequence('employees', 'id'),
                COALESCE((SELECT MAX(id) FROM employees), 1),
                true
            );
        """)
        conn.commit()
        print("🔁 SERIAL sequence for 'employees.id' synced successfully.")

    except psycopg2.Error as e:
        print(f"Error initializing database: {e}")

    finally:
        if conn:
            conn.close()

# --- Function to Insert Employee Data (including face data) ---

def insert_employee(
    name, dob,
    employee_id=None, doj=None, is_special_guest=False,
    gender=None, designation=None,
    current_address=None, permanent_address=None,
    official_email=None,
    contact_number=None,
    blood_group=None, department=None,
    formal_photograph=None, # Re-included formal_photograph parameter
    full_image=None,         # Now optional, can be populated later
    embedding=None           # Now optional, can be populated later
):
    """
    Inserts a new employee record into the 'employees' table.
    Includes 'formal_photograph' parameter.
    'full_image' and 'embedding' can now be None initially.
    Args:
        name (str): Employee's full name. (NOT NULL)
        dob (str or datetime.date): Date of Birth in 'YYYY-MM-DD' format or a date object. (NOT NULL)
        employee_id (str, optional): Unique employee identifier.
        doj (str or datetime.date, optional): Date of Joining.
        is_special_guest (bool, optional): Indicates if the employee is a special guest. Defaults to False.
        gender (str, optional): Employee's gender.
        designation (str, optional): Employee's designation.
        current_address (str, optional): Employee's current address.
        permanent_address (str, optional): Employee's permanent address.
        official_email (str, optional): Employee's official email.
        contact_number (str, optional): Employee's contact number.
        blood_group (str, optional): Employee's blood group.
        department (str, optional): Employee's department.
        formal_photograph (str, optional): URL or path to the formal photograph.
        full_image (numpy.ndarray, optional): Full image as a numpy array.
        embedding (numpy.ndarray, optional): Face embedding as a numpy array.
    Returns:
        bool: True if insertion was successful, False otherwise.
    """
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor()
        
        embedding_blob = None
        if embedding is not None:
            embedding_blob = embedding.astype(np.float32).tobytes()

        full_blob = None
        if full_image is not None:
            # Ensure the image is in BGR format if coming from something like PIL (RGB)
            if full_image.shape[2] == 3 and full_image.dtype == np.uint8:
                # Convert from RGB (PIL default) to BGR (OpenCV default) if necessary
                # If image is already from OpenCV capture, this might not be needed
                pass # Assuming full_image is already BGR for cv2.imencode
            
            success, full_buffer = cv2.imencode('.jpg', full_image)
            if not success:
                raise ValueError("Could not encode full_image to JPEG bytes.")
            full_blob = full_buffer.tobytes()

        c.execute(
            '''
            INSERT INTO employees (
                employee_id, name, dob, doj, gender, designation,
                current_address, permanent_address,
                official_email,
                contact_number,
                blood_group, department,
                formal_photograph,
                full_image, embedding, is_special_guest
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''',
            (
                employee_id, name, dob, doj, gender, designation,
                current_address, permanent_address,
                official_email,
                contact_number,
                blood_group, department,
                formal_photograph,
                psycopg2.Binary(full_blob) if full_blob else None,
                psycopg2.Binary(embedding_blob) if embedding_blob else None,
                is_special_guest
            )
        )
        conn.commit()
        print(f"Employee '{name}' inserted successfully.")
        return True
    except psycopg2.IntegrityError as e:
        print(f"[Insert Error] Duplicate employee_id or name: {e}")
        if conn:
            conn.rollback()
        return False
    except (psycopg2.Error, ValueError) as e:
        print(f"[Insert Error] Failed to insert employee '{name}': {e}")
        if conn:
            conn.rollback() # Rollback transaction on error
        return False
    finally:
        if conn:
            conn.close()

# --- Function to Update Employee Columns ---

def update_employee_columns(
    employee_id,
    full_image=None,
    embedding=None,
    is_special_guest=None,
    formal_photograph=None
):
    """
    Updates specified columns (full_image, embedding, is_special_guest, formal_photograph) for an existing employee.

    Args:
        employee_id (str): The unique employee ID of the record to update. (NOT NULL)
        full_image (numpy.ndarray, optional): New full image as a numpy array. If None, column is not updated.
        embedding (numpy.ndarray, optional): New face embedding as a numpy array. If None, column is not updated.
        is_special_guest (bool, optional): New special guest status. If None, column is not updated.
        formal_photograph (str, optional): New URL or path for the formal photograph. If None, column is not updated.
    Returns:
        bool: True if update was successful, False otherwise.
    """
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor()
        set_clauses = []
        params = []
        if formal_photograph is not None:
            set_clauses.append("formal_photograph = %s")
            params.append(formal_photograph)

        if full_image is not None:
            success, full_buffer = cv2.imencode('.jpg', full_image)
            if not success:
                raise ValueError("Could not encode full_image to JPEG bytes for update.")
            set_clauses.append("full_image = %s")
            params.append(psycopg2.Binary(full_buffer.tobytes()))
        # Option to set full_image to NULL if specifically passed as None
        # This allows explicitly clearing the image
        elif full_image is None and 'full_image' not in [s.split('=')[0].strip() for s in set_clauses]: 
             # Check if it was explicitly passed as None, but not already set by a prior `if full_image is not None`
            # This logic needs to be careful: if `full_image` is truly not provided, don't update.
            # If `full_image=None` is explicitly passed, then set to NULL.
            # A common pattern is to only include parameters if they are NOT None,
            # and if you want to set to NULL, you explicitly pass `value=None`
            pass # Keep previous behavior: if full_image is None and not updated, leave it as is.

        if embedding is not None:
            set_clauses.append("embedding = %s")
            params.append(psycopg2.Binary(embedding.astype(np.float32).tobytes()))
        # Option to set embedding to NULL if specifically passed as None
        elif embedding is None and 'embedding' not in [s.split('=')[0].strip() for s in set_clauses]:
            pass # Same as above for full_image

        if is_special_guest is not None:
            set_clauses.append("is_special_guest = %s")
            params.append(is_special_guest)

        if not set_clauses:
            print(f"No columns specified for update for employee_id '{employee_id}'.")
            return False

        query = f"UPDATE employees SET {', '.join(set_clauses)} WHERE employee_id = %s"
        params.append(employee_id)

        c.execute(query, tuple(params))
        conn.commit()

        if c.rowcount > 0:
            print(f"Employee with ID '{employee_id}' updated successfully.")
            return True
        else:
            print(f"No employee found with ID '{employee_id}' to update.")
            return False

    except (psycopg2.Error, ValueError) as e:
        print(f"[Update Error] Failed to update employee '{employee_id}': {e}")
        if conn:
            conn.rollback() # Rollback transaction on error
        return False
    finally:
        if conn:
            conn.close()

# --- Helper Function to get Google Drive Direct Download Link ---
def get_gdrive_direct_download_link(drive_url):
    """
    Converts a Google Drive 'open' or 'view' URL to a direct download URL.
    Extracts the file ID and constructs the 'uc?export=download' link.
    """
    match = re.search(r'id=([a-zA-Z0-9_-]+)', drive_url)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    print(f"Warning: Could not extract file ID from Google Drive URL: {drive_url}")
    return drive_url # Return original if ID not found, might still work for some direct links

# --- New Function: Process Image and Embeddings from Drive Link ---
def process_and_update_employee_face_data(employee_id):
    """
    Fetches the formal_photograph link, downloads the image,
    extracts face embeddings, and updates full_image and embedding columns.
    Args:
        employee_id (str): The unique employee ID of the record to process.
    Returns:
        bool: True if processing and update was successful, False otherwise.
    """
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor()
        # 1. Fetch formal_photograph URL
        c.execute("SELECT formal_photograph FROM employees WHERE employee_id = %s", (employee_id,))
        row = c.fetchone()
        if not row or not row[0]:
            print(f"No formal_photograph URL found for employee ID: {employee_id}")
            return False
        formal_photo_url = row[0]
        print(f"Found formal_photograph URL: {formal_photo_url}")
        
        # Convert to direct download link if it's a Google Drive 'open' link
        download_url = get_gdrive_direct_download_link(formal_photo_url)
        print(f"Attempting to download from: {download_url}")
        
        # 2. Download the image
        response = requests.get(download_url, stream=True)
        response.raise_for_status() # Raise an exception for HTTP errors

        image_data = response.content
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError(f"Could not decode image from URL: {download_url}")
        print(f"Image downloaded and decoded successfully. Image shape: {img.shape}")

        # 3. TODO: Extract face embeddings from the image
        # THIS IS A PLACEHOLDER. YOU NEED TO INTEGRATE YOUR FACE RECOGNITION LIBRARY HERE.
        # Example using a hypothetical face_recognition library:
        # import face_recognition # You would import this at the top of this file
        # face_locations = face_recognition.face_locations(img)
        # if not face_locations:
        #     print(f"No face found in the image for employee ID: {employee_id}")
        #     face_embedding = None # Set to None if no face is found
        # else:
        #     face_encodings = face_recognition.face_encodings(img, face_locations)
        #     face_embedding = face_encodings[0]
        
        # For demonstration, using a dummy embedding.
        # Replace this with your actual face embedding extraction logic.
        face_embedding = np.random.rand(128).astype(np.float32) # Common embedding size is 128 or 512
        print(f"Face embedding (dummy) generated. Shape: {face_embedding.shape}")

        # 4. Update full_image and embedding columns
        success = update_employee_columns(
            employee_id=employee_id,
            full_image=img,
            embedding=face_embedding
        )
        return success
    except requests.exceptions.RequestException as e:
        print(f"[Download Error] Failed to download image for employee ID '{employee_id}': {e}")
        return False
    except ValueError as e:
        print(f"[Processing Error] {e}")
        return False
    except psycopg2.Error as e:
        print(f"[DB Error] Failed to process employee data for '{employee_id}': {e}")
        return False
    except Exception as e:
        print(f"[General Error] An unexpected error occurred during face data processing for '{employee_id}': {e}")
        return False
    finally:
        if conn:
            conn.close()

# --- Function to Fetch All Employee Data ---
def fetch_all_employees():
    """
    Fetches all employee records from the 'employees' table.
    Returns:
        list[dict]: A list of dictionaries, where each dictionary represents an employee.
                    'embedding' is a numpy array, 'full_image' is raw byte data.
    """
    conn = None
    employees = []
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            SELECT
                id, employee_id, name, dob, doj, gender, designation,
                current_address, permanent_address,
                official_email,
                contact_number,
                blood_group, department,
                formal_photograph, -- Re-included here
                full_image, embedding, is_special_guest
            FROM employees
        ''')
        rows = c.fetchall()

        for row in rows:
            try:
                (
                    emp_id_db, emp_id, name, dob, doj, gender, desig,
                    curr_addr, perm_addr,
                    off_email,
                    contact,
                    blood_group, department,
                    formal_photo, # Variable for formal_photograph
                    full_blob, embedding_blob, is_guest
                ) = row

                # Convert embedding_blob (bytes) back to numpy array if not None
                embedding_array = np.frombuffer(embedding_blob, dtype=np.float32) if embedding_blob else None

                employee_data = {
                    'id': emp_id_db,
                    'employee_id': emp_id,
                    'name': name,
                    'dob': dob.strftime('%Y-%m-%d') if dob else None, # Format date objects to string
                    'doj': doj.strftime('%Y-%m-%d') if doj else None,
                    'gender': gender,
                    'designation': desig,
                    'current_address': curr_addr,
                    'permanent_address': perm_addr,
                    'official_email': off_email,
                    'contact_number': contact,
                    'blood_group': blood_group,
                    'department': department,
                    'formal_photograph': formal_photo, # Returned as part of the dictionary
                    'full_image': full_blob, # Keep as bytes, or decode if needed
                    'embedding': embedding_array,
                    'is_special_guest': is_guest
                }
                employees.append(employee_data)
            except Exception as e:
                print(f"[Load Error] Failed to process row for employee '{row[2] if len(row) > 2 else 'Unknown'}': {e}")
                continue
    except psycopg2.Error as e:
        print(f"[Fetch Error] Failed to fetch all employees: {e}")
    finally:
        if conn:
            conn.close()
    return employees

# --- Function to Fetch Image Blob by Name ---
def fetch_image_blob_by_name(name):
    """
    Fetches the full_image (BYTEA) for a given employee name.
    Args:
        name (str): The name of the employee.
    Returns:
        bytes or None: The binary image data if found, otherwise None.
    """
    conn = None
    full_image_blob = None
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT full_image FROM employees WHERE name = %s", (name,))
        row = c.fetchone()
        if row:
            full_image_blob = row[0]
            # print(f"Full image for '{name}' fetched successfully.") # Uncomment for debugging
        else:
            print(f"No image found for employee '{name}'.")
    except psycopg2.Error as e:
        print(f"[Fetch Image Error] Failed to fetch image for '{name}': {e}")
    finally:
        if conn:
            conn.close()
    return full_image_blob

# --- NEW FUNCTION: Get All Employee Names (for select boxes) ---
def get_all_employee_names():
    """
    Fetches only the names of all employees from the 'employees' table.
    Returns:
        list[tuple]: A list of tuples, where each tuple contains (name,).
    """
    conn = None
    names = []
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT name FROM employees ORDER BY name") # Order by name for consistency
        rows = c.fetchall()
        names = rows # rows will already be a list of tuples like [('Name1',), ('Name2',)]
    except psycopg2.Error as e:
        print(f"[Fetch Names Error] Failed to fetch employee names: {e}")
    finally:
        if conn:
            conn.close()
    return names

# --- NEW FUNCTION: Get Employee By Name ---
def get_employee_by_name(name):
    """
    Fetches a single employee record by their name.
    Returns:
        dict or None: A dictionary representing the employee, or None if not found.
    """
    conn = None
    employee_data = None
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            SELECT
                id, employee_id, name, dob, doj, gender, designation,
                current_address, permanent_address,
                official_email,
                contact_number,
                blood_group, department,
                formal_photograph,
                full_image, embedding, is_special_guest
            FROM employees
            WHERE name = %s
        ''', (name,))
        row = c.fetchone()

        if row:
            (
                emp_id_db, emp_id, name, dob, doj, gender, desig,
                curr_addr, perm_addr,
                off_email,
                contact,
                blood_group, department,
                formal_photo,
                full_blob, embedding_blob, is_guest
            ) = row

            embedding_array = np.frombuffer(embedding_blob, dtype=np.float32) if embedding_blob else None

            employee_data = {
                'id': emp_id_db,
                'employee_id': emp_id,
                'name': name,
                'dob': dob.strftime('%Y-%m-%d') if dob else None,
                'doj': doj.strftime('%Y-%m-%d') if doj else None,
                'gender': gender,
                'designation': desig,
                'current_address': curr_addr,
                'permanent_address': perm_addr,
                'official_email': off_email,
                'contact_number': contact,
                'blood_group': blood_group,
                'department': department,
                'formal_photograph': formal_photo,
                'full_image': full_blob,
                'embedding': embedding_array,
                'is_special_guest': is_guest
            }
    except psycopg2.Error as e:
        print(f"[Fetch Error] Failed to fetch employee '{name}': {e}")
    finally:
        if conn:
            conn.close()
    return employee_data

# --- NEW FUNCTION: Update Employee Name ---
def update_employee_name(old_name, new_name):
    """
    Updates the name of an employee.
    Returns True on success, False otherwise.
    """
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE employees SET name = %s WHERE name = %s", (new_name, old_name))
        conn.commit()
        if c.rowcount > 0:
            print(f"Successfully updated name from '{old_name}' to '{new_name}'.")
            return True
        else:
            print(f"No employee found with name '{old_name}' to update.")
            return False
    except psycopg2.Error as e:
        print(f"[Update Name Error] Failed to update name for '{old_name}': {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

# --- NEW FUNCTION: Update Employee DOB ---
def update_employee_dob(name, new_dob_str):
    """
    Updates the date of birth of an employee.
    Args:
        name (str): The name of the employee to update.
        new_dob_str (str): The new date of birth in 'YYYY-MM-DD' format.
    Returns True on success, False otherwise.
    """
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE employees SET dob = %s WHERE name = %s", (new_dob_str, name))
        conn.commit()
        if c.rowcount > 0:
            print(f"Successfully updated DOB for '{name}' to '{new_dob_str}'.")
            return True
        else:
            print(f"No employee found with name '{name}' to update DOB.")
            return False
    except psycopg2.Error as e:
        print(f"[Update DOB Error] Failed to update DOB for '{name}': {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
def update_employee_all_fields(
    old_name, new_name, designation, gender, dob, doj,
    official_email, contact_number, blood_group, department,
    current_address, permanent_address, is_special_guest
):
    """
    Updates all editable fields for an employee by their old name.
    Returns True on success, False otherwise.
    """
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor()
        query = """
            UPDATE employees
            SET name = %s,
                designation = %s,
                gender = %s,
                dob = %s,
                doj = %s,
                official_email = %s,
                contact_number = %s,
                blood_group = %s,
                department = %s,
                current_address = %s,
                permanent_address = %s,
                is_special_guest = %s
            WHERE name = %s;
        """
        c.execute(query, (
            new_name, designation, gender, dob, doj,
            official_email, contact_number, blood_group, department,
            current_address, permanent_address, is_special_guest,
            old_name
        ))
        conn.commit()
        if c.rowcount > 0:
            print(f"Successfully updated all fields for '{old_name}'.")
            return True
        else:
            print(f"No employee found with name '{old_name}' to update.")
            return False
    except psycopg2.Error as e:
        print(f"[Update All Fields Error] Failed to update employee '{old_name}': {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

# --- NEW FUNCTION: Remove Employee ---
def remove_employee(name):
    """
    Removes an employee record from the 'employees' table by name.
    Returns True on success, False otherwise.
    """
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM employees WHERE name = %s", (name,))
        conn.commit()
        if c.rowcount > 0:
            print(f"Employee '{name}' removed successfully.")
            return True
        else:
            print(f"No employee found with name '{name}' to remove.")
            return False
    except psycopg2.Error as e:
        print(f"[Delete Error] Failed to remove employee '{name}': {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


# --- Example Usage (Uncomment to Run) ---
if __name__ == "__main__":
    # 1. Initialize the database (create table if not exists)
    init_db()
