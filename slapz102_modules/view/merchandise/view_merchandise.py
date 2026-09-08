import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from flask import render_template, request
from merchandise.merchandise_proc import merchandise_proc
from slapz102_stdlib import sanitize

def html_merchandise():
    proc = merchandise_proc()
    category = sanitize.clean_html(request.args.get("category") or "")
    query = sanitize.clean_html(request.args.get("q") or "")
    track_code = sanitize.clean_html(request.args.get("track") or "")
    data = proc.get_merchandise_page(category, query, track_code)
    return render_template("merchandise.html", data=data)
# end def

def html_product(slug):
    proc = merchandise_proc()
    data = proc.get_product_page(slug)
    if data == None:
        return "Product not found", 404
    # end if
    return render_template("product.html", data=data)
# end def
