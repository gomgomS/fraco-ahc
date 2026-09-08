import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from flask import render_template, request, redirect
import sanitize
from cart.cart_proc import cart_proc

def html_cart():
    proc = cart_proc()
    data = proc.get_cart_page()
    return render_template("cart.html", data=data)
# end def

def html_add():
    proc = cart_proc()
    params = sanitize.clean_html_dic(request.form.to_dict())
    proc.add_item(params)
    nxt = (params.get("next") or "").strip()
    if nxt == "checkout":
        return redirect("/checkout")
    # end if
    return redirect("/cart")
# end def

def html_update():
    proc = cart_proc()
    params = sanitize.clean_html_dic(request.form.to_dict())
    proc.update_item(params)
    return redirect("/cart")
# end def

def html_remove():
    proc = cart_proc()
    params = sanitize.clean_html_dic(request.form.to_dict())
    proc.remove_item(params)
    return redirect("/cart")
# end def

def html_checkout():
    proc = cart_proc()
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        action = (params.get("action") or "").strip()
        if action == "apply_referral":
            data = proc.get_checkout_page("", params.get("referral_code") or "")
            data["form_values"] = params
            if data.get("cart_items") == []:
                return redirect("/cart")
            # end if
            return render_template("checkout.html", data=data)
        # end if
        result = proc.place_order(params)
        if result.get("status") == "SUCCESS":
            return redirect("/order/" + result.get("order_id"))
        # end if
        data = proc.get_checkout_page(result.get("desc", ""), params.get("referral_code") or "")
        data["form_values"] = params
        return render_template("checkout.html", data=data)
    # end if
    data = proc.get_checkout_page()
    data["form_values"] = {}
    if data.get("cart_items") == []:
        return redirect("/cart")
    # end if
    return render_template("checkout.html", data=data)
# end def

def html_order(order_id):
    proc = cart_proc()
    data = proc.get_order_page(order_id)
    if data == None:
        return "Order not found", 404
    # end if
    return render_template("order.html", data=data)
# end def
