from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ------------------ DATA ------------------

authors = [
    {
        "id": 1,
        "name": "Priya Sharma",
        "email": "priya@email.com",
        "bank_account": "1234567890",
        "ifsc": "HDFC0001234"
    },
    {
        "id": 2,
        "name": "Rahul Verma",
        "email": "rahul@email.com",
        "bank_account": "0987654321",
        "ifsc": "ICIC0005678"
    },
    {
        "id": 3,
        "name": "Anita Desai",
        "email": "anita@email.com",
        "bank_account": "5678901234",
        "ifsc": "SBIN0009012"
    }
]

books = [
    {"id": 1, "title": "The Silent River", "author_id": 1, "royalty": 45},
    {"id": 2, "title": "Midnight in Mumbai", "author_id": 1, "royalty": 60},
    {"id": 3, "title": "Code & Coffee", "author_id": 2, "royalty": 75},
    {"id": 4, "title": "Startup Diaries", "author_id": 2, "royalty": 50},
    {"id": 5, "title": "Poetry of Pain", "author_id": 2, "royalty": 30},
    {"id": 6, "title": "Garden of Words", "author_id": 3, "royalty": 40}
]

sales = [
    {"book_id": 1, "qty": 25, "date": "2025-01-05"},
    {"book_id": 1, "qty": 40, "date": "2025-01-12"},
    {"book_id": 2, "qty": 15, "date": "2025-01-08"},
    {"book_id": 3, "qty": 60, "date": "2025-01-03"},
    {"book_id": 3, "qty": 45, "date": "2025-01-15"},
    {"book_id": 4, "qty": 30, "date": "2025-01-10"},
    {"book_id": 5, "qty": 20, "date": "2025-01-18"},
    {"book_id": 6, "qty": 10, "date": "2025-01-20"}
]

withdrawals = []

# ------------------ HELPERS ------------------

def calculate_total_earnings(author_id):
    total = 0
    for book in books:
        if book["author_id"] == author_id:
            for sale in sales:
                if sale["book_id"] == book["id"]:
                    total += sale["qty"] * book["royalty"]
    return total

def calculate_withdrawn(author_id):
    return sum(w["amount"] for w in withdrawals if w["author_id"] == author_id)

# ------------------ ROUTES ------------------

@app.route("/")
def home():
    return jsonify({"message": "API is running"})

# 1️⃣ GET /authors
@app.route("/authors", methods=["GET"])
def get_authors():
    result = []

    for author in authors:
        total_earnings = calculate_total_earnings(author["id"])
        withdrawn = calculate_withdrawn(author["id"])

        result.append({
            "id": author["id"],
            "name": author["name"],
            "total_earnings": total_earnings,
            "current_balance": total_earnings - withdrawn
        })

    return jsonify(result)

# 2️⃣ GET /authors/<id>
@app.route("/authors/<int:author_id>", methods=["GET"])
def get_author(author_id):
    author = next((a for a in authors if a["id"] == author_id), None)
    if not author:
        return jsonify({"error": "Author not found"}), 404

    author_books = []
    total_earnings = 0

    for book in books:
        if book["author_id"] == author_id:
            total_sold = 0
            total_royalty = 0

            for sale in sales:
                if sale["book_id"] == book["id"]:
                    total_sold += sale["qty"]
                    total_royalty += sale["qty"] * book["royalty"]

            total_earnings += total_royalty

            author_books.append({
                "id": book["id"],
                "title": book["title"],
                "royalty_per_sale": book["royalty"],
                "total_sold": total_sold,
                "total_royalty": total_royalty
            })

    withdrawn = calculate_withdrawn(author_id)

    return jsonify({
        "id": author["id"],
        "name": author["name"],
        "email": author["email"],
        "total_books": len(author_books),
        "total_earnings": total_earnings,
        "current_balance": total_earnings - withdrawn,
        "books": author_books
    })

# 3️⃣ GET /authors/<id>/sales
@app.route("/authors/<int:author_id>/sales", methods=["GET"])
def get_author_sales(author_id):
    author_books = [b for b in books if b["author_id"] == author_id]
    if not author_books:
        return jsonify({"error": "Author not found"}), 404

    sales_list = []

    for sale in sales:
        for book in author_books:
            if sale["book_id"] == book["id"]:
                sales_list.append({
                    "book_title": book["title"],
                    "quantity": sale["qty"],
                    "royalty_earned": sale["qty"] * book["royalty"],
                    "sale_date": sale["date"]
                })

    sales_list.sort(key=lambda x: x["sale_date"], reverse=True)
    return jsonify(sales_list)

# 4️⃣ POST /withdrawals
@app.route("/withdrawals", methods=["POST"])
def create_withdrawal():
    data = request.json
    author_id = data.get("author_id")
    amount = data.get("amount")

    author = next((a for a in authors if a["id"] == author_id), None)
    if not author:
        return jsonify({"error": "Author not found"}), 404

    if amount < 500:
        return jsonify({"error": "Minimum withdrawal is 500"}), 400

    total_earnings = calculate_total_earnings(author_id)
    withdrawn = calculate_withdrawn(author_id)
    balance = total_earnings - withdrawn

    if amount > balance:
        return jsonify({"error": "Amount exceeds current balance"}), 400

    withdrawal = {
        "id": len(withdrawals) + 1,
        "author_id": author_id,
        "amount": amount,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }

    withdrawals.append(withdrawal)

    return jsonify({
        "message": "Withdrawal created",
        "withdrawal": withdrawal,
        "new_balance": balance - amount
    }), 201

# 5️⃣ GET /authors/<id>/withdrawals
@app.route("/authors/<int:author_id>/withdrawals", methods=["GET"])
def get_withdrawals(author_id):
    result = [w for w in withdrawals if w["author_id"] == author_id]
    result.sort(key=lambda x: x["created_at"], reverse=True)
    return jsonify(result)

# ------------------ RUN ------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)