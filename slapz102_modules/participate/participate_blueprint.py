import sys
import traceback
from flask import Blueprint

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from view.participate import view_participate

participate_blueprint = Blueprint("participate_blueprint", __name__)

@participate_blueprint.route("/participate", methods=["GET"])
def participate():
    try:
        return view_participate.html_participate()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@participate_blueprint.route("/register", methods=["GET", "POST"])
def register():
    try:
        return view_participate.html_register()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@participate_blueprint.route("/participate/register", methods=["GET", "POST"])
def participate_register():
    try:
        return view_participate.html_register()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@participate_blueprint.route("/register/<reg_id>", methods=["GET"])
def registration(reg_id):
    try:
        return view_participate.html_registration(reg_id)
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def
