import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from flask import render_template, request, redirect
import sanitize
from partners.partners_proc import partners_proc

def html_partners():
    proc = partners_proc()
    data = proc.get_partners_page()
    return render_template("partners.html", data=data)
# end def

def html_contact():
    proc = partners_proc()
    data = proc.get_partners_page()
    return render_template("contact.html", data=data)
# end def

def html_sponsorship():
    proc = partners_proc()
    data = proc.get_sponsorship_page()
    return render_template("sponsorship.html", data=data)
# end def

def html_vendors():
    proc = partners_proc()
    data = proc.get_vendors_page()
    return render_template("vendors.html", data=data)
# end def

def html_sponsor_apply():
    proc = partners_proc()
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        file_obj = request.files.get("attachment")
        result = proc.save_sponsor(params, file_obj)
        if result.get("status") == "SUCCESS":
            return redirect("/sponsorship/apply?ok=1")
        # end if
        data = proc.get_apply_page("sponsor", result.get("desc", ""))
        return render_template("partner_apply.html", data=data)
    # end if
    data = proc.get_apply_page("sponsor", ok=(request.args.get("ok") == "1"))
    return render_template("partner_apply.html", data=data)
# end def

def html_vendor_apply():
    proc = partners_proc()
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        file_obj = request.files.get("attachment")
        result = proc.save_vendor(params, file_obj)
        if result.get("status") == "SUCCESS":
            return redirect("/vendor/register?ok=1")
        # end if
        data = proc.get_apply_page("vendor", result.get("desc", ""))
        return render_template("partner_apply.html", data=data)
    # end if
    data = proc.get_apply_page("vendor", ok=(request.args.get("ok") == "1"))
    return render_template("partner_apply.html", data=data)
# end def
