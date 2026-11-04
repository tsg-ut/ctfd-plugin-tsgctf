from CTFd.models import Pages
from CTFd.schemas.pages import PageSchema


def load(app):
    @app.route("/api/v1/rules", methods=["GET"])
    def rules():
        page = (
            Pages.query.filter_by(route="rules", auth_required=False)
            .filter(Pages.draft.isnot(True))
            .first_or_404()
        )
        schema = PageSchema()
        response = schema.dump(page)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}
