from flask import Blueprint


restaurant_bp = Blueprint("restaurant", __name__, url_prefix="/restaurant")


@restaurant_bp.route("/dashboard")
def dashboard():
    return "Restaurant dashboard (to be implemented)"
