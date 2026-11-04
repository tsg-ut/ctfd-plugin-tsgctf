from flask import jsonify, request

from CTFd.models import TeamFields, UserFields
from CTFd.schemas.fields import FieldSchema


def load(app):
    @app.route("/api/v1/fields", methods=["GET"])
    def list_fields():
        t = (request.args.get("type") or "").lower()

        if t == "teams":
            q = TeamFields.query
        elif t == "users":
            q = UserFields.query
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "data": None,
                        "errors": {"type": "Missing or invalid ?type (teams|users)"},
                    }
                ),
                400,
            )

        fields = q.all()

        schema = FieldSchema(
            many=True,
            only=("id", "name", "field_type", "description", "required"),
        )
        response = schema.dump(fields)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return jsonify({"success": True, "data": response.data})
