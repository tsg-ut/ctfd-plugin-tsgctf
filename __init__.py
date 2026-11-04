from .src import dates, downloads, fields, onesignal, rules


def load(app):
    dates.load(app)
    downloads.load(app)
    fields.load(app)
    onesignal.load(app)
    rules.load(app)
