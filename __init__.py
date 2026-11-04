from .src import dates, downloads, onesignal, rules


def load(app):
    dates.load(app)
    downloads.load(app)
    onesignal.load(app)
    rules.load(app)
