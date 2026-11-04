from CTFd.models import db


class Badges(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challenge = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False
    )
    url = db.Column(db.String(256), nullable=True)

    def __init__(self, challenge, url):
        self.challenge = challenge
        self.url = url

    def __repr__(self):
        return "<Badge %r> (chall=%r)" % (self.id, self.challenge)
