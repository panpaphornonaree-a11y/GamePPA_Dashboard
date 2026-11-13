
import os
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Dashboard แสดงข้อมูลผู้เล่นที่อนุญาตให้เปิดเผย
CORS(app, resources={r"/api/*": {"origins": "*"}})

KEY_FILENAME = "game-ppa-firebase-adminsdk-fbsvc-15eda87a15.json"

def connect_firebase():
    if not firebase_admin._apps:
        local_key = os.path.join("SECRETS", KEY_FILENAME)
        render_key = os.path.join("/etc/secrets", KEY_FILENAME)

        if os.path.exists(render_key):
            key_path = render_key
        else:
            key_path = local_key

        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)

    return firestore.client()


db = connect_firebase()


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Game PPA Dashboard API is running"
    })


@app.route("/api/players", methods=["GET"])
def get_players():
    try:
        docs = db.collection("users").stream()

        players = []

        for doc in docs:
            data = doc.to_dict()

            players.append({
                "username": data.get("username", doc.id),
                "bestScore": data.get("bestScore", 0),
                "playCount": data.get("playCount", 0)
            })

        players.sort(
            key=lambda p: p["bestScore"],
            reverse=True
        )

        response = jsonify({
            "success": True,
            "totalPlayers": len(players),
            "players": players
        })

        response.headers["Cache-Control"] = "no-store"
        return response

    except Exception:
        return jsonify({
            "success": False,
            "message": "Unable to load player data"
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
