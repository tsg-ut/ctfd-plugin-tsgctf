from flask import request
from CTFd.models import db
from CTFd.utils.plugins import register_admin_script
from CTFd.plugins import register_plugin_assets_directory
from CTFd.utils.decorators import admins_only
from .model import Badges


def onload(app):
    register_plugin_assets_directory(app, base_path="/plugins/tsgctf/assets/")
    register_admin_script("/plugins/tsgctf/assets/badge.js")


def register_routes(app):
    @app.route("/api/v1/challenges/<challenge>/badge", methods=["GET"])
    def get_badge(challenge):
        try:
            challenge_i = int(challenge)
        except ValueError:
            return {"success": False, "errors": "Invalid challenge ID"}, 400
        badge = Badges.query.filter_by(challenge=challenge_i).first_or_404()
        return {"success": True, "badge_url": badge.url}

    @app.route("/api/v1/challenges/<challenge>/badge", methods=["POST"])
    @admins_only
    def create_badge(challenge):
        try:
            challenge_i = int(challenge)
        except ValueError:
            return {"success": False, "errors": "Invalid challenge ID"}, 400
        badge_url = request.get_json().get("badge_url")
        badge_url = badge_url.split(" ")[0]
        if len(badge_url) == 0:
            badge_url = None

        db.session.add(Badges(challenge_i, badge_url))
        db.session.commit()
        db.session.close()
        return {"success": True}

    @app.route("/api/v1/challenges/<challenge>/badge", methods=["PATCH"])
    @admins_only
    def patch_badge(challenge):
        try:
            challenge_i = int(challenge)
        except ValueError:
            return {"success": False, "errors": "Invalid challenge ID"}, 400
        print(request.get_json())
        badge_url = request.get_json().get("badge_url")
        badge_url = badge_url.split(" ")[0]
        if len(badge_url) == 0:
            badge_url = None

        badge = Badges.query.filter_by(challenge=challenge_i).first_or_404()
        badge.url = badge_url
        db.session.commit()
        db.session.close()
        return {"success": True}
