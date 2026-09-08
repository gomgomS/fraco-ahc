import sys
import traceback
from flask import Blueprint

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from view.home import view_home

home_blueprint = Blueprint("home_blueprint", __name__)

@home_blueprint.route("/", methods=["GET"])
def index():
    try:
        return view_home.html_home()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@home_blueprint.route("/lang/<lang>", methods=["GET"])
def set_lang(lang):
    try:
        return view_home.html_set_lang(lang)
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def
