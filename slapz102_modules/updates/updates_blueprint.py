import sys
import traceback
from flask import Blueprint

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from view.updates import view_updates

updates_blueprint = Blueprint("updates_blueprint", __name__)

@updates_blueprint.route("/updates", methods=["GET"])
def updates():
    try:
        return view_updates.html_updates()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@updates_blueprint.route("/updates/<slug>", methods=["GET"])
def article(slug):
    try:
        return view_updates.html_article(slug)
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@updates_blueprint.route("/news", methods=["GET"])
def news():
    try:
        return view_updates.html_updates()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@updates_blueprint.route("/gallery", methods=["GET"])
def gallery():
    try:
        return view_updates.html_gallery()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def
