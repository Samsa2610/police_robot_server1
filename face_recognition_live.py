import cv2
import sqlite3
import face_recognition
import pickle
import requests
import json
import base64
import time

# Load known faces from the database
conn = sqlite3.connect("suspects.db")
c = conn.cursor()
c.execute("SELECT name, id_number, nationality, encoding FROM suspects")
known_faces = [(row[0], row[1], row[2], pickle.loads(row[3])) for row in c.fetchall()]
conn.close()

print(f"Loaded {len(known_faces)} faces from the database.")

# Open the camera
video_capture = cv2.VideoCapture(0)
video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Frame skipping for better performance
frame_count = 0
process_every_n_frames = 3  

# Store recognized faces and timestamps
recognized_faces = {}
face_tracker = {}  # Keeps faces for bounding box display
face_appearance_time = {}  # Track how long a face stays in the frame
face_timeout = 2  # Bounding box remains for 2 frames after the face disappears

while True:
    ret, frame = video_capture.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame_count += 1
    face_names = []
    face_locations = []

    if frame_count % process_every_n_frames == 0:
        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Detect faces
        face_locations = face_recognition.face_locations(rgb_frame, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        current_time = time.time()
        detected_faces = []

        for (face_encoding, face_location) in zip(face_encodings, face_locations):
            name = "Unknown"
            id_number = ""
            nationality = ""

            for stored_name, stored_id, stored_nationality, stored_encoding in known_faces:
                matches = face_recognition.compare_faces([stored_encoding], face_encoding, tolerance=0.6)
                if True in matches:
                    name = stored_name
                    id_number = stored_id
                    nationality = stored_nationality
                    break

            full_info = f"{name} | ID: {id_number} | {nationality}"
            face_names.append(full_info)
            detected_faces.append(full_info)

            # Track face duration
            if full_info in face_appearance_time:
                face_appearance_time[full_info] += 1
            else:
                face_appearance_time[full_info] = 1  # First appearance

            # Keep track of seen faces
            recognized_faces[full_info] = current_time
            face_tracker[full_info] = (face_location, current_time)

            # Send suspect info **only if the face remains in frame for 5+ seconds**
            if name != "Unknown" and face_appearance_time[full_info] >= 5:
                # Capture detected face image
                top, right, bottom, left = [v * 2 for v in face_location]
                face_image = frame[top:bottom, left:right]
                _, img_encoded = cv2.imencode(".jpg", face_image)
                detected_face_encoded = base64.b64encode(img_encoded).decode("utf-8")

                # Send recognition data to server
                data = {"recognized_name": full_info, "detected_image": detected_face_encoded}
                try:
                    requests.post("https://github.com/Samsa2610/police_robot_server.git", json=data, timeout=1)
                except requests.exceptions.RequestException:
                    print("Warning: Failed to send data to the server")

    # Remove faces that haven't been seen for `face_timeout` frames
    face_tracker = {k: v for k, v in face_tracker.items() if time.time() - v[1] < face_timeout}

    # Draw bounding boxes smoothly
    for name, (face_location, timestamp) in face_tracker.items():
        top, right, bottom, left = [v * 2 for v in face_location]
        color = (0, 0, 255) if "Unknown" in name else (0, 255, 0)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    cv2.imshow("Face Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video_capture.release()
cv2.destroyAllWindows()





















