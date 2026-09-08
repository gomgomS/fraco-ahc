import sys
import traceback
from flask import Blueprint

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from view.merchandise import view_merchandise

merchandise_blueprint = Blueprint("merchandise_blueprint", __name__)

@merchandise_blueprint.route("/merchandise", methods=["GET"])
def merchandise():
    try:
        return view_merchandise.html_merchandise()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@merchandise_blueprint.route("/merchandise/<slug>", methods=["GET"])
def product_detail(slug):
    try:
        return view_merchandise.html_product(slug)
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@merchandise_blueprint.route("/properti", methods=["GET"])
def properti():
    try:
        return view_merchandise.html_merchandise()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def
