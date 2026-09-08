import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from flask import render_template, request, redirect
import sanitize
from programs.programs_proc import programs_proc

def html_programs():
    proc = programs_proc()
    data = proc.get_programs_page()
    return render_template("programs.html", data=data)
# end def

def html_program(slug):
    proc = programs_proc()
    data = proc.get_program_page(slug)
    if data == None:
        return "Program not found", 404
    # end if
    return render_template("program.html", data=data)
# end def

def html_register(slug):
    proc = programs_proc()
    data = proc.get_register_page(slug)
    if data == None:
        return "Program not found", 404
    # end if
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        result = proc.save_registration(slug, params)
        if result.get("status") == "SUCCESS":
            return redirect(request.path + "?ok=1")
        # end if
        data["form_error"] = result.get("desc", "Registration failed")
    # end if
    if request.args.get("ok") == "1":
        data["form_ok"] = True
    # end if
    return render_template("program_register.html", data=data)
# end def
