from routes.organisation_routes import organisation_bp
from routes.employee_routes import employee_bp
from routes.auth_routes import auth_bp

from flask import Flask, jsonify

from database import db, MONGO_DB, check_database_connection

app = Flask(__name__)

app.register_blueprint(organisation_bp)
app.register_blueprint(employee_bp)
app.register_blueprint(auth_bp)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "CodeAthon API is running!"
    }), 200


@app.route("/health", methods=["GET"])
def health_check():
    if check_database_connection():
        return jsonify({
            "status": "healthy",
            "database": MONGO_DB,
            "mongodb": "connected"
        }), 200

    return jsonify({
        "status": "error",
        "message": "MongoDB connection failed"
    }), 503


if __name__ == "__main__":
    app.run(debug=True)