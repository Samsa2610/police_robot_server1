import face_recognition
import cv2

# Load and convert the image
image = cv2.imread("suspect.jpg")
if image is None:
    print("Failed to load the image!")
else:
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Detect faces
    face_locations = face_recognition.face_locations(image_rgb)

    if len(face_locations) == 0:
        print("No faces detected!")
    else:
        print(f"{len(face_locations)} face(s) detected!")

        # Draw bounding boxes around detected faces
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)

        # Show the image with detected face(s)
        cv2.imshow('Detected Faces', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()