from auth_utils import token_required
from permissions import roles_required
from flask import Blueprint, request, jsonify
from bson import ObjectId
from pymongo.errors import PyMongoError

from database import db

employee_bp = Blueprint("employees", __name__)


def serialize_employee(employee):
    employee["_id"] = str(employee["_id"])
    employee["organisation_id"] = str(
        employee["organisation_id"]
    )
    return employee


@employee_bp.route("/employees", methods=["POST"])
@token_required
@roles_required("editor", "admin")
def create_employee():
    if db is None:
        return jsonify({"error": "Database is not configured"}), 503

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    name = data.get("name")
    email = data.get("email")
    organisation_id = data.get("organisation_id")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Employee name is required"}), 400

    if not isinstance(email, str) or not email.strip():
        return jsonify({"error": "Employee email is required"}), 400

    if not isinstance(organisation_id, str) or not ObjectId.is_valid(organisation_id):
        return jsonify({"error": "Invalid organisation ID"}), 400

    try:
        organisation = db.organisations.find_one({
            "_id": ObjectId(organisation_id)
        })

        if organisation is None:
            return jsonify({"error": "Organisation not found"}), 404

        employee = {
            "name": name.strip(),
            "email": email.strip(),
            "organisation_id": ObjectId(organisation_id)
        }

        result = db.employees.insert_one(employee)
        employee["_id"] = result.inserted_id

        return jsonify({
            "message": "Employee created successfully",
            "employee": serialize_employee(employee)
        }), 201

    except PyMongoError:
        return jsonify({"error": "Could not save employee"}), 500


@employee_bp.route("/employees", methods=["GET"])
@token_required
@roles_required("viewer","editor", "admin")
def get_employees():
    if db is None:
        return jsonify({"error": "Database is not configured"}), 503

    try:
        employees = [
            serialize_employee(employee)
            for employee in db.employees.find()
        ]

        return jsonify({"employees": employees}), 200

    except PyMongoError:
        return jsonify({"error": "Could not retrieve employees"}), 500


def is_valid_object_id(id):
    """Check whether a string is a valid MongoDB ObjectId."""
    return ObjectId.is_valid(id)


@employee_bp.route("/employees/<id>", methods=["PUT"])
@token_required
@roles_required("editor", "admin")
def replace_employee(id):
    if db is None:
        return jsonify({"error": "Database is not configured"}), 503

    if not is_valid_object_id(id):
        return jsonify({"error": "Invalid  ID"}), 400

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    name = data.get("name")
    email = data.get("email")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "employee name is required"}), 400

    if not isinstance(email, str) or not email.strip():
        return jsonify({"error": "employee email is required"}), 400


    try:
        result = db.employees.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "name": name.strip(),
                "email": email.strip()
            }}
        )

        if result.matched_count == 0:
            return jsonify({"error": "employee not found"}), 404

        employee = db.employees.find_one(
            {"_id": ObjectId(id)}
        )

        return jsonify({
            "message": "employee updated successfully",
            "employee": serialize_employee(employee)
        }), 200

    except PyMongoError:
        return jsonify({"error": "Could not update employee"}), 500


@employee_bp.route("/employees/<id>", methods=["PATCH"])
@token_required
@roles_required("editor", "admin")
def update_organisation(id):
    if db is None:
        return jsonify({"error": "Database is not configured"}), 503

    if not is_valid_object_id(id):
        return jsonify({"error": "Invalid organisation ID"}), 400

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    allowed_fields = {"name", "email"}

    if not data or not set(data).issubset(allowed_fields):
        return jsonify({
            "error": "Provide name , email and/or organisation_id only"
        }), 400

    updates = {}

    for field in allowed_fields.intersection(data):
        value = data[field]

        if not isinstance(value, str) or not value.strip():
            return jsonify({
                "error": f"{field} must be a non-empty string"
            }), 400

        updates[field] = value.strip()

    try:
        result = db.employees.update_one(
            {"_id": ObjectId(id)},
            {"$set": updates}
        )

        if result.matched_count == 0:
            return jsonify({"error": "Employee not found "}), 404

        employee = db.employees.find_one(
            {"_id": ObjectId(id)}
        )

        return jsonify({
            "message": "Employee partially updated",
            "employee": serialize_employee(employee)
        }), 200

    except PyMongoError:
        return jsonify({"error": "Could not update organisation"}), 500

@employee_bp.route("/employees/<id>", methods=["DELETE"])
@token_required
@roles_required("admin")
def delete_employee(id):
    if db is None:
        return jsonify({"error": "Database is not configured"}), 503

    if not is_valid_object_id(id):
        return jsonify({"error": "Invalid organisation ID"}), 400

    try:
        result = db.employees.delete_one(
            {"_id": ObjectId(id)}
        )

        if result.deleted_count == 0:
            return jsonify({"error": "Employee not found"}), 404

        return jsonify({
            "message": "Employee deleted successfully"
        }), 200

    except PyMongoError:
        return jsonify({"error": "Could not delete Employee"}), 500