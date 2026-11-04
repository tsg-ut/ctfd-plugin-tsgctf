from .src import badge, dates, fields, onesignal, rules, solves


def load(app):
    badge.load(app)
    dates.load(app)
    fields.load(app)
    onesignal.load(app)
    rules.load(app)
    solves.load(app)
