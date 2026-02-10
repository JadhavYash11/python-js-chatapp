from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
socketio = SocketIO(app)

users = {}

@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("connect")
def handle_connect():
    username = f"User_{random.randint(1000,9999)}"
    gender = random.choice(["boy", "girl"])
    avatar = f"https://avatar.iran.liara.run/public/{gender}?username={username}"

    users[request.sid] = {
        "username": username,
        "avatar": avatar
    }

    emit("set_username", {"username": username})
    emit("user_joined", {"username": username, "avatar": avatar}, broadcast=True)


@socketio.on("send_message")
def handle_send_message(data):
    user = users.get(request.sid)
    if not user:
        return

    emit(
        "new_message",
        {
            "username": user["username"],
            "message": data["message"],
            "avatar": user["avatar"]
        },
        broadcast=True
    )


@socketio.on("update_username")
def handle_update_username(data):
    user = users.get(request.sid)
    if not user:
        return

    old_username = user["username"]
    user["username"] = data["username"]

    emit(
        "username_updated",
        {
            "old_username": old_username,
            "new_username": user["username"]
        },
        broadcast=True
    )


@socketio.on("disconnect")
def handle_disconnect():
    user = users.pop(request.sid, None)
    if user:
        emit("user_left", {"username": user["username"]}, broadcast=True)


if __name__ == "__main__":
    socketio.run(app, debug=True)
