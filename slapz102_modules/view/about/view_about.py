import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from flask import render_template
from about.about_proc import about_proc

def html_about():
    proc = about_proc()
    data = proc.get_about()
    return render_template("about.html", data=data)
# end def
