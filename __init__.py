from .src import badge, dates, downloads, fields, onesignal, rules, solves


def load(app):
    badge.load(app)
    dates.load(app)
    downloads.load(app)
    fields.load(app)
    onesignal.load(app)
    rules.load(app)
    solves.load(app)
