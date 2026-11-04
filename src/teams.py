from flask import Blueprint, has_request_context, request
from sqlalchemy import event

from CTFd.models import Teams, db
from CTFd.utils import get_config


def hide_new_teams(session, flush_context, instances):
    if not has_request_context():
        return
    if request.endpoint != "teams.new" or request.method != "POST":
        return
    if not get_config("tsgctf_hide_new_teams", default=False):
        return

    for team in session.new:
        if isinstance(team, Teams):
            team.hidden = True


def load(app):
    app.register_blueprint(
        Blueprint("tsgctf_teams", __name__, template_folder="../templates")
    )
    if not event.contains(db.session, "before_flush", hide_new_teams):
        event.listen(db.session, "before_flush", hide_new_teams)
