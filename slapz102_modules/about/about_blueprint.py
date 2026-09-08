import sys
import traceback
from flask import Blueprint

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from view.about import view_about

about_blueprint = Blueprint("about_blueprint", __name__)

@about_blueprint.route("/about", methods=["GET"])
def about():
    try:
        return view_about.html_about()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@about_blueprint.route("/about-us", methods=["GET"])
def about_us():
    try:
        return view_about.html_about()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def
