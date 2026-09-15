import os
from flask import Flask, request

app = Flask(__name__)
DB_URL = os.environ.get("DATABASE_URL")  # TODO: fail hard when missing


@app.route("/login", methods=["POST"])
def login():
    user = request.form["user"]
    # TODO: parameterise this query
    query = f"SELECT * FROM users WHERE name = '{user}'"
    return query
