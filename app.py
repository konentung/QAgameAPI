from flask import Flask, request, jsonify, session
from flask_cors import CORS
from mongodb import MongoDB
from map import AuthManager
from flask import render_template, redirect, url_for

app = Flask(__name__)
# CORS(app)
CORS(app, supports_credentials=True)
app.secret_key = "supersecretkey"

db = MongoDB()
auth = AuthManager(db)

@app.route("/")
def index():
    return redirect(url_for("login_page"))

@app.route("/login_page")
def login_page():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    success, message, is_admin = auth.login_user(username, password)

    if success:
        session["user"] = username
        return jsonify({"success": True, "message": message, "is_admin": is_admin}), 200
    else:
        return jsonify({"success": False, "message": message}), 401

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"success": True, "message": "Logged out"}), 200

@app.route("/questions", methods=["GET"])
def get_questions():
    if "user" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    question_collection = db.get_question_collection()
    questions = list(question_collection.find({}, {"_id": 0}))
    return jsonify({"success": True, "questions": questions}), 200

@app.route("/admin")
def admin_panel():
    if "user" not in session:
        return "請先登入", 401
    user_data = db.get_user_collection().find_one({"username": session["user"]})
    if not user_data.get("is_admin", False):
        return "你不是管理員", 403
    return render_template("admin.html")

@app.route("/add_question", methods=["POST"])
def add_question():
    if "user" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    user_data = db.get_user_collection().find_one({"username": session["user"]})
    if not user_data.get("is_admin", False):
        return jsonify({"success": False, "message": "Permission denied"}), 403

    data = request.get_json()
    statement = data.get("statement")
    options = data.get("options")
    answer = data.get("answer")

    if not statement or not options or not answer:
        return jsonify({"success": False, "message": "缺少必要欄位"}), 400

    db.get_question_collection().insert_one({
        "statement": statement,
        "options": options,
        "answer": answer
    })
    return jsonify({"success": True, "message": "新增成功"}), 200

if __name__ == "__main__":
    app.run()