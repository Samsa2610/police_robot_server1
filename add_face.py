import sqlite3
import face_recognition
import pickle
import cv2

# Connect to the database
conn = sqlite3.connect('suspects.db')
c = conn.cursor()

# Create the table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS suspects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        id_number TEXT,
        nationality TEXT,
        encoding BLOB,
        image BLOB)
''')

# Main Menu
print("Suspect Management System")
print("1. Add a Suspect")
print("2. Delete a Suspect")
print("3. Update a Suspect")
choice = input("Enter your choice (1, 2, or 3): ")

if choice == '1':
    # Add Suspect
    name = input("Enter the suspect's name: ")
    id_number = input("Enter the suspect's ID number: ")
    nationality = input("Enter the suspect's nationality: ")

    # Load the suspect image using OpenCV
    image_path = input("Enter the suspect image filename: ")
    image = cv2.imread(image_path)

    if image is None:
        print("Failed to load the image!")
    else:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(image_rgb)
        encodings = face_recognition.face_encodings(image_rgb, face_locations)

        if len(encodings) == 0:
            print("No face found in the image!")
        else:
            encoding_blob = pickle.dumps(encodings[0])
            _, image_encoded = cv2.imencode('.jpg', image)
            image_blob = image_encoded.tobytes()

            # Insert into the database
            c.execute("INSERT INTO suspects (name, id_number, nationality, encoding, image) VALUES (?, ?, ?, ?, ?)",
                      (name, id_number, nationality, encoding_blob, image_blob))
            conn.commit()
            print(f"Suspect '{name}' added successfully!")

elif choice == '2':
    # Delete Suspect
    delete_choice = input("Delete by (1) Table ID or (2) Suspect Information (Name, ID, Nationality)? Enter 1 or 2: ")

    if delete_choice == '1':
        table_id = input("Enter the table ID: ")
        c.execute("DELETE FROM suspects WHERE id=?", (table_id,))
    elif delete_choice == '2':
        name = input("Enter the suspect's name: ")
        suspect_id = input("Enter the suspect's ID number: ")
        nationality = input("Enter the suspect's nationality: ")
        c.execute("DELETE FROM suspects WHERE name=? AND id_number=? AND nationality=?", (name, suspect_id, nationality))
    else:
        print("Invalid choice. No action taken.")

    conn.commit()
    print("Suspect deletion process completed.")

elif choice == '3':
    # Update Suspect
    table_id = input("Enter the table ID of the suspect to update: ")
    new_name = input("Enter the new name (leave blank to keep unchanged): ")
    new_id_number = input("Enter the new ID number (leave blank to keep unchanged): ")
    new_nationality = input("Enter the new nationality (leave blank to keep unchanged): ")

    # Load new suspect image if provided
    update_image = input("Do you want to update the suspect's image? (yes/no): ").lower()
    if update_image == 'yes':
        image_path = input("Enter the new suspect image filename: ")
        image = cv2.imread(image_path)

        if image is None:
            print("Failed to load the image!")
        else:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(image_rgb)
            encodings = face_recognition.face_encodings(image_rgb, face_locations)

            if len(encodings) == 0:
                print("No face found in the image!")
            else:
                encoding_blob = pickle.dumps(encodings[0])
                _, image_encoded = cv2.imencode('.jpg', image)
                image_blob = image_encoded.tobytes()
                c.execute("UPDATE suspects SET encoding=?, image=? WHERE id=?", (encoding_blob, image_blob, table_id))

    if new_name:
        c.execute("UPDATE suspects SET name=? WHERE id=?", (new_name, table_id))
    if new_id_number:
        c.execute("UPDATE suspects SET id_number=? WHERE id=?", (new_id_number, table_id))
    if new_nationality:
        c.execute("UPDATE suspects SET nationality=? WHERE id=?", (new_nationality, table_id))

    conn.commit()
    print("Suspect update process completed.")

else:
    print("Invalid option selected.")

conn.close()
