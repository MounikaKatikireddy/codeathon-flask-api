from auth_utils import token_required
from permissions import roles_required
from flask import Blueprint, request, jsonify
from bson import ObjectId
from pymongo.errors import PyMongoError

from database import db

organisation_bp = Blueprint("organisations", __name__)


def serialize_organisation(organisation):
    """Convert MongoDB ObjectId into a JSON-friendly string."""
    organisation["_id"] = str(organisation["_id"])
    return organisation


@organisation_bp.route("/organisations", methods=["POST"])
@token_required
@roles_required("editor", "admin")
def create_organisation():
    if db is None:
        return jsonify({"error": "Database is not configured"}), 503

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    name = data.get("name")
    address = data.get("address")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Organisation name is required"}), 400

    if not isinstance(address, str) or not address.strip():
        return jsonify({"error": "Organisation address is required"}), 400

    organisation = {
        "name": name.strip(),
        "address": address.strip()
    }

    try:
        result = db.organisations.insert_one(organisation)
        organisation["_id"] = str(result.inserted_id)

        return jsonify({
            "message": "Organisation created successfully",
            "organisation": organisation
        }), 201

    except PyMongoError:
        return jsonify({"error": "Could not save organisation"}), 500


@organisation_bp.route("/organisations", methods=["GET"])
@token_required
@roles_required("viewer","editor", "admin")
def get_organisations():
    if db is None:
        return jsonify({"error": "Database is not configured"}), 503

    try:
        organisations = [
            serialize_organisation(item)
            for item in db.organisations.find()
        ]

        return jsonify({"organisations": organisations}), 200

    except PyMongoError:
        return jsonify({"error": "Could not retrieve organisations"}), 500



def is_valid_object_id(id):
    """Check whether a string is a valid MongoDB ObjectId."""
    return ObjectId.is_valid(id)


@organisation_bp.route("/organisations/<id>", methods=["GET"])
@token_required
@roles_required("viewer","editor", "admin")
def get_organisation(id):
    if db is None:
        return jsonify({"error": "Database is not configured"}), 503

    if not is_valid_object_id(id):
        return jsonify({"error": "Invalid organisation ID"}), 400

    try:
        organisation = db.organisations.find_one(
            {"_id": ObjectId(id)}
        )

        if organisation is None:
            return jsonify({"error": "Organisation not found"}), 404

        return jsonify({
            "organisation": serialize_organisation(organisation)
        }), 200

    except PyMongoError:
        return jsonify({"error": "Could not retrieve organisation"}), 500


@organisation_bp.route("/organisations/<id>", methods=["PUT"])
@token_required
@roles_required("editor", "admin")
def replace_organisation(id):
    if db is None:
        return jsonify({"error": "Database is not configured"}), 503

    if not is_valid_object_id(id):
        return jsonify({"error": "Invalid organisation ID"}), 400

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    name = data.get("name")
    address = data.get("address")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Organisation name is required"}), 400

    if not isinstance(address, str) or not address.strip():
        return jsonify({"error": "Organisation address is required"}), 400

    try:
        result = db.organisations.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "name": name.strip(),
                "address": address.strip()
            }}
        )

        if result.matched_count == 0:
            return jsonify({"error": "Organisation not found"}), 404

        organisation = db.organisations.find_one(
            {"_id": ObjectId(id)}
        )

        return jsonify({
            "message": "Organisation updated successfully",
            "organisation": serialize_organisation(organisation)
        }), 200

    except PyMongoError:
        return jsonify({"error": "Could not update organisation"}), 500


@organisation_bp.route("/organisations/<id>", methods=["PATCH"])
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

    allowed_fields = {"name", "address"}

    if not data or not set(data).issubset(allowed_fields):
        return jsonify({
            "error": "Provide name and/or address only"
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
        result = db.organisations.update_one(
            {"_id": ObjectId(id)},
            {"$set": updates}
        )

        if result.matched_count == 0:
            return jsonify({"error": "Organisation not found"}), 404

        organisation = db.organisations.find_one(
            {"_id": ObjectId(id)}
        )

        return jsonify({
            "message": "Organisation partially updated",
            "organisation": serialize_organisation(organisation)
        }), 200

    except PyMongoError:
        return jsonify({"error": "Could not update organisation"}), 500


@organisation_bp.route("/organisations/<id>", methods=["DELETE"])
@token_required
@roles_required("admin")
def delete_organisation(id):
    if db is None:
        return jsonify({"error": "Database is not configured"}), 503

    if not is_valid_object_id(id):
        return jsonify({"error": "Invalid organisation ID"}), 400

    try:
        result = db.organisations.delete_one(
            {"_id": ObjectId(id)}
        )

        if result.deleted_count == 0:
            return jsonify({"error": "Organisation not found"}), 404

        return jsonify({
            "message": "Organisation deleted successfully"
        }), 200

    except PyMongoError:
        return jsonify({"error": "Could not delete organisation"}), 500