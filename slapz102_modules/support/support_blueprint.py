import sys
import traceback
from flask import Blueprint

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from view.support import view_support

support_blueprint = Blueprint("support_blueprint", __name__)

@support_blueprint.route("/support", methods=["GET", "POST"])
def support():
    try:
        return view_support.html_support()
    except Exception:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def

@support_blueprint.route("/support/proposal.pdf", methods=["GET"])
def support_proposal_pdf():
    try:
        return view_support.download_proposal_pdf()
    except Exception:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def

@support_blueprint.route("/support/check-referral", methods=["GET", "POST"])
def support_check_referral():
    try:
        return view_support.api_check_referral()
    except Exception:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def

@support_blueprint.route("/donate", methods=["GET", "POST"])
def donate():
    try:
        return view_support.html_support()
    except Exception:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def
