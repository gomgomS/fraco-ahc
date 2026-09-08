import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from flask import render_template, request, redirect
import sanitize
from dashboard.dashboard_proc import dashboard_proc

def _safe_next():
    nxt = (request.args.get("next") or request.form.get("next") or "/dashboard").strip()
    allowed = [
        "/dashboard",
        "/dashboard/orders",
        "/dashboard/proposal",
        "/dashboard/events",
        "/dashboard/profile"
    ]
    if nxt not in allowed and not nxt.startswith("/dashboard/orders/"):
        nxt = "/dashboard"
    # end if
    return nxt
# end def

def _need_login():
    proc = dashboard_proc()
    if proc.current_user() == None:
        return redirect("/login?next=" + request.path)
    # end if
    return None
# end def

def html_login():
    proc = dashboard_proc()
    if proc.current_user() != None:
        return redirect(_safe_next())
    # end if
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        raw = request.form.get("password") or ""
        result = proc.login(params, raw)
        if result.get("status") == "SUCCESS":
            return redirect(_safe_next())
        # end if
        data = proc.get_login_page(result.get("desc", ""), _safe_next())
        return render_template("login.html", data=data)
    # end if
    data = proc.get_login_page("", _safe_next())
    return render_template("login.html", data=data)
# end def

def html_logout():
    proc = dashboard_proc()
    proc.logout_user()
    return redirect("/")
# end def

def html_overview():
    gate = _need_login()
    if gate != None:
        return gate
    # end if
    proc = dashboard_proc()
    data = proc.base_data("overview")
    return render_template("dashboard.html", data=data)
# end def

def html_registration():
    gate = _need_login()
    if gate != None:
        return gate
    # end if
    proc = dashboard_proc()
    data = proc.base_data("registration")
    return render_template("dashboard_registration.html", data=data)
# end def

def html_orders():
    gate = _need_login()
    if gate != None:
        return gate
    # end if
    proc = dashboard_proc()
    status_filter = (request.args.get("status") or "").strip()
    payment_filter = (request.args.get("pay") or "").strip()
    contact_q = (request.args.get("q") or "").strip()
    if status_filter == "ALL":
        status_filter = ""
    # end if
    if payment_filter == "ALL":
        payment_filter = ""
    # end if
    extra = {
        "order_status_filter": status_filter,
        "payment_status_filter": payment_filter,
        "order_contact_q": contact_q
    }
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        result = proc.update_referral_order(params)
        if result.get("status") == "SUCCESS":
            q_parts = []
            if status_filter != "":
                q_parts.append("status=" + status_filter)
            # end if
            if payment_filter != "":
                q_parts.append("pay=" + payment_filter)
            # end if
            if contact_q != "":
                from urllib.parse import quote
                q_parts.append("q=" + quote(contact_q))
            # end if
            q_parts.append("ok=1")
            return redirect("/dashboard/orders?" + "&".join(q_parts))
        # end if
        data = proc.base_data("orders", extra)
        if not data.get("is_ahc_member"):
            return redirect("/dashboard")
        # end if
        data["form_error"] = result.get("desc") or "Could not update order"
        return render_template("dashboard_orders.html", data=data)
    # end if
    data = proc.base_data("orders", extra)
    if not data.get("is_ahc_member"):
        return redirect("/dashboard")
    # end if
    if (request.args.get("ok") or "") == "1":
        data["form_ok"] = True
    # end if
    return render_template("dashboard_orders.html", data=data)
# end def

