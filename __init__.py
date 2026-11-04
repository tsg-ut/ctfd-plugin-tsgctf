from .src import dates, downloads, rules, teams


def load(app):
    dates.load(app)
    downloads.load(app)
    rules.load(app)
    teams.load(app)
