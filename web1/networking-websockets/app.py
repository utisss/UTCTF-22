import flask
import flask_sock
import base64
import os
import json
import jwt

secret = base64.b64decode(os.environ["SECRET"].encode("ascii"))

app = flask.Flask(__name__)
sock = flask_sock.Sock(app)

# ok the actual http code starts here
@app.route("/")
def index():
    return flask.render_template("index.html")

#@app.route("/notepad", methods=["GET"])
#def notepad():
#    sess = flask.request.cookies.get("notes-session")
#    if sess:
#        try:
#            username = cookie_un(sess)
#            with open(notes_dir + username, "r") as notesfile:
#                return flask.render_template("notepad.html", notes=notesfile.read())
#        except InvalidCookieException:
#            resp = flask.make_response(flask.redirect(flask.url_for("login_page")))
#            resp.set_cookie("notes-session", "", expires=0)
#            return resp
#    else:
#        return flask.redirect(flask.url_for("login_page"))
#
#@app.route("/notepad", methods=["POST"])
#def notepad_save():
#    sess = flask.request.cookies.get("notes-session")
#    if sess:
#        try:
#            username = cookie_un(sess)
#            with open(notes_dir + username, "w") as notesfile:
#                notesfile.write(flask.request.form["notes"])
#            return flask.redirect(flask.url_for("notepad"))
#        except InvalidCookieException:
#            resp = flask.make_response(flask.redirect(flask.url_for("login_page")))
#            resp.set_cookie("notes-session", "", expires=0)
#    else:
#        return flask.redirect(flask.url_for("login_page"))

@app.route("/internal/login", methods=["GET"])
def login_page():
    return flask.render_template("logreg.html", desc="Login")

@app.route("/internal/user")
def user_page():
    sess = flask.request.cookies.get("flask-session")
    if not sess:
        return flask.redirect(flask.url_for("login_page"))
    try:
        sess = jwt.decode(sess, secret, algorithms=["HS256"])
    except jwt.exceptions.InvalidTokenError:
        return flask.redirect(flask.url_for("login_page"))
    return flask.render_template("userpage.html", flag=os.environ["FLAG"])

#@app.route("/register", methods=["GET"])
#def register_page():
#    return flask.render_template("logreg.html", desc="Register")
#
#@app.route("/register", methods=["POST"])
#def register():
#    username = flask.request.form["username"]
#    password = flask.request.form["password"]
#    if not check_characters(username):
#        flask.abort(401)
#    with sqlite3.connect(sq_file) as sq:
#        cur = sq.cursor()
#        cur.execute("SELECT username FROM users WHERE username=?", (username,))
#        if cur.fetchone():
#            return flask.render_template("logreg.html", desc="Register", error="User already exists")
#        cur.execute("INSERT INTO users VALUES (?, ?)", (username, password))
#        sq.commit()
#    open(notes_dir + username, "a").close()
#    return flask.redirect(flask.url_for("login_page"))
#

@sock.route('/internal/ws')
def websocket(ws):
    ws.send("begin")
    data = ws.receive(timeout=2)
    if (data != "begin"):
        ws.send("error")
        ws.close()
        return
    while True:
        data = ws.receive(timeout=2)
        if data == "goodbye":
            ws.send("goodbye")
            ws.close()
            return
        if data.startswith("user "):
            if data != "user admin":
                ws.send("baduser")
                continue
        else:
            ws.send("error")
            ws.close()
            return
        data = ws.receive(timeout=2)
        if data.startswith("pass "):
            if data != "pass 907":
                ws.send("badpass")
                continue
            else:
                ws.send("session " + jwt.encode({"username": "admin", "authenticated": True}, secret, algorithm="HS256"))
        else:
            ws.send("error")
            ws.close()
            return
