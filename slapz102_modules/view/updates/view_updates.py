import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from flask import render_template, request
from updates.updates_proc import updates_proc

def html_updates():
    proc = updates_proc()
    data = proc.get_updates_page((request.args.get("category") or "").strip())
    return render_template("updates.html", data=data)
# end def

def html_article(slug):
    proc = updates_proc()
    data = proc.get_article_page(slug)
    if data == None:
        return "Update not found", 404
    # end if
    return render_template("update.html", data=data)
# end def

def html_gallery():
    proc = updates_proc()
    data = proc.get_gallery_page((request.args.get("album") or "").strip())
    return render_template("gallery.html", data=data)
# end def
