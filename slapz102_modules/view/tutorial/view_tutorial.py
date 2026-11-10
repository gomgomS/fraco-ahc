import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from flask import render_template
import sanitize
from ahc_site.ahc_site_proc import ahc_site_proc
from tutorial.tutorial_proc import tutorial_proc

def html_tutorials():
    site = ahc_site_proc()
    tut = tutorial_proc()
    data = site.with_site({
        "tutorials": tut.list_published(),
        "share_title": "Tutorials | FRACO",
        "share_description": "Step-by-step guides from the FRACO team.",
        "share_url": "/tutorials"
    })
    return render_template("tutorials.html", data=data)
# end def

def html_tutorial(slug):
    site = ahc_site_proc()
    tut = tutorial_proc()
    rec = tut.get_published(slug)
    if rec == None:
        return "Tutorial not found", 404
    # end if
    extra = {
        "tutorial": rec,
        "content_html": sanitize.clean_rich_html(rec.get("content") or ""),
        "share_title": (rec.get("title") or "Tutorial") + " | FRACO",
        "share_description": rec.get("excerpt") or "",
        "share_url": "/tutorials/" + (rec.get("slug") or "")
    }
    if (rec.get("cover_image") or "") != "":
        extra["share_image"] = rec.get("cover_image")
    # end if
    data = site.with_site(extra)
    return render_template("tutorial.html", data=data)
# end def