def html_order_detail(order_ref):
    gate = _need_login()
    if gate != None:
        return gate
    # end if
    proc = dashboard_proc()
    data = proc.base_data("orders")
    if not data.get("is_ahc_member"):
        return redirect("/dashboard")
    # end if
    order_tab = (request.args.get("tab") or "details").strip().lower()
    if order_tab not in ["details", "shipping"]:
        order_tab = "details"
    # end if
    order = proc.get_referral_order_detail(data.get("participant"), order_ref)
    if order == None:
        return "Transaction not found", 404
    # end if
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        params["pkey"] = order.get("pkey") or ""
        action = (params.get("action") or "delivery_location").strip()
        if action == "shipping_request":
            result = proc.save_shipping_request(params)
        elif action == "shipping_complete":
            result = proc.complete_officer_shipping_order(params)
        else:
            result = proc.update_referral_order(params)
        # end if
        if result.get("status") == "SUCCESS":
            if action == "shipping_request":
                return redirect("/dashboard/orders/" + order_ref + "?tab=shipping&shipping_ok=1")
            # end if
            if action == "shipping_complete":
                return redirect("/dashboard/orders/" + order_ref + "?tab=details&complete_ok=1")
            # end if
            return redirect("/dashboard/orders/" + order_ref + "?tab=details&ok=1")
        # end if
        if action == "shipping_request":
            data["shipping_error"] = result.get("desc") or "Could not save shipping choice"
        else:
            data["form_error"] = result.get("desc") or "Could not update delivery location"
        # end if
    # end if
    data["order_tab"] = order_tab
    data["order"] = order
    data["form_ok"] = (request.args.get("ok") or "") == "1"
    data["complete_ok"] = (request.args.get("complete_ok") or "") == "1"
    data["shipping_ok"] = (request.args.get("shipping_ok") or "") == "1"
    data["shipping_eligibility"] = proc.shipping_eligibility(data.get("participant"), order)
    return render_template("dashboard_order_detail.html", data=data)
# end def

def html_proposal():
    gate = _need_login()
    if gate != None:
        return gate
    # end if
    proc = dashboard_proc()
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        result = proc.save_member_pledge(params)
        if result.get("status") == "SUCCESS":
            return redirect("/dashboard/proposal?tab=follow_up&ok=1")
        # end if
        data = proc.base_data("proposal")
        if not data.get("is_ahc_member"):
            return redirect("/dashboard")
        # end if
        data["form_error"] = result.get("desc", "")
        data["proposal_tab"] = "follow_up"
        follow_up = []
        done = []
        for item in data.get("proposal_pledges") or []:
            if (item.get("follow_status") or "") == "RECEIVED":
                done.append(item)
            else:
                follow_up.append(item)
            # end if
        # end for
        data["proposal_follow_up"] = follow_up
        data["proposal_done"] = done
        data["proposal_rows"] = follow_up
        return render_template("dashboard_proposal.html", data=data)
    # end if
    data = proc.base_data("proposal")
    if not data.get("is_ahc_member"):
        return redirect("/dashboard")
    # end if
    tab = (request.args.get("tab") or "follow_up").strip().lower()
    if tab not in ["follow_up", "done"]:
        tab = "follow_up"
    # end if
    follow_up = []
    done = []
    for item in data.get("proposal_pledges") or []:
        if (item.get("follow_status") or "") == "RECEIVED":
            done.append(item)
        else:
            follow_up.append(item)
        # end if
    # end for
    data["proposal_tab"] = tab
    data["proposal_follow_up"] = follow_up
    data["proposal_done"] = done
    data["form_ok"] = (request.args.get("ok") or "") == "1"
    if tab == "done":
        data["proposal_rows"] = done
    else:
        data["proposal_rows"] = follow_up
    # end if
    return render_template("dashboard_proposal.html", data=data)
# end def

def html_events():
    gate = _need_login()
    if gate != None:
        return gate
    # end if
    proc = dashboard_proc()
    data = proc.base_data("events")
    return render_template("dashboard_events.html", data=data)
# end def

def html_profile():
    gate = _need_login()
    if gate != None:
        return gate
    # end if
    proc = dashboard_proc()
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        result = proc.save_profile(params)
        data = proc.base_data("profile")
        if result.get("status") == "SUCCESS":
            data["form_ok"] = True
        else:
            data["form_error"] = result.get("desc", "")
        # end if
        return render_template("dashboard_profile.html", data=data)
    # end if
    data = proc.base_data("profile")
    return render_template("dashboard_profile.html", data=data)
# end def
