from flask import Blueprint, jsonify

api = Blueprint(
    "api",
    __name__,
    url_prefix="/api"
)


@api.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "success",
        "message": "API Working"
    })