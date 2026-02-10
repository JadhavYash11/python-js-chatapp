from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)

# IMPORTANT: polling + threading for Render Free
socketio = SocketIO(
    app,
    async_mode="threading",
    cors_allowed_origins="*",
    transports=["polling"],
    allow_upgrades=False
)

users = {}

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("connect")
def handle_connect():
    username = f"User_{random.randint(1000,9999)}"
    gender = random.choice(["girl", "boy"])
    avatar_url = f"https://avatar.iran.liara.run/public/{gender}?username={username}"

    users[request.sid] = {
        "username": username,
        "avatar": avatar_url
    }

    emit("set_username", {"username": username})
    emit("user_joined", {
        "username": username,
        "avatar": avatar_url
    }, broadcast=True)

@socketio.on("disconnect")
def handle_disconnect():
    user = users.pop(request.sid, None)
    if user:
        emit("user_left", {"username": user["username"]}, broadcast=True)

@socketio.on("send_message")
def handle_message(data):
    user = users.get(request.sid)
    if not user:
        return

    emit("new_message", {
        "username": user["username"],
        "avatar": user["avatar"],
        "message": data.get("message", "")
    }, broadcast=True)

@socketio.on("update_username")
def handle_update_username(data):
    user = users.get(request.sid)
    if not user:
        return

    old = user["username"]
    new = data.get("username", old)
    user["username"] = new

    emit("username_updated", {
        "old_username": old,
        "new_username": new
    }, broadcast=True)

if __name__ == "__main__":
    socketio.run(app)
