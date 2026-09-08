import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from flask import render_template, request, redirect
import sanitize
from participate.participate_proc import participate_proc

def html_participate():
    proc = participate_proc()
    data = proc.get_participate_page()
    return render_template("participate.html", data=data)
# end def

def html_register():
    proc = participate_proc()
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        params["password"] = request.form.get("password") or ""
        params["password_confirm"] = request.form.get("password_confirm") or ""
        result = proc.save_registration(params)
        if result.get("status") == "SUCCESS":
            return redirect("/register/" + result.get("reg_id"))
        # end if
        data = proc.get_register_page(
            result.get("desc", ""),
            params,
            params.get("member_type") or ""
        )
        return render_template("register.html", data=data)
    # end if
    member_type = (request.args.get("as") or "").strip().upper()
    data = proc.get_register_page("", {}, member_type)
    return render_template("register.html", data=data)
# end def

def html_registration(reg_id):
    proc = participate_proc()
    data = proc.get_registration_page(reg_id)
    if data == None:
        return "Registration not found", 404
    # end if
    return render_template("registration.html", data=data)
# end def
