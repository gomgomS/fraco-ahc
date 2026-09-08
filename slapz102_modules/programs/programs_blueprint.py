import sys
import traceback
from flask import Blueprint

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from view.programs import view_programs

programs_blueprint = Blueprint("programs_blueprint", __name__)

@programs_blueprint.route("/programs", methods=["GET"])
def programs():
    try:
        return view_programs.html_programs()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@programs_blueprint.route("/programs/<slug>", methods=["GET"])
def program_detail(slug):
    try:
        return view_programs.html_program(slug)
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@programs_blueprint.route("/university-fair", methods=["GET"])
def university_fair():
    try:
        return view_programs.html_program("university-fair")
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@programs_blueprint.route("/university-fair/register", methods=["GET", "POST"])
def university_fair_register():
    try:
        return view_programs.html_register("university-fair")
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@programs_blueprint.route("/career-workshop", methods=["GET"])
def career_workshop():
    try:
        return view_programs.html_program("career-workshop")
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@programs_blueprint.route("/career-workshop/register", methods=["GET", "POST"])
def career_workshop_register():
    try:
        return view_programs.html_register("career-workshop")
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@programs_blueprint.route("/facility", methods=["GET"])
def facility():
    try:
        return view_programs.html_programs()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def
