from functools import wraps

from flask import abort, request

from CTFd.constants.config import ChallengeVisibilityTypes
from CTFd.models import ChallengeFiles, Challenges, Users
from CTFd.utils import get_config
from CTFd.utils.challenges import get_solve_ids_for_user_id
from CTFd.utils.config.visibility import challenges_visible
from CTFd.utils.dates import ctf_ended, ctftime, view_after_ctf
from CTFd.utils.security.signing import (
    BadSignature,
    BadTimeSignature,
    SignatureExpired,
    unserialize,
)
from CTFd.utils.user import get_current_user


def _can_access_challenge(challenge, user):
    # Released CTFd 3.8.9 does not have module access or scheduled releases.
    if not hasattr(Challenges, "module_id"):
        return True

    from CTFd.utils.modules import can_access_challenge

    return can_access_challenge(challenge, user)


def _get_download_user(file):
    if challenges_visible():
        return get_current_user()

    # Match the identity used by CTFd for cookie-free, token-based downloads.
    try:
        data = unserialize(request.args.get("token", ""), max_age=3600)
    except (BadTimeSignature, SignatureExpired, BadSignature):
        abort(403)
    if not isinstance(data, dict) or data.get("file_id") != file.id:
        abort(403)

    user = Users.query.filter_by(id=data.get("user_id")).first()
    if user is None:
        abort(403)
    return user


def _prerequisites_met(challenge, user):
    requirements = (challenge.requirements or {}).get("prerequisites", [])
    if not requirements:
        return True

    # Like the challenge API, ignore references to challenges that were deleted.
    prerequisites = {
        challenge_id
        for (challenge_id,) in Challenges.query.with_entities(Challenges.id)
        .filter(Challenges.id.in_(requirements))
        .all()
    }
    solve_ids = get_solve_ids_for_user_id(user.id) if user is not None else set()
    return solve_ids >= prerequisites


def load(app):
    original_files = app.view_functions["views.files"]

    @wraps(original_files)
    def files(path):
        file = ChallengeFiles.query.filter_by(location=path).first()
        if file is not None:
            user = _get_download_user(file)
            if user is None or user.type != "admin":
                challenge = file.challenge
                if challenge.state != "visible":
                    abort(404)
                if not (ctftime() or (ctf_ended() and view_after_ctf())):
                    abort(403)
                if not _can_access_challenge(challenge, user):
                    abort(404)
                if not _prerequisites_met(challenge, user):
                    abort(403)

        # Keep CTFd's authentication, other file types, and uploader behavior.
        return original_files(path)

    app.view_functions["views.files"] = files

    @app.url_defaults
    def remove_public_file_token(endpoint, values):
        if endpoint != "views.files" or "token" not in values:
            return
        if get_config("challenge_visibility") != ChallengeVisibilityTypes.PUBLIC:
            return
        if not (ctftime() or (ctf_ended() and view_after_ctf())):
            return

        file = ChallengeFiles.query.filter_by(location=values.get("path")).first()
        if file is None:
            return

        challenge = file.challenge
        if challenge.state != "visible" or not _can_access_challenge(challenge, None):
            return
        if not _prerequisites_met(challenge, None):
            return

        values.pop("token")
