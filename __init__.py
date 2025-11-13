from flask import send_file, jsonify
from werkzeug.utils import safe_join
from CTFd.models import Challenges, Solves, Pages, db
from CTFd.schemas.pages import PageSchema
from CTFd.utils import get_config
from CTFd.utils.modes import get_model
from CTFd.utils.dates import ctf_ended, ctf_started
from CTFd.utils.user import is_verified, is_admin
from CTFd.utils.decorators import during_ctf_time_only
from sqlalchemy.sql import and_
from .badge import onload as badge_onload, register_routes as badge_register_routes


def load(app):
    db.create_all()

    badge_onload(app)

    @app.route("/OneSignalSDKWorker.js", methods=["GET"])
    def worker():
        filename = safe_join(
            app.root_path, "themes", "tsgctf", "static", "OneSignalSDKWorker.js"
        )
        return send_file(filename)

    @app.route("/api/v1/dates", methods=["GET"])
    def dates():
        start = get_config("start")
        end = get_config("end")
        is_started = ctf_started()
        is_ended = ctf_ended()

        return jsonify(
            {
                "success": True,
                "data": {
                    "start": start,
                    "end": end,
                    "is_started": is_started,
                    "is_ended": is_ended,
                    "is_verified": is_verified() or is_admin(),
                },
            }
        )

    @app.route("/api/v1/rules", methods=["GET"])
    def rules():
        page = Pages.query.filter_by(route="rules", auth_required=False).first_or_404()
        schema = PageSchema()
        response = schema.dump(page)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @app.route("/api/v1/challenges/solves", methods=["GET"])
    @during_ctf_time_only
    def solves():
        chals = (
            Challenges.query.filter(
                and_(Challenges.state != "hidden", Challenges.state != "locked")
            )
            .order_by(Challenges.value)
            .all()
        )

        Model = get_model()

        solves_sub = (
            db.session.query(
                Solves.challenge_id, db.func.count(Solves.challenge_id).label("solves")
            )
            .join(Model, Solves.account_id == Model.id)
            .filter(Model.banned == False, Model.hidden == False)
            .group_by(Solves.challenge_id)
            .subquery()
        )

        solves = (
            db.session.query(
                solves_sub.columns.challenge_id,
                solves_sub.columns.solves,
                Challenges.name,
            )
            .join(Challenges, solves_sub.columns.challenge_id == Challenges.id)
            .all()
        )

        response = []
        has_solves = []

        for challenge_id, count, name in solves:
            challenge = {"id": challenge_id, "name": name, "solves": count}
            response.append(challenge)
            has_solves.append(challenge_id)
        for c in chals:
            if c.id not in has_solves:
                challenge = {"id": c.id, "name": c.name, "solves": 0}
                response.append(challenge)

        db.session.close()
        return {"success": True, "data": response}

    badge_register_routes(app)
