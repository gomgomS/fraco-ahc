import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from flask import render_template, request, jsonify, redirect, send_file
import re
import sanitize
from support.support_proc import support_proc

def html_support():
    proc = support_proc()
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        result = proc.save_pledge(params)
        if result.get("status") == "SUCCESS":
            return redirect("/support?ok=1#pledge")
        # end if
        data = proc.get_support_page(
            form_error=result.get("desc") or "Could not submit",
            form_values={
                "name": params.get("name") or "",
                "phone": params.get("phone") or "",
                "commitment": params.get("commitment") or "",
                "referral_code": params.get("referral_code") or params.get("referred_by") or ""
            },
            form_field=result.get("field") or ""
        )
        return render_template("support.html", data=data)
    # end if
    form_ok = (request.args.get("ok") or "") == "1"
    data = proc.get_support_page(form_ok=form_ok)
    return render_template("support.html", data=data)
# end def

def api_check_referral():
    proc = support_proc()
    params = sanitize.clean_html_dic(request.args.to_dict())
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
    # end if
    result = proc.check_referral_code(params.get("referral_code") or params.get("code") or "")
    return jsonify({
        "message_action": result.get("status"),
        "message_desc": result.get("desc") or "",
        "message_data": {
            "valid": result.get("valid"),
            "empty": result.get("empty"),
            "code": result.get("code") or "",
            "referrer_name": result.get("referrer_name") or ""
        }
    })
# end def

def download_proposal_pdf():
    proc = support_proc()
    path = proc.resolve_proposal_pdf_path()
    if path == None:
        return "Not found", 404
    # end if
    settings = proc.get_settings()
    label = (settings.get("proposal_pdf_label") or "FRACO-proposal").strip()
    download_name = re.sub(r"[^a-zA-Z0-9._ -]", "", label)
    if download_name == "":
        download_name = "FRACO-proposal"
    # end if
    if download_name.lower().find(".pdf") < 0:
        download_name = download_name + ".pdf"
    # end if
    return send_file(path, mimetype="application/pdf", as_attachment=True, download_name=download_name)
# end def
