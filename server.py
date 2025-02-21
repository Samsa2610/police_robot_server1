from flask import Flask, render_template, jsonify, request
import sqlite3
import base64
import time

app = Flask(__name__)

# Store recognized suspects with timestamp
recognized_suspects = {}

def get_suspects():
    conn = sqlite3.connect("suspects.db")
    c = conn.cursor()
    c.execute("SELECT id, name, id_number, nationality, image FROM suspects")
    suspects = []

    for row in c.fetchall():
        suspect_id, name, id_number, nationality, image_blob = row
        image_base64 = base64.b64encode(image_blob).decode("utf-8") if image_blob else None

        suspects.append({
            "id": suspect_id,
            "name": name,
            "id_number": id_number,
            "nationality": nationality,
            "image": image_base64,
            "detected_image": None  # Initially empty
        })

    conn.close()
    return suspects

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/notifications")
def get_notifications():
    """Send notification data to frontend"""
    current_time = time.time()
    global recognized_suspects

    # Remove suspects not detected for 5+ seconds
    recognized_suspects = {k: v for k, v in recognized_suspects.items() if current_time - v["timestamp"] < 5}

    return jsonify({"recognized_suspects": list(recognized_suspects.values())})

@app.route("/recognition", methods=["POST"])
def receive_recognition():
    global recognized_suspects
    data = request.json
    recognized_name = data.get("recognized_name", "")
    detected_image = data.get("detected_image", "")

    suspects = get_suspects()
    for suspect in suspects:
        if suspect["name"] in recognized_name:
            recognized_suspects[suspect["id"]] = {
                "name": suspect["name"],
                "id_number": suspect["id_number"],
                "nationality": suspect["nationality"],
                "image": suspect["image"],
                "detected_image": detected_image,  # Store the detected image
                "timestamp": time.time()
            }
            break

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)







