from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os
import config

app = Flask(__name__)

# Database configuration
os.makedirs("data", exist_ok=True)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(os.getcwd(), "data", "chats.db")
app.config["SECRET_KEY"] = "smartbiz-secret-key-change-this"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# ---------- DATABASE MODELS ----------

# Chat history table
class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.String(500))
    bot_reply = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.now)


# Order table
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(300))
    items = db.Column(db.String(500))
    status = db.Column(db.String(20), default="Pending")
    timestamp = db.Column(db.DateTime, default=datetime.now)


# ---------- FAQ LOADER ----------

def load_faqs():
    try:
        with open("faqs.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


# ---------- ROUTES ----------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").lower()
    faqs = load_faqs()
    reply = ""

    # Greeting check
    if any(word in user_message for word in ["hi", "hello", "salam", "assalam", "hey"]):
        reply = "Assalam-o-Alaikum! Kaise madad kar sakta hoon?"

    # Order check
    elif any(word in user_message for word in ["order", "book", "mangwana"]):
        reply = "Order karne ke liye 'Order Now' button dabayein ya apna naam, address aur order likhein."

    # FAQ match
    else:
        for keyword, answer in faqs.items():
            if keyword in user_message:
                reply = answer
                break

        if not reply:
            reply = "Maaf kijiye, samajh nahi aaya. Aap 'timing', 'location', 'price', 'delivery', 'payment' pooch sakte hain."

    # Save to database
    chat_entry = Chat(user_message=user_message, bot_reply=reply)
    db.session.add(chat_entry)
    db.session.commit()

    return jsonify({"reply": reply})


@app.route("/order", methods=["POST"])
def place_order():
    data = request.json
    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    address = data.get("address", "").strip()
    items = data.get("items", "").strip()

    if not name or not phone or not items:
        return jsonify({"success": False, "message": "Please fill all required fields."})

    new_order = Order(
        customer_name=name,
        phone=phone,
        address=address,
        items=items
    )
    db.session.add(new_order)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"Shukriya {name}! Aapka order mil gaya. Hum jald contact karenge.",
        "order_id": new_order.id
    })


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        else:
            return render_template("login.html", error="Galat username ya password!")
    return render_template("login.html", error=None)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))


@app.route("/admin")
def admin():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    orders = Order.query.order_by(Order.timestamp.desc()).all()
    chats = Chat.query.order_by(Chat.timestamp.desc()).limit(50).all()
    return render_template("admin.html", orders=orders, chats=chats)


@app.route("/admin/order/<int:order_id>/<status>")
def update_order_status(order_id, status):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    order = Order.query.get(order_id)
    if order:
        order.status = status
        db.session.commit()
    return redirect(url_for("admin"))

# ---------- RUN ----------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)