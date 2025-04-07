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
    if "user" in session:
        # 檢查使用者是否為管理員
        user_data = db.get_user_collection().find_one({"username": session["user"]})
        if user_data and user_data.get("is_admin", False):
            # 如果是管理員，跳轉到管理員頁面
            return redirect(url_for("admin_panel"))
        else:
            # 如果是非管理員，跳轉到問題頁面
            return redirect(url_for("question_page"))
    # 如果未登入，跳轉到登入頁面
    return redirect(url_for("login_page"))

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

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    success, message = auth.register_user(username, password)
    if success:
        return jsonify({"success": True, "message": message}), 200
    else:
        return jsonify({"success": False, "message": message}), 400

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"success": True, "message": "Logged out"}), 200

@app.route("/admin")
def admin_panel():
    if "user" not in session:
        return "請先登入", 401
    user_data = db.get_user_collection().find_one({"username": session["user"]})
    if not user_data.get("is_admin", False):
        return "你不是管理員", 403
    return render_template("admin.html")

@app.route("/login_page")
def login_page():
    return render_template("login.html")

@app.route("/register_page")
def register_page():
    return render_template("register.html")

@app.route("/questions_page")
def question_page():
    if "user" not in session:
        return redirect(url_for("login_page"))
    return render_template("question.html")

@app.route("/questions", methods=["GET"])
def get_questions():
    if "user" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    question_collection = db.get_question_collection()
    questions = list(question_collection.find({}, {"_id": 0}))
    return jsonify({"success": True, "questions": questions}), 200

@app.route("/edit_question/<question_id>", methods=["PUT"])
def edit_question(question_id):
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

    db.get_question_collection().update_one(
        {"_id": question_id},
        {"$set": {"statement": statement, "options": options, "answer": answer}}
    )
    return jsonify({"success": True, "message": "題目更新成功"}), 200

@app.route("/delete_question/<question_id>", methods=["DELETE"])
def delete_question(question_id):
    if "user" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    user_data = db.get_user_collection().find_one({"username": session["user"]})
    if not user_data.get("is_admin", False):
        return jsonify({"success": False, "message": "Permission denied"}), 403

    db.get_question_collection().delete_one({"_id": question_id})
    return jsonify({"success": True, "message": "題目刪除成功"}), 200

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