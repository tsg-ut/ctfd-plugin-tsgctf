from .src import dates, downloads, rules


def load(app):
    dates.load(app)
    downloads.load(app)
    rules.load(app)
