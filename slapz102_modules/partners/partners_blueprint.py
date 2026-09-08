import sys
import traceback
from flask import Blueprint

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from view.partners import view_partners

partners_blueprint = Blueprint("partners_blueprint", __name__)

@partners_blueprint.route("/partners", methods=["GET"])
def partners():
    try:
        return view_partners.html_partners()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@partners_blueprint.route("/sponsorship", methods=["GET"])
def sponsorship():
    try:
        return view_partners.html_sponsorship()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@partners_blueprint.route("/sponsorship/apply", methods=["GET", "POST"])
def sponsorship_apply():
    try:
        return view_partners.html_sponsor_apply()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@partners_blueprint.route("/vendors", methods=["GET"])
def vendors():
    try:
        return view_partners.html_vendors()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@partners_blueprint.route("/vendor/register", methods=["GET", "POST"])
def vendor_register():
    try:
        return view_partners.html_vendor_apply()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@partners_blueprint.route("/partners/sponsorship", methods=["GET"])
def partners_sponsorship():
    try:
        return view_partners.html_sponsorship()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@partners_blueprint.route("/partners/sponsorship/apply", methods=["GET", "POST"])
def partners_sponsorship_apply():
    try:
        return view_partners.html_sponsor_apply()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@partners_blueprint.route("/contact", methods=["GET"])
def contact():
    try:
        return view_partners.html_contact()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def
