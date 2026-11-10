import sys
import traceback
from flask import Blueprint

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from view.tutorial import view_tutorial

tutorial_blueprint = Blueprint("tutorial_blueprint", __name__)

@tutorial_blueprint.route("/tutorials", methods=["GET"])
def tutorials():
    try:
        return view_tutorial.html_tutorials()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@tutorial_blueprint.route("/tutorials/<slug>", methods=["GET"])
def tutorial(slug):
    try:
        return view_tutorial.html_tutorial(slug)
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def
