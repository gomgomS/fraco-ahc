import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from flask import render_template, redirect, request, make_response
from home.home_proc import home_proc

def html_home():
    proc = home_proc()
    data = proc.get_home()
    return render_template("index.html", data=data)
# end def

def html_set_lang(lang):
    clean = (lang or "").strip().lower()
    if clean not in ["en", "id"]:
        clean = "en"
    # end if
    nxt = (request.args.get("next") or "/").strip()
    if not nxt.startswith("/"):
        nxt = "/"
    # end if
    if nxt.startswith("//") or nxt.startswith("/admin"):
        nxt = "/"
    # end if
    resp = make_response(redirect(nxt))
    resp.set_cookie("fraco_lang", clean, max_age=60 * 60 * 24 * 365, samesite="Lax")
    return resp
# end def
