import sys
import traceback
from flask import Blueprint, send_from_directory
from slapz102_core import config
import os

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

@home_blueprint.route("/favicon.ico", methods=["GET"])
def favicon():
    try:
        brand_dir = os.path.join(config.G_HOME_PATH, "static", "brand")
        return send_from_directory(brand_dir, "fraco-og.jpg", mimetype="image/jpeg")
    except Exception as e:
        print(traceback.format_exc())
        return "Not found", 404
    # end try
# end def

@home_blueprint.route("/lang/<lang>", methods=["GET"])
def set_lang(lang):
    try:
        return view_home.html_set_lang(lang)
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def
