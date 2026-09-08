import sys
import traceback
from flask import Blueprint

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from view.dashboard import view_dashboard

dashboard_blueprint = Blueprint("dashboard_blueprint", __name__)

@dashboard_blueprint.route("/login", methods=["GET", "POST"])
def login():
    try:
        return view_dashboard.html_login()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@dashboard_blueprint.route("/logout", methods=["GET"])
def logout():
    try:
        return view_dashboard.html_logout()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@dashboard_blueprint.route("/dashboard", methods=["GET"])
def overview():
    try:
        return view_dashboard.html_overview()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@dashboard_blueprint.route("/dashboard/registration", methods=["GET"])
def registration():
    try:
        return view_dashboard.html_registration()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@dashboard_blueprint.route("/dashboard/orders", methods=["GET", "POST"])
def orders():
    try:
        return view_dashboard.html_orders()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@dashboard_blueprint.route("/dashboard/orders/<order_ref>", methods=["GET", "POST"])
def order_detail(order_ref):
    try:
        return view_dashboard.html_order_detail(order_ref)
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@dashboard_blueprint.route("/dashboard/proposal", methods=["GET", "POST"])
def proposal():
    try:
        return view_dashboard.html_proposal()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@dashboard_blueprint.route("/dashboard/events", methods=["GET"])
def events():
    try:
        return view_dashboard.html_events()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@dashboard_blueprint.route("/dashboard/profile", methods=["GET", "POST"])
def profile():
    try:
        return view_dashboard.html_profile()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def
