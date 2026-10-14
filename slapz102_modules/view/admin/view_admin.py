import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from flask import render_template, request, redirect, Response
from io import BytesIO
import re
from urllib.parse import quote
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import sanitize
from admin.admin_proc import admin_proc

def _safe_next():
    nxt = (request.args.get("next") or request.form.get("next") or "/admin").strip()
    if nxt[0:6] != "/admin":
        nxt = "/admin"
    # end if
    if ".." in nxt:
        nxt = "/admin"
    # end if
    return nxt
# end def

def _gate(page_key, write=False, delete=False, pay=False):
    proc = admin_proc()
    result = proc.gate(page_key)
    if result.get("status") == "LOGIN":
        return redirect("/admin/login?next=" + request.path)
    # end if
    if result.get("status") == "FORBIDDEN":
        return "Forbidden", 403
    # end if
    admin = proc.current_admin()
    role = (admin or {}).get("role", "")
    if write and not proc.can_write(role, page_key):
        return "This role can view this page but cannot change it.", 403
    # end if
    if delete and not proc.can_delete(role, page_key):
        return "This role cannot delete here.", 403
    # end if
    if pay and not proc.can_pay(role):
        return "Only finance, admin, or super admin can change money.", 403
    # end if
    return None
# end def

def _deny_post(page_key, params=None):
    action = ""
    if params != None:
        action = params.get("action") or ""
    # end if
    if action in ["delete", "deactivate"]:
        return _gate(page_key, delete=True)
    # end if
    if page_key == "payments":
        return _gate(page_key, write=True, pay=True)
    # end if
    return _gate(page_key, write=True)
# end def

def html_login():
    proc = admin_proc()
    if proc.current_admin() != None:
        return redirect(_safe_next())
    # end if
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        raw = request.form.get("password") or ""
        result = proc.login(params, raw)
        if result.get("status") == "SUCCESS":
            return redirect(_safe_next())
        # end if
        data = proc.page("login", {"form_error": result.get("desc", ""), "next_path": _safe_next()})
        return render_template("admin_login.html", data=data)
    # end if
    data = proc.page("login", {"next_path": _safe_next()})
    return render_template("admin_login.html", data=data)
# end def

def html_logout():
    proc = admin_proc()
    proc.logout()
    return redirect("/admin/login")
# end def

def html_overview():
    gate = _gate("overview")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    data = proc.page("overview", proc.get_stats())
    return render_template("admin_overview.html", data=data)
# end def

def html_participants():
    gate = _gate("participants")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    section = (request.args.get("section") or "overview").strip().lower()
    ahc_tab = (request.args.get("ahc_tab") or "list").strip().lower()
    focus = (request.args.get("focus") or "all").strip().lower()
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        denied = _deny_post("participants", params)
        if denied != None:
            return denied
        # end if
        action = params.get("action") or ""
        pkey = params.get("pkey") or ""
        if action in ["delete", "deactivate"] and pkey != "":
            proc.delete_participant(pkey)
        # end if
        nxt = "/admin/participants?section=" + section
        if section == "ahc":
            nxt = nxt + "&ahc_tab=" + ahc_tab
            if focus != "all":
                nxt = nxt + "&focus=" + focus
            # end if
        # end if
        return redirect(nxt)
    # end if
    hub = proc.participants_hub(section, ahc_tab, focus)
    data = proc.page("participants", hub)
    return render_template("admin_participants.html", data=data)
# end def

def html_participant(pkey):
    gate = _gate("participants")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    rec = proc.get_row("db_participant", pkey)
    if rec == None:
        return "Not found", 404
    # end if
    tab = (request.args.get("tab") or "details").strip().lower()
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        denied = _deny_post("participants", params)
        if denied != None:
            return denied
        # end if
        action = params.get("action") or "save"
        if action in ["delete", "deactivate"]:
            proc.delete_participant(pkey)
            return redirect("/admin/participants")
        # end if
        new_password = request.form.get("new_password") or ""
        fields = {
            "full_name": params.get("full_name") or "",
            "phone": params.get("phone") or "",
            "address": params.get("address") or "",
            "city": params.get("city") or "",
            "shirt_size": params.get("shirt_size") or "",
            "member_kit_status": params.get("member_kit_status") or "",
            "registration_status": params.get("registration_status") or "",
            "notes": params.get("notes") or "",
            "member_type": (params.get("member_type") or rec.get("member_type") or "AHC_MEMBER").upper(),
            "referral_code": re.sub(r"[^a-z0-9]", "", (params.get("referral_code") or "").strip().lower())
        }
        if fields["member_type"] not in ["AHC_MEMBER", "ALUMNI"]:
            fields["member_type"] = "AHC_MEMBER"
        # end if
        if proc.can_write((proc.current_admin() or {}).get("role", ""), "participants"):
            fields["contribution_num"] = proc.parse_int(params.get("contribution_num"))
            if fields["contribution_num"] > 0:
                fields["contribution"] = proc.format_rp(fields["contribution_num"])
            elif fields["member_type"] == "ALUMNI":
                fields["contribution"] = "Rp 0"
                fields["contribution_num"] = 0
            # end if
        # end if
        proc.save_row("db_participant", pkey, fields)
        if new_password.strip() != "":
            result = proc.set_participant_password(rec, new_password.strip())
            if result.get("status") != "SUCCESS":
                detail = proc.participant_detail(proc.get_row("db_participant", pkey), "details")
                detail["form_error"] = result.get("desc") or "Could not update password"
                data = proc.page("participants", detail)
                return render_template("admin_participant.html", data=data)
            # end if
        # end if
        proc.sync_participant_money(pkey)
        return redirect("/admin/participants/" + pkey + "?tab=details")
    # end if
    detail = proc.participant_detail(rec, tab)
    data = proc.page("participants", detail)
    return render_template("admin_participant.html", data=data)
# end def

def html_orders():
    gate = _gate("orders")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        denied = _deny_post("orders", params)
        if denied != None:
            return denied
        # end if
        action = params.get("action") or ""
        pkey = params.get("pkey") or ""
        if action == "delete" and pkey != "":
            proc.delete_order(pkey)
            return redirect("/admin/orders")
        # end if
        if action == "order_pay":
            rec = proc.get_row("db_order", pkey)
            if rec != None:
                pay = proc.pick_order_pay(params.get("payment_status") or "", rec.get("payment_status"))
                proc.save_row("db_order", pkey, {"payment_status": pay})
            # end if
        # end if
        if action == "order_shipping_handler":
            rec = proc.get_row("db_order", pkey)
            if rec != None:
                shipping_params = {
                    "shipping_handler": params.get("shipping_handler") or "",
                    "shipping_request_status": rec.get("shipping_request_status") or "REQUESTED",
                    "shipping_expedition": rec.get("shipping_expedition") or "",
                    "shipping_budget_num": rec.get("shipping_budget_num") or 0,
                    "shipping_tracking_code": rec.get("shipping_tracking_code") or "",
                    "shipping_tracking_url": rec.get("shipping_tracking_url") or ""
                }
                result = proc.save_order_shipping(pkey, shipping_params)
                if result.get("status") != "SUCCESS":
                    return redirect("/admin/orders/" + pkey + "?tab=shipping&error=" + quote(result.get("desc") or "Could not save shipping type"))
                # end if
            # end if
        # end if
        return redirect("/admin/orders")
    # end if
    shipping_filter = (request.args.get("shipping") or "").strip().upper()
    print_params = []
    for key in ["status", "pay", "q"]:
        value = (request.args.get(key) or "").strip()
        if value != "":
            print_params.append(key + "=" + quote(value))
        # end if
    # end for
    print_href = "/admin/orders/print/officer"
    if print_params != []:
        print_href = print_href + "?" + "&".join(print_params)
    # end if
    data = proc.page("orders", {
        "list_table": proc.table_orders(),
        "show_officer_print": shipping_filter == "OFFICER",
        "officer_print_href": print_href
    })
    return render_template("admin_orders.html", data=data)
# end def

def html_officer_shipping_print():
    gate = _gate("orders")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    params = sanitize.clean_html_dic(request.args.to_dict())
    raw_order_pkeys = request.args.getlist("order")
    order_pkeys = None
    if raw_order_pkeys != []:
        order_pkeys = [sanitize.clean_html(value) for value in raw_order_pkeys]
    # end if
    documents = proc.officer_shipping_documents(
        (params.get("status") or "").strip(),
        (params.get("pay") or "").strip(),
        (params.get("q") or "").strip(),
        order_pkeys
    )
    data = proc.page("orders", {"documents": documents})
    return render_template("admin_shipping_bulk_print.html", data=data)
# end def

def html_order(pkey):
    gate = _gate("orders")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    order_tab = (request.args.get("tab") or "details").strip().lower()
    if order_tab not in ["details", "shipping"]:
        order_tab = "details"
    # end if
    rec = proc.get_row("db_order", pkey)
    if rec == None:
        return "Not found", 404
    # end if
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        denied = _deny_post("orders", params)
        if denied != None:
            return denied
        # end if
        if (params.get("action") or "") == "order_line_status":
            result = proc.update_order_line_status(
                pkey,
                params.get("item_index") or "",
                params.get("line_status") or ""
            )
            if result.get("status") != "SUCCESS":
                return redirect("/admin/orders/" + pkey + "?tab=details&error=" + quote(result.get("desc") or "Could not update item status"))
            # end if
            return redirect("/admin/orders/" + pkey + "?tab=details&ok=" + quote("Item shipment status saved"))
        # end if
        if (params.get("action") or "") == "delete":
            proc.delete_order(pkey)
            return redirect("/admin/orders")
        # end if
        if (params.get("action") or "") == "shipping_reset":
            result = proc.reset_order_shipping(pkey)
            if result.get("status") != "SUCCESS":
                return redirect("/admin/orders/" + pkey + "?tab=shipping&error=" + quote(result.get("desc") or "Could not reset shipping choice"))
            # end if
            return redirect("/admin/orders/" + pkey + "?tab=shipping&ok=" + quote("Shipping choice reset. The member can choose again."))
        # end if
        if (params.get("action") or "") == "shipping_update":
            result = proc.save_order_shipping(pkey, params)
            if result.get("status") != "SUCCESS":
                return redirect("/admin/orders/" + pkey + "?tab=shipping&error=" + quote(result.get("desc") or "Could not save shipping"))
            # end if
            return redirect("/admin/orders/" + pkey + "?tab=shipping&ok=" + quote("Shipping information saved"))
        # end if
        pay = proc.pick_order_pay(params.get("payment_status") or "", rec.get("payment_status"))
        proc.save_row("db_order", pkey, {
            "order_status": params.get("order_status") or rec.get("order_status"),
            "payment_status": pay,
            "notes": params.get("notes") or ""
        })
        return redirect("/admin/orders/" + pkey)
    # end if
    shipping_eligibility = proc.order_shipping_eligibility(rec)
    rec["shipping_service_fee_num"] = shipping_eligibility.get("service_fee_num") or 0
    rec["shipping_service_fee"] = shipping_eligibility.get("service_fee") or "Rp 0"
    rec["shipping_total_expense_num"] = (
        int(rec.get("shipping_budget_num") or 0) +
        int(rec.get("shipping_service_fee_num") or 0)
    )
    rec["shipping_total_expense"] = proc.format_rp(rec.get("shipping_total_expense_num"))
    data = proc.page("orders", {
        "order_tab": order_tab,
        "row": rec,
        "statuses": proc.ORDER_STATUSES,
        "pay_statuses": proc.order_pay_options(rec.get("payment_status") or ""),
        "item_table": proc.table_order_items(rec),
        "referrer_label": proc.order_referrer_label(rec),
        "referrer": proc.find_order_referrer(rec),
        "shipping_expeditions": proc.shipping_expeditions(),
        "shipping_statuses": proc.shipping_status_options(),
        "shipping_eligibility": shipping_eligibility,
        "form_ok": (request.args.get("ok") or "").strip(),
        "form_error": (request.args.get("error") or "").strip()
    })
    return render_template("admin_order.html", data=data)
# end def

def html_order_shipping_document(pkey):
    gate = _gate("orders")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    rec = proc.get_row("db_order", pkey)
    if rec == None:
        return "Not found", 404
    # end if
    data = proc.page("orders", {
        "row": rec,
        "document": proc.shipping_document_data(rec)
    })
    return render_template("admin_shipping_document.html", data=data)
# end def

def pdf_order_shipping_document(pkey):
    gate = _gate("orders")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    rec = proc.get_row("db_order", pkey)
    if rec == None:
        return "Not found", 404
    # end if
    data = proc.shipping_document_data(rec)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ShippingTitle",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        fontSize=18,
        leading=22,
        spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name="ShippingLabel",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#666666"),
        spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        name="ShippingValue",
        parent=styles["Normal"],
        fontSize=11,
        leading=15
    ))
    styles.add(ParagraphStyle(
        name="ShippingNote",
        parent=styles["Normal"],
        fontSize=10,
        leading=14
    ))
    def paragraph(value, style="ShippingValue"):
        text = escape(str(value or "—")).replace("\n", "<br/>")
        return Paragraph(text, styles[style])
    # end def
    recipient_location = " · ".join([
        value for value in [data.get("recipient_city"), data.get("recipient_postal_code")] if value
    ])
    buffer = BytesIO()
    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A5,
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        title="Pengiriman " + data.get("order_id", "")
    )
    story = [
        Paragraph(escape(data.get("order_id") or "—"), styles["ShippingTitle"]),
        Spacer(1, 3 * mm)
    ]
    contact_table = Table([
        [
            [paragraph("PENGIRIM / MEMBER FRACO", "ShippingLabel"), paragraph(data.get("sender_name")), paragraph(data.get("sender_phone"))],
            [paragraph("PENERIMA", "ShippingLabel"), paragraph(data.get("recipient_name")), paragraph(data.get("recipient_phone"))]
        ],
        [
            [paragraph("ALAMAT PENERIMA", "ShippingLabel"), paragraph(data.get("recipient_address")), paragraph(recipient_location)],
            ""
        ]
    ], colWidths=[62 * mm, 62 * mm])
    contact_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("SPAN", (0, 1), (1, 1)),
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#aaaaaa")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8)
    ]))
    story.append(contact_table)
    item_rows = [[paragraph("BARANG", "ShippingLabel"), paragraph("JUMLAH", "ShippingLabel")]]
    for item in data.get("items") or []:
        item_label = item.get("name") or "Merchandise"
        if item.get("options"):
            item_label += "\n" + item.get("options")
        # end if
        item_rows.append([paragraph(item_label), paragraph(item.get("qty"))])
    # end for
    item_table = Table(item_rows, colWidths=[106 * mm, 18 * mm])
    item_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7)
    ]))
    story.append(item_table)
    if data.get("package_note"):
        note_table = Table([[
            [paragraph("CATATAN PAKET", "ShippingLabel"), paragraph(data.get("package_note"), "ShippingNote")]
        ]], colWidths=[124 * mm])
        note_table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7)
        ]))
        story.append(note_table)
    # end if
    pdf.build(story)
    filename = re.sub(r"[^A-Za-z0-9._-]", "-", data.get("order_id") or "order")
    return Response(
        buffer.getvalue(),
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment; filename=shipping-" + filename + ".pdf"}
    )
# end def

def _discount_is_enabled(rec):
    row = rec or {}
    flag = row.get("discount_enabled")
    if flag == True or flag in ["1", "YES", "true", "on", "True"]:
        return True
    # end if
    if flag == False or flag in ["0", "NO", "false", "off", "False"]:
        return False
    # end if
    try:
        return int(row.get("discount_num") or 0) > 0
    except Exception:
        return False
    # end try
# end def

def _unit_discount_amount(price_num, discount_type, discount_num, enabled=True):
    if not enabled:
        return 0
    # end if
    price = int(price_num or 0)
    dnum = int(discount_num or 0)
    dtype = (discount_type or "PCT").strip().upper()
    if price <= 0 or dnum <= 0:
        return 0
    # end if
    if dtype == "FIXED":
        amount = dnum
    else:
        amount = int(round(price * dnum / 100.0))
    # end if
    if amount > price:
        amount = price
    # end if
    if amount < 0:
        amount = 0
    # end if
    return amount
# end def

def _decorate_product_profit(proc, rec):
    # Base profit = price − bahan. Referral discount cuts profit only (not bahan).
    if rec == None or rec == {}:
        return rec
    # end if
    price_num = int(rec.get("price_num") or 0)
    bahan_num = int(rec.get("bahan_baku_num") or 0)
    if bahan_num < 0:
        bahan_num = 0
    # end if
    profit_num = price_num - bahan_num
    if profit_num < 0:
        profit_num = 0
    # end if
    discount_enabled = _discount_is_enabled(rec)
    discount_type = (rec.get("discount_type") or "PCT").strip().upper() or "PCT"
    discount_num = int(rec.get("discount_num") or 0)
    if discount_num < 0:
        discount_num = 0
    # end if
    unit_disc = _unit_discount_amount(price_num, discount_type, discount_num, discount_enabled)
    profit_after = profit_num - unit_disc
    if profit_after < 0:
        profit_after = 0
    # end if
    rec["discount_enabled"] = discount_enabled
    rec["profit_num"] = profit_num
    rec["profit"] = proc.format_rp(profit_num)
    rec["discount_unit_num"] = unit_disc
    rec["discount_unit"] = proc.format_rp(unit_disc) if unit_disc > 0 else ""
    rec["profit_with_discount_num"] = profit_after
    rec["profit_with_discount"] = proc.format_rp(profit_after)
    rec["has_referral_discount"] = unit_disc > 0
    rec["discount_hits_bahan"] = unit_disc > 0 and unit_disc > profit_num
    return rec
# end def

def _decorate_product_form(proc, rec):
    rec = _decorate_product_profit(proc, rec)
    if rec == None or rec == {}:
        return rec
    # end if
    sizes = rec.get("sizes") or []
    by_size = rec.get("stock_by_size") or {}
    if not isinstance(by_size, dict):
        by_size = {}
    # end if
    rows = []
    for idx in range(0, len(sizes)):
        sz = sizes[idx]
        qty = 0
        if sz in by_size:
            try:
                qty = int(by_size.get(sz) or 0)
            except Exception:
                qty = 0
            # end try
        # end if
        rows.append({"size": sz, "stock": qty, "idx": idx})
    # end for
    rec["size_stock_rows"] = rows
    rec["stock_by_size"] = by_size
    return rec
# end def

def _product_category_options(proc, rec=None):
    categories = proc.merchandise_categories()
    current = ((rec or {}).get("category") or "").strip()
    if current != "" and current not in categories:
        categories.append(current)
    # end if
    return categories
# end def

def _product_fields(proc, params):
    name = (params.get("name") or "").strip()
    slug = (params.get("slug") or "").strip()
    if slug == "":
        slug = proc.slugify(name)
    # end if
    price_num = proc.parse_int(params.get("price_num") or params.get("price"))
    bahan_num = proc.parse_int(params.get("bahan_baku_num") or params.get("bahan_baku"))
    if bahan_num < 0:
        bahan_num = 0
    # end if
    profit_num = price_num - bahan_num
    if profit_num < 0:
        profit_num = 0
    # end if
    discount_enabled = (params.get("discount_enabled") or "") in ["1", "YES", "true", "on"]
    discount_type = (params.get("discount_type") or "PCT").strip().upper()
    if discount_type not in ["PCT", "FIXED"]:
        discount_type = "PCT"
    # end if
    discount_num = proc.parse_int(params.get("discount_num") or params.get("discount"))
    if discount_num < 0:
        discount_num = 0
    # end if
    if discount_type == "PCT" and discount_num > 100:
        discount_num = 100
    # end if
    if discount_enabled and discount_num > 0:
        if discount_type == "PCT":
            discount_label = str(discount_num) + "%"
        else:
            discount_label = proc.format_rp(discount_num)
        # end if
    else:
        discount_label = ""
    # end if
    is_preorder_legacy = (params.get("is_preorder") or "") in ["1", "YES", "true", "on"]
    allow_preorder = (params.get("allow_preorder") or "") in ["1", "YES", "true", "on"]
    if not allow_preorder and is_preorder_legacy:
        allow_preorder = True
    # end if
    sizes = proc.parse_list(params.get("sizes"))
    stock_by_size = {}
    stock_num = 0
    if sizes != []:
        for idx in range(0, len(sizes)):
            sz = sizes[idx]
            key = "stock_size_" + str(idx)
            n = proc.parse_int(params.get(key))
            if n < 0:
                n = 0
            # end if
            stock_by_size[sz] = n
            stock_num = stock_num + n
        # end for
    else:
        stock_num = proc.parse_int(params.get("stock"))
        if stock_num < 0:
            stock_num = 0
        # end if
    # end if
    availability = (params.get("availability") or "").strip()
    if availability == "":
        if stock_num > 0:
            availability = "In Stock"
        elif allow_preorder:
            availability = "Preorder"
        else:
            availability = "Out of Stock"
        # end if
    # end if
    return {
        "name": name,
        "slug": slug,
        "sku": params.get("sku") or "",
        "category": params.get("category") or "",
        "description": params.get("description") or "",
        "price": proc.format_rp(price_num),
        "price_num": price_num,
        "bahan_baku": proc.format_rp(bahan_num),
        "bahan_baku_num": bahan_num,
        "profit": proc.format_rp(profit_num),
        "profit_num": profit_num,
        "discount": discount_label,
        "discount_type": discount_type,
        "discount_num": discount_num,
        "discount_note": (params.get("discount_note") or "").strip(),
        "discount_enabled": discount_enabled,
        "stock": stock_num,
        "stock_by_size": stock_by_size,
        "reserved": proc.parse_int(params.get("reserved")),
        "sold": proc.parse_int(params.get("sold")),
        "sizes": sizes,
        "colors": proc.parse_list(params.get("colors")),
        "image": params.get("image") or "",
        "availability": availability,
        "allow_preorder": allow_preorder,
        "is_preorder": allow_preorder,
        "preorder_eta": (params.get("preorder_eta") or "").strip(),
        "preorder_note": (params.get("preorder_note") or "").strip(),
        "status": params.get("status") or "DRAFT"
    }
# end def

def html_products():
    gate = _gate("products")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        denied = _deny_post("products", params)
        if denied != None:
            return denied
        # end if
        action = params.get("action") or ""
        pkey = params.get("pkey") or ""
        if action == "delete" and pkey != "":
            proc.soft_delete("db_product", pkey)
        # end if
        return redirect("/admin/products")
    # end if
    data = proc.page("products", {"list_table": proc.table_products()})
    return render_template("admin_products.html", data=data)
# end def

def html_product_form(pkey=""):
    gate = _gate("products")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    rec = {}
    if pkey != "":
        rec = proc.get_row("db_product", pkey) or {}
        if rec == {}:
            return "Not found", 404
        # end if
        if rec.get("allow_preorder") != True and (
            rec.get("is_preorder") == True or rec.get("is_preorder") in ["1", "YES"]
        ):
            rec["allow_preorder"] = True
        # end if
        if int(rec.get("discount_num") or 0) <= 0:
            raw = (rec.get("discount") or "").strip().replace(" ", "")
            if raw.endswith("%"):
                rec["discount_type"] = "PCT"
                try:
                    rec["discount_num"] = int(re.sub(r"[^0-9]", "", raw[:-1]) or 0)
                except Exception:
                    rec["discount_num"] = 0
                # end try
            elif raw.lower().startswith("rp"):
                rec["discount_type"] = "FIXED"
                try:
                    rec["discount_num"] = int(re.sub(r"[^0-9]", "", raw) or 0)
                except Exception:
                    rec["discount_num"] = 0
                # end try
            elif re.sub(r"[^0-9]", "", raw) != "":
                try:
                    n = int(re.sub(r"[^0-9]", "", raw) or 0)
                except Exception:
                    n = 0
                # end try
                rec["discount_num"] = n
                if (rec.get("discount_type") or "") == "":
                    rec["discount_type"] = "PCT" if n <= 100 else "FIXED"
                # end if
            # end if
        # end if
    # end if
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        denied = _deny_post("products", params)
        if denied != None:
            return denied
        # end if
        action = params.get("action") or ""
        if action == "delete" and pkey != "":
            proc.soft_delete("db_product", pkey)
            return redirect("/admin/products")
        # end if
        if action == "stock_arrived" and pkey != "":
            result = proc.release_product_stock(pkey, params.get("arrived_stock"))
            if result.get("status") == "SUCCESS":
                msg = "Stock set to " + str(result.get("stock")) + ". Released " + str(result.get("released")) + " preorder(s) to Ready."
                return redirect("/admin/products/" + pkey + "?ok=" + quote(msg))
            # end if
            data = proc.page("products", {
                "row": _decorate_product_form(proc, proc.get_row("db_product", pkey) or rec),
                "form_error": result.get("desc", "Could not update stock"),
                "statuses": proc.PRODUCT_STATUSES,
                "categories": _product_category_options(proc, rec)
            })
            return render_template("admin_product_form.html", data=data)
        # end if
        old_image = rec.get("image") or ""
        image = (params.get("image") or "").strip()
        existing_gallery = []
        if isinstance(rec.get("images"), list):
            existing_gallery = [
                item for item in rec.get("images") if isinstance(item, str) and item.strip() != ""
            ]
        # end if
        if existing_gallery == [] and old_image != "":
            existing_gallery = [old_image]
        # end if
        upload_files = [
            file_obj for file_obj in request.files.getlist("image_file")
            if file_obj != None and file_obj.filename != ""
        ]
        kept_existing = [item for item in existing_gallery if item != old_image]
        if len(upload_files) + len(kept_existing) > 12:
            fields = _decorate_product_form(proc, _product_fields(proc, params))
            fields["image"] = image or old_image
            fields["images"] = existing_gallery
            data = proc.page("products", {
                "row": fields,
                "form_error": "A product can have up to 12 images. Remove some images before uploading more.",
                "statuses": proc.PRODUCT_STATUSES,
                "categories": _product_category_options(proc, fields)
            })
            return render_template("admin_product_form.html", data=data)
        # end if
        uploaded_images = []
        upload_error = ""
        for file_obj in upload_files:
            stored, rel = proc.save_upload(file_obj, "products")
            if stored == "ERR_TYPE":
                upload_error = "Every image must be jpg, png, or webp"
                break
            # end if
            if rel != "":
                uploaded_images.append(rel)
            # end if
        # end for
        if upload_error != "":
            for uploaded_image in uploaded_images:
                proc.delete_local_upload(uploaded_image)
            # end for
            fields = _decorate_product_form(proc, _product_fields(proc, params))
            fields["image"] = image or old_image
            fields["images"] = existing_gallery
            data = proc.page("products", {
                "row": fields,
                "form_error": upload_error,
                "statuses": proc.PRODUCT_STATUSES,
                "categories": _product_category_options(proc, fields)
            })
            return render_template("admin_product_form.html", data=data)
        # end if
        if uploaded_images != []:
            image = uploaded_images[0]
        # end if
        params["image"] = image
        fields = _product_fields(proc, params)
        if image != "":
            if uploaded_images != []:
                gallery = uploaded_images + [
                    item for item in existing_gallery
                    if item not in uploaded_images and item != old_image
                ]
            elif image != old_image:
                gallery = [image] + [
                    item for item in existing_gallery if item != image and item != old_image
                ]
            else:
                gallery = existing_gallery if existing_gallery != [] else [image]
            # end if
            fields["images"] = gallery[:12]
        else:
            fields["images"] = []
        # end if
        result = proc.save_row("db_product", pkey, fields)
        if result.get("status") == "SUCCESS":
            if uploaded_images != [] and old_image != "" and old_image != image:
                proc.delete_local_upload(old_image)
            # end if
            return redirect("/admin/products")
        # end if
        for uploaded_image in uploaded_images:
            proc.delete_local_upload(uploaded_image)
        # end for
        if uploaded_images != []:
            fields["image"] = old_image
            fields["images"] = existing_gallery
        # end if
        data = proc.page("products", {
            "row": _decorate_product_form(proc, fields),
            "form_error": result.get("desc", ""),
            "statuses": proc.PRODUCT_STATUSES,
            "categories": _product_category_options(proc, fields)
        })
        return render_template("admin_product_form.html", data=data)
    # end if
    form_ok = (request.args.get("ok") or "").strip()
    data = proc.page("products", {
        "row": _decorate_product_form(proc, rec),
        "statuses": proc.PRODUCT_STATUSES,
        "categories": _product_category_options(proc, rec),
        "form_ok": form_ok
    })
    return render_template("admin_product_form.html", data=data)
# end def

def html_programs():
    gate = _gate("programs")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    data = proc.page("programs", {"list_table": proc.table_programs()})
    return render_template("admin_programs.html", data=data)
# end def

def html_program_form(pkey=""):
    gate = _gate("programs")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    rec = {}
    if pkey != "":
        rec = proc.get_row("db_program", pkey) or {}
        if rec == {}:
            return "Not found", 404
        # end if
    # end if
    def _program_tab(default="details"):
        tab = (request.args.get("tab") or request.form.get("tab") or default).strip().lower()
        if tab not in ["details", "schedule", "updates", "faq"]:
            tab = "details"
        # end if
        if pkey == "" and tab != "details":
            tab = "details"
        # end if
        return tab
    # end def
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        denied = _deny_post("programs", params)
        if denied != None:
            return denied
        # end if
        if (params.get("action") or "") == "delete" and pkey != "":
            proc.delete_program(pkey)
            return redirect("/admin/programs")
        # end if
        old_image = ""
        if rec != {}:
            old_image = rec.get("image") or ""
        # end if
        image = (params.get("image") or "").strip()
        file_obj = request.files.get("image_file")
        stored, rel = proc.save_upload(file_obj, "programs")
        if stored == "ERR_TYPE":
            bundle = proc.get_program_bundle((params.get("slug") or "").strip() or (rec.get("slug") or ""))
            data = proc.page("programs", {
                "row": params if params.get("title") else rec,
                "program_tab": "details",
                "form_error": "Cover image must be jpg, png, or webp",
                "venue_modes": proc.VENUE_MODES,
                "update_categories": proc.UPDATE_CATEGORIES,
                "schedule": bundle["schedule"],
                "faqs": bundle["faqs"],
                "updates": bundle["updates"]
            })
            return render_template("admin_program_form.html", data=data)
        # end if
        if rel != "":
            image = rel
        # end if
        params["image"] = image
        result = proc.save_program_full(pkey, params)
        if result.get("status") == "SUCCESS":
            if rel != "" and old_image != "" and old_image != image:
                proc.delete_local_upload(old_image)
            # end if
            return redirect("/admin/programs/" + result.get("pkey", pkey) + "?tab=details")
        # end if
        bundle = proc.get_program_bundle((params.get("slug") or "").strip())
        data = proc.page("programs", {
            "row": params,
            "program_tab": "details",
            "form_error": result.get("desc", "Could not save"),
            "venue_modes": proc.VENUE_MODES,
            "update_categories": proc.UPDATE_CATEGORIES,
            "schedule": bundle["schedule"],
            "faqs": bundle["faqs"],
            "updates": bundle["updates"]
        })
        return render_template("admin_program_form.html", data=data)
    # end if
    slug = rec.get("slug") or ""
    bundle = proc.get_program_bundle(slug)
    form_error = ""
    if (request.args.get("error") or "") == "image_type":
        form_error = "Update image must be jpg, png, or webp"
    # end if
    data = proc.page("programs", {
        "row": rec,
        "program_tab": _program_tab(),
        "form_error": form_error,
        "venue_modes": proc.VENUE_MODES,
        "update_categories": proc.UPDATE_CATEGORIES,
        "schedule": bundle["schedule"],
        "faqs": bundle["faqs"],
        "updates": bundle["updates"]
    })
    return render_template("admin_program_form.html", data=data)
# end def

def html_program_schedule(pkey):
    gate = _gate("programs", write=True)
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    rec = proc.get_row("db_program", pkey)
    if rec == None:
        return "Not found", 404
    # end if
    params = sanitize.clean_html_dic(request.form.to_dict())
    action = params.get("action") or ""
    slug = rec.get("slug") or ""
    item = params.get("item_pkey") or ""
    if action == "delete" and item != "":
        proc.soft_delete("db_schedule", item)
    # end if
    if action == "add":
        proc.save_program_schedule(slug, params, "")
    # end if
    if action == "edit" and item != "":
        proc.save_program_schedule(slug, params, item)
    # end if
    return redirect("/admin/programs/" + pkey + "?tab=schedule")
# end def

def html_program_faq_action(pkey):
    gate = _gate("programs", write=True)
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    rec = proc.get_row("db_program", pkey)
    if rec == None:
        return "Not found", 404
    # end if
    params = sanitize.clean_html_dic(request.form.to_dict())
    action = params.get("action") or ""
    slug = rec.get("slug") or ""
    item = params.get("item_pkey") or ""
    if action == "delete" and item != "":
        proc.soft_delete("db_faq", item)
    # end if
    if action == "add":
        proc.save_program_faq(slug, params, "")
    # end if
    if action == "edit" and item != "":
        proc.save_program_faq(slug, params, item)
    # end if
    return redirect("/admin/programs/" + pkey + "?tab=faq")
# end def

def html_program_update_action(pkey):
    gate = _gate("programs", write=True)
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    rec = proc.get_row("db_program", pkey)
    if rec == None:
        return "Not found", 404
    # end if
    params = sanitize.clean_html_dic(request.form.to_dict())
    params["content"] = sanitize.clean_rich_html(request.form.get("content") or "")
    action = params.get("action") or ""
    slug = rec.get("slug") or ""
    item = params.get("item_pkey") or ""
    if action == "delete" and item != "":
        old_row = proc.get_row("db_update", item)
        proc.soft_delete("db_update", item)
        if old_row != None:
            proc.delete_local_upload(old_row.get("image"))
        # end if
    # end if
    if action in ["add", "edit"]:
        old_image = ""
        if action == "edit" and item != "":
            old_row = proc.get_row("db_update", item)
            if old_row != None:
                old_image = old_row.get("image") or ""
            # end if
        # end if
        image = (params.get("image") or "").strip()
        file_obj = request.files.get("image_file")
        stored, rel = proc.save_upload(file_obj, "updates")
        if stored == "ERR_TYPE":
            return redirect("/admin/programs/" + pkey + "?tab=updates&error=image_type")
        # end if
        if rel != "":
            image = rel
        # end if
        params["image"] = image
        result = proc.save_program_update(slug, params, item if action == "edit" else "")
        if result.get("status") == "SUCCESS" and rel != "" and old_image != "" and old_image != image:
            proc.delete_local_upload(old_image)
        # end if
    # end if
    return redirect("/admin/programs/" + pkey + "?tab=updates")
# end def

def html_events():
    gate = _gate("events")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    data = proc.page("events", {"list_table": proc.table_events()})
    return render_template("admin_events.html", data=data)
# end def

def html_event_form(pkey=""):
    gate = _gate("events")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    rec = {}
    if pkey != "":
        rec = proc.get_row("db_event", pkey) or {}
        if rec == {}:
            return "Not found", 404
        # end if
    # end if
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        denied = _deny_post("events", params)
        if denied != None:
            return denied
        # end if
        if (params.get("action") or "") == "delete" and pkey != "":
            proc.soft_delete("db_event", pkey)
            return redirect("/admin/events")
        # end if
        old_image = rec.get("image") or ""
        image = (params.get("image") or "").strip()
        stored, rel = proc.save_upload(request.files.get("image_file"), "events")
        if stored == "ERR_TYPE":
            data = proc.page("events", {
                "row": params,
                "form_error": "Image must be jpg, png, or webp",
                "event_statuses": proc.EVENT_STATUSES
            })
            return render_template("admin_event_form.html", data=data)
        # end if
        if rel != "":
            image = rel
        # end if
        proc.save_row("db_event", pkey, {
            "title": params.get("title") or "",
            "description": params.get("description") or "",
            "date": params.get("date") or "",
            "time_label": params.get("time_label") or "",
            "location": params.get("location") or "",
            "venue": params.get("venue") or params.get("location") or "",
            "capacity": params.get("capacity") or "",
            "deadline": params.get("deadline") or "",
            "speaker": params.get("speaker") or "",
            "image": image,
            "event_status": params.get("event_status") or "Draft",
            "status": params.get("status") or "ENABLE"
        })
        if rel != "" and old_image != "" and old_image != image:
            proc.delete_local_upload(old_image)
        # end if
        return redirect("/admin/events")
    # end if
    data = proc.page("events", {"row": rec, "event_statuses": proc.EVENT_STATUSES})
    return render_template("admin_event_form.html", data=data)
# end def

def html_sponsors():
    gate = _gate("sponsors")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    data = proc.page("sponsors", {
        "sponsors_tab": "applications",
        "list_table": proc.table_sponsors()
    })
    return render_template("admin_sponsors.html", data=data)
# end def

def html_sponsor(pkey):
    gate = _gate("sponsors")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    rec = proc.get_row("db_sponsor_app", pkey)
    if rec == None:
        return "Not found", 404
    # end if
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        denied = _deny_post("sponsors", params)
        if denied != None:
            return denied
        # end if
        proc.save_row("db_sponsor_app", pkey, {
            "status": params.get("status") or rec.get("status"),
            "assigned_pic": params.get("assigned_pic") or "",
            "notes": params.get("notes") or ""
        })
        return redirect("/admin/sponsors/" + pkey)
    # end if
    data = proc.page("sponsors", {
        "sponsors_tab": "applications",
        "row": rec,
        "statuses": proc.SPONSOR_STATUSES
    })
    return render_template("admin_sponsor.html", data=data)
# end def

def _sponsor_package_fields(proc, params):
    name = (params.get("name") or "").strip()
    slug = (params.get("slug") or "").strip()
    if slug == "":
        slug = proc.slugify(name)
    # end if
    status = (params.get("status") or "ENABLE").strip().upper()
    if status not in ["ENABLE", "DISABLE"]:
        status = "ENABLE"
    # end if
    return {
        "name": name,
        "slug": slug,
        "amount": (params.get("amount") or "").strip(),
        "benefits": proc.parse_lines(params.get("benefits")),
        "logo_placement": (params.get("logo_placement") or "").strip(),
        "booth": (params.get("booth") or "").strip(),
        "promo": (params.get("promo") or "").strip(),
        "other": (params.get("other") or "").strip(),
        "order": proc.parse_int(params.get("order")),
        "status": status
    }
# end def

def html_sponsor_packages():
    gate = _gate("sponsors")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        denied = _deny_post("sponsors", params)
        if denied != None:
            return denied
        # end if
        action = params.get("action") or ""
        pkey = params.get("pkey") or ""
        if action == "delete" and pkey != "":
            proc.soft_delete("db_sponsor_package", pkey)
            return redirect("/admin/sponsors/packages")
        # end if
    # end if
    data = proc.page("sponsors", {
        "sponsors_tab": "packages",
        "list_table": proc.table_sponsor_packages()
    })
    return render_template("admin_sponsor_packages.html", data=data)
# end def

def html_sponsor_package_form(pkey=""):
    gate = _gate("sponsors")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    rec = {}
    if pkey != "":
        rec = proc.get_row("db_sponsor_package", pkey) or {}
        if rec == {}:
            return "Not found", 404
        # end if
    # end if
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        denied = _deny_post("sponsors", params)
        if denied != None:
            return denied
        # end if
        action = params.get("action") or ""
        if action == "delete" and pkey != "":
            proc.soft_delete("db_sponsor_package", pkey)
            return redirect("/admin/sponsors/packages")
        # end if
        fields = _sponsor_package_fields(proc, params)
        if fields.get("name") == "":
            data = proc.page("sponsors", {
                "sponsors_tab": "packages",
                "row": fields,
                "package_statuses": ["ENABLE", "DISABLE"],
                "form_error": "Package name is required"
            })
            return render_template("admin_sponsor_package_form.html", data=data)
        # end if
        result = proc.save_row("db_sponsor_package", pkey, fields)
        if result.get("status") == "SUCCESS":
            return redirect("/admin/sponsors/packages")
        # end if
        data = proc.page("sponsors", {
            "sponsors_tab": "packages",
            "row": fields,
            "package_statuses": ["ENABLE", "DISABLE"],
            "form_error": result.get("desc", "Could not save")
        })
        return render_template("admin_sponsor_package_form.html", data=data)
    # end if
    data = proc.page("sponsors", {
        "sponsors_tab": "packages",
        "row": rec,
        "package_statuses": ["ENABLE", "DISABLE"]
    })
    return render_template("admin_sponsor_package_form.html", data=data)
# end def

def html_vendors():
    gate = _gate("vendors")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        params["description"] = sanitize.clean_rich_html(request.form.get("description") or "")
        denied = _deny_post("vendors", params)
        if denied != None:
            return denied
        # end if
        action = params.get("action") or ""
        pkey = params.get("pkey") or ""
        if action == "delete" and pkey != "":
            proc.soft_delete("db_vendor_app", pkey)
            return redirect("/admin/vendors?tab=list")
        # end if
        if action == "status" and pkey != "":
            rec = proc.get_row("db_vendor_app", pkey)
            if rec != None:
                status = (params.get("status") or "").strip()
                if status not in proc.VENDOR_STATUSES:
                    status = rec.get("status") or "PENDING"
                # end if
                proc.save_row("db_vendor_app", pkey, {"status": status})
            # end if
            return redirect("/admin/vendors?tab=list")
        # end if
        result = proc.save_vendor_app("", params)
        if result.get("status") != "SUCCESS":
            data = proc.page("vendors", {
                "vendors_tab": "add",
                "list_table": proc.table_vendors(),
                "categories": proc.vendor_categories(),
                "divisions": proc.division_names(),
                "statuses": proc.VENDOR_STATUSES,
                "form": params,
                "form_error": result.get("desc") or "Could not add vendor"
            })
            return render_template("admin_vendors.html", data=data)
        # end if
        return redirect("/admin/vendors?tab=list")
    # end if
    tab = (request.args.get("tab") or "list").strip().lower()
    if tab not in ["list", "add"]:
        tab = "list"
    # end if
    data = proc.page("vendors", {
        "vendors_tab": tab,
        "list_table": proc.table_vendors(),
        "categories": proc.vendor_categories(),
        "divisions": proc.division_names(),
        "statuses": proc.VENDOR_STATUSES,
        "form": {}
    })
    return render_template("admin_vendors.html", data=data)
# end def

def html_vendor(pkey):
    gate = _gate("vendors")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    rec = proc.get_row("db_vendor_app", pkey)
    if rec == None:
        return "Not found", 404
    # end if
    rec["description_html"] = sanitize.clean_rich_html(rec.get("description") or "")
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        params["description"] = sanitize.clean_rich_html(request.form.get("description") or "")
        denied = _deny_post("vendors", params)
        if denied != None:
            return denied
        # end if
        if (params.get("action") or "") == "delete":
            proc.soft_delete("db_vendor_app", pkey)
            return redirect("/admin/vendors?tab=list")
        # end if
        result = proc.save_vendor_app(pkey, params)
        if result.get("status") != "SUCCESS":
            data = proc.page("vendors", {
                "row": rec,
                "categories": proc.vendor_categories(),
                "divisions": proc.division_names(),
                "statuses": proc.VENDOR_STATUSES,
                "form_error": result.get("desc") or "Could not save vendor"
            })
            return render_template("admin_vendor.html", data=data)
        # end if
        return redirect("/admin/vendors/" + pkey)
    # end if
    data = proc.page("vendors", {
        "row": rec,
        "categories": proc.vendor_categories(),
        "divisions": proc.division_names(),
        "statuses": proc.VENDOR_STATUSES
    })
    return render_template("admin_vendor.html", data=data)
# end def

def html_universities():
    gate = _gate("universities")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    data = proc.page("universities", {
        "list_table": proc.table_university_applications()
    })
    return render_template("admin_universities.html", data=data)
# end def

def html_university_application(pkey):
    gate = _gate("universities")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    rec = proc.get_row("db_program_reg", pkey)
    if rec == None:
        return "Not found", 404
    # end if
    if (rec.get("fk_program_slug") or "") != "university-fair":
        return "Not found", 404
    # end if
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        denied = _deny_post("universities", params)
        if denied != None:
            return denied
        # end if
        status = (params.get("status") or "").strip()
        if status not in proc.UNI_STATUSES:
            status = rec.get("status") or "PENDING"
        # end if
        show_campus = (params.get("show_campus") or "") in ["1", "YES", "true", "on"]
        logo = (params.get("logo") or rec.get("logo") or "").strip()
        stored, rel = proc.save_upload(request.files.get("logo_file"), "universities")
        if stored == "ERR_TYPE":
            data = proc.page("universities", {
                "row": rec,
                "statuses": proc.UNI_STATUSES,
                "form_error": "Logo must be jpg, png, or webp"
            })
            return render_template("admin_university_application.html", data=data)
        # end if
        if rel != "":
            old_logo = (rec.get("logo") or "").strip()
            logo = rel
            if old_logo != "" and old_logo != logo:
                proc.delete_local_upload(old_logo)
            # end if
        # end if
        proc.save_row("db_program_reg", pkey, {
            "full_name": (params.get("full_name") or "").strip(),
            "organization": (params.get("organization") or "").strip(),
            "email": (params.get("email") or "").strip(),
            "phone": (params.get("phone") or "").strip(),
            "city": (params.get("city") or "").strip(),
            "booth": (params.get("booth") or "").strip(),
            "notes": params.get("notes") or "",
            "logo": logo,
            "show_campus": show_campus,
            "status": status
        })
        return redirect("/admin/universities/" + pkey)
    # end if
    data = proc.page("universities", {
        "row": rec,
        "statuses": proc.UNI_STATUSES
    })
    return render_template("admin_university_application.html", data=data)
# end def

def html_payments():
    gate = _gate("payments")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        denied = _deny_post("payments", params)
        if denied != None:
            return denied
        # end if
        action = params.get("action") or ""
        if action == "transaction_account":
            source_table = (params.get("source_table") or "").strip()
            source_pkey = (params.get("source_pkey") or "").strip()
            if source_table in ["db_payment", "db_order", "db_donor"] and source_pkey != "":
                account_pkey = (params.get("fk_receive_account") or "").strip()
                account_label = ""
                if account_pkey != "":
                    account = proc.get_row("db_receive_account", account_pkey)
                    if account != None:
                        account_label = proc.receive_account_label(account)
                    else:
                        account_pkey = ""
                    # end if
                # end if
                proc.save_row(source_table, source_pkey, {
                    "fk_receive_account": account_pkey,
                    "receive_account_label": account_label
                })
            # end if
            return redirect("/admin/payments?tab=transactions")
        # end if
        if action == "status":
            proc.confirm_payment(params.get("pkey") or "", params.get("status") or "PENDING")
            return redirect("/admin/payments?tab=transactions")
        # end if
        source_type = (params.get("source_type") or "Other").strip()
        if source_type not in proc.TRANSACTION_TYPES:
            source_type = "Other"
        # end if
        transaction_kind = (params.get("transaction_kind") or "INCOME").strip().upper()
        if transaction_kind not in proc.TRANSACTION_KINDS:
            transaction_kind = "INCOME"
        # end if
        amount_num = proc.parse_int(params.get("amount"))
        if amount_num <= 0:
            return redirect("/admin/payments?tab=add&error=" + quote("Amount must be greater than zero"))
        # end if
        account_pkey = (params.get("fk_receive_account") or "").strip()
        account_label = ""
        if account_pkey != "":
            account = proc.get_row("db_receive_account", account_pkey)
            if account != None:
                account_label = proc.receive_account_label(account)
            else:
                account_pkey = ""
            # end if
        # end if
        if account_pkey == "":
            return redirect("/admin/payments?tab=add&error=" + quote("Select an account"))
        # end if
        name = params.get("name") or ""
        referral_code = params.get("referral_code") or ""
        fk_reg_id = params.get("fk_reg_id") or ""
        fk_user_id = params.get("fk_user_id") or ""
        member_pkey = (params.get("member_pkey") or "").strip()
        if member_pkey != "":
            member = proc.finance_member(member_pkey)
            if member == None:
                return redirect("/admin/payments?tab=add&error=" + quote("Selected member was not found"))
            # end if
            name = member.get("full_name") or ""
            referral_code = member.get("referral_code") or ""
            fk_reg_id = member.get("reg_id") or ""
            fk_user_id = member.get("fk_user_id") or ""
        # end if
        proc.save_row("db_payment", "", {
            "name": name,
            "email": params.get("email") or "",
            "fk_reg_id": fk_reg_id,
            "fk_user_id": fk_user_id,
            "pay_type": source_type,
            "transaction_kind": transaction_kind,
            "source_type": source_type,
            "source_ref": params.get("source_ref") or "",
            "referral_code": referral_code,
            "transaction_date": params.get("transaction_date") or "",
            "fk_receive_account": account_pkey,
            "receive_account_label": account_label,
            "amount": proc.format_rp(amount_num),
            "amount_num": amount_num,
            "method": "Transfer",
            "note": params.get("note") or "",
            "status": params.get("status") or "PAID"
        })
        return redirect("/admin/payments?tab=transactions")
    # end if
    finance_tab = (request.args.get("tab") or "summary").strip().lower()
    if finance_tab not in ["summary", "transactions", "add"]:
        finance_tab = "summary"
    # end if
    source_filter = (request.args.get("type") or "").strip()
    account_filter = (request.args.get("account") or "").strip()
    kind_filter = (request.args.get("kind") or "").strip().upper()
    if source_filter not in proc.TRANSACTION_TYPES:
        source_filter = ""
    # end if
    if kind_filter not in proc.TRANSACTION_KINDS:
        kind_filter = ""
    # end if
    transaction_data = proc.transaction_page(source_filter, account_filter, kind_filter)
    data = proc.page("payments", {
        "finance_tab": finance_tab,
        "form_error": (request.args.get("error") or "").strip(),
        "list_table": transaction_data.get("table"),
        "transaction_summary": transaction_data,
        "transaction_type_filter": source_filter,
        "transaction_account_filter": account_filter,
        "transaction_kind_filter": kind_filter,
        "receive_accounts": proc.receive_accounts(enabled_only=True),
        "statuses": proc.PAY_STATUSES,
        "types": proc.TRANSACTION_TYPES,
        "kinds": proc.TRANSACTION_KINDS,
        "finance_members": proc.finance_member_options()
    })
    return render_template("admin_payments.html", data=data)
# end def

def html_content():
    gate = _gate("content")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    data = proc.page("content", {"list_table": proc.table_content()})
    return render_template("admin_content.html", data=data)
# end def

def html_content_form(pkey=""):
    gate = _gate("content")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    rec = {}
    if pkey != "":
        rec = proc.get_row("db_update", pkey) or {}
        if rec == {}:
            return "Not found", 404
        # end if
    # end if
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        denied = _deny_post("content", params)
        if denied != None:
            return denied
        # end if
        if (params.get("action") or "") == "delete" and pkey != "":
            proc.soft_delete("db_update", pkey)
            return redirect("/admin/content")
        # end if
        title = (params.get("title") or "").strip()
        slug = (params.get("slug") or "").strip() or proc.slugify(title)
        category = (params.get("category") or "").strip()
        if category not in proc.UPDATE_CATEGORIES:
            category = proc.UPDATE_CATEGORIES[0]
        # end if
        old_image = rec.get("image") or ""
        image = (params.get("image") or "").strip()
        stored, rel = proc.save_upload(request.files.get("image_file"), "content")
        if stored == "ERR_TYPE":
            data = proc.page("content", {
                "row": params,
                "form_error": "Image must be jpg, png, or webp",
                "categories": proc.UPDATE_CATEGORIES,
                "programs": proc.list_rows("db_program", sort_field="order", direction=1)
            })
            return render_template("admin_content_form.html", data=data)
        # end if
        if rel != "":
            image = rel
        # end if
        proc.save_row("db_update", pkey, {
            "title": title,
            "slug": slug,
            "date": params.get("date") or "",
            "category": category,
            "excerpt": params.get("excerpt") or "",
            "content": params.get("content") or "",
            "image": image,
            "author": params.get("author") or "FRACO",
            "fk_program_slug": (params.get("fk_program_slug") or "").strip(),
            "status": params.get("status") or "DRAFT"
        })
        if rel != "" and old_image != "" and old_image != image:
            proc.delete_local_upload(old_image)
        # end if
        return redirect("/admin/content")
    # end if
    data = proc.page("content", {
        "row": rec,
        "categories": proc.UPDATE_CATEGORIES,
        "programs": proc.list_rows("db_program", sort_field="order", direction=1)
    })
    return render_template("admin_content_form.html", data=data)
# end def

def html_gallery():
    gate = _gate("gallery")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        denied = _deny_post("gallery", params)
        if denied != None:
            return denied
        # end if
        action = params.get("action") or "add"
        pkey = params.get("pkey") or ""
        if action == "delete" and pkey != "":
            proc.soft_delete("db_gallery", pkey)
            return redirect("/admin/gallery")
        # end if
        image = params.get("image") or ""
        file_obj = request.files.get("file")
        stored, rel = proc.save_upload(file_obj, "gallery")
        if stored == "ERR_TYPE":
            data = proc.page("gallery", {
                "list_table": proc.table_gallery(),
                "albums": proc.GALLERY_ALBUMS,
                "form_error": "Image must be jpg, png, or webp"
            })
            return render_template("admin_gallery.html", data=data)
        # end if
        if rel != "":
            image = rel
        # end if
        proc.save_row("db_gallery", pkey, {
            "image": image,
            "alt": params.get("alt") or "",
            "album": params.get("album") or "AHC 2027",
            "order": proc.parse_int(params.get("order")),
            "status": "ENABLE"
        })
        return redirect("/admin/gallery")
    # end if
    data = proc.page("gallery", {
        "list_table": proc.table_gallery(),
        "albums": proc.GALLERY_ALBUMS
    })
    return render_template("admin_gallery.html", data=data)
# end def

def html_team():
    gate = _gate("team")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        denied = _deny_post("team", params)
        if denied != None:
            return denied
        # end if
        action = params.get("action") or "save"
        pkey = params.get("pkey") or ""
        if action == "delete" and pkey != "":
            proc.soft_delete("db_team", pkey)
            return redirect("/admin/team")
        # end if
        photo = (params.get("photo") or "").strip()
        stored, rel = proc.save_upload(request.files.get("photo_file"), "team")
        if stored == "ERR_TYPE":
            data = proc.page("team", {
                "list_table": proc.table_team(),
                "form_error": "Photo must be jpg, png, or webp"
            })
            return render_template("admin_team.html", data=data)
        # end if
        if rel != "":
            photo = rel
        # end if
        proc.save_row("db_team", pkey, {
            "name": params.get("name") or "",
            "position": params.get("position") or "",
            "division": params.get("division") or "",
            "photo": photo,
            "bio": params.get("bio") or "",
            "social": params.get("social") or "",
            "order": proc.parse_int(params.get("order")),
            "status": params.get("status") or "ENABLE"
        })
        return redirect("/admin/team")
    # end if
    data = proc.page("team", {"list_table": proc.table_team()})
    return render_template("admin_team.html", data=data)
# end def

def _donations_tab():
    tab = (request.args.get("tab") or request.form.get("tab") or "").strip().lower()
    if tab not in ["settings", "pledges", "add"]:
        if (request.args.get("edit") or "").strip() != "":
            tab = "add"
        elif (request.args.get("follow") or "").strip() != "":
            tab = "pledges"
        else:
            tab = "pledges"
        # end if
    # end if
    return tab
# end def

def html_donations():
    gate = _gate("donations")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        denied = _deny_post("donations", params)
        if denied != None:
            return denied
        # end if
        action = params.get("action") or "save_donor"
        pkey = params.get("pkey") or ""
        if action == "delete" and pkey != "":
            old = proc.get_row("db_donor", pkey)
            proc.soft_delete("db_donor", pkey)
            proc.sync_donor_referrers(old)
            return redirect("/admin/donations?tab=pledges")
        # end if
        if action == "donor_follow" and pkey != "":
            proc.update_donor_follow(pkey, params.get("follow_status") or "")
            follow = (params.get("follow_filter") or request.args.get("follow") or "").strip().upper()
            href = "/admin/donations?tab=pledges"
            if follow in proc.DONOR_FOLLOW_STATUSES:
                href = href + "&follow=" + follow
            # end if
            return redirect(href)
        # end if
        if action == "donor_anonymous" and pkey != "":
            proc.update_donor_anonymous(pkey, params.get("is_anonymous") or "NO")
            follow = (params.get("follow_filter") or request.args.get("follow") or "").strip().upper()
            href = "/admin/donations?tab=pledges"
            if follow in proc.DONOR_FOLLOW_STATUSES:
                href = href + "&follow=" + follow
            # end if
            return redirect(href)
        # end if
        if action == "save_settings":
            result = proc.save_donation_settings(params)
            if result.get("status") != "SUCCESS":
                data = proc.page("donations", {
                    "donations_tab": "settings",
                    "settings": params,
                    "list_table": proc.table_donors(),
                    "edit_donor": {},
                    "form_error": result.get("desc") or "Could not save settings"
                })
                return render_template("admin_donations.html", data=data)
            # end if
            return redirect("/admin/donations?tab=settings")
        # end if
        result = proc.save_donor(pkey, params)
        if result.get("status") != "SUCCESS":
            data = proc.page("donations", {
                "donations_tab": "add",
                "settings": proc.get_donation_settings(),
                "list_table": proc.table_donors(),
                "edit_donor": params if pkey != "" else {},
                "form_error": result.get("desc") or "Could not save donor"
            })
            return render_template("admin_donations.html", data=data)
        # end if
        return redirect("/admin/donations?tab=pledges")
    # end if
    tab = _donations_tab()
    edit_pkey = (request.args.get("edit") or "").strip()
    edit_donor = {}
    if edit_pkey != "":
        edit_donor = proc.get_row("db_donor", edit_pkey) or {}
        tab = "add"
    # end if
    data = proc.page("donations", {
        "donations_tab": tab,
        "settings": proc.get_donation_settings(),
        "list_table": proc.table_donors(),
        "edit_donor": edit_donor,
        "follow_labels": proc.DONOR_FOLLOW_LABELS
    })
    return render_template("admin_donations.html", data=data)
# end def

def html_settings():
    gate = _gate("settings")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    if request.method == "POST":
        denied = _deny_post("settings")
        if denied != None:
            return denied
        # end if
        params = sanitize.clean_html_dic(request.form.to_dict())
        action = (params.get("action") or "").strip()
        if action == "shipping_config_save":
            minimum = proc.parse_int(params.get("shipping_minimum_progress_num"))
            service_fee = proc.parse_int(params.get("shipping_service_fee_num"))
            if minimum < 0:
                minimum = 0
            # end if
            if service_fee < 0:
                service_fee = 0
            # end if
            site = proc.site.get_site() or {}
            proc.mgdDB.db_site.update_one(
                {"pkey": site.get("pkey")},
                {"$set": {
                    "shipping_minimum_progress_num": minimum,
                    "shipping_service_fee_num": service_fee
                }}
            )
            return redirect("/admin/settings?tab=shipping&ok=" + quote("Shipping settings saved"))
        # end if
        if action == "merchandise_category_delete":
            category_pkey = (params.get("category_pkey") or "").strip()
            if category_pkey != "":
                proc.soft_delete("db_merchandise_category", category_pkey)
            # end if
            return redirect("/admin/settings?tab=merchandise&ok=" + quote("Merchandise category deleted") + "#merchandise-categories")
        # end if
        if action in ["merchandise_category_add", "merchandise_category_edit"]:
            category_pkey = ""
            if action == "merchandise_category_edit":
                category_pkey = (params.get("category_pkey") or "").strip()
            # end if
            result = proc.save_merchandise_category(category_pkey, params)
            if result.get("status") != "SUCCESS":
                return redirect("/admin/settings?tab=merchandise&error=" + quote(result.get("desc") or "Could not save category") + "#merchandise-categories")
            # end if
            return redirect("/admin/settings?tab=merchandise&ok=" + quote("Merchandise category saved") + "#merchandise-categories")
        # end if
        if action == "shipping_expedition_delete":
            expedition_pkey = (params.get("expedition_pkey") or "").strip()
            if expedition_pkey != "":
                proc.soft_delete("db_shipping_expedition", expedition_pkey)
            # end if
            return redirect("/admin/settings?tab=shipping&ok=" + quote("Shipping expedition deleted"))
        # end if
        if action in ["shipping_expedition_add", "shipping_expedition_edit"]:
            expedition_pkey = ""
            if action == "shipping_expedition_edit":
                expedition_pkey = (params.get("expedition_pkey") or "").strip()
            # end if
            result = proc.save_shipping_expedition(expedition_pkey, params)
            if result.get("status") != "SUCCESS":
                return redirect("/admin/settings?tab=shipping&error=" + quote(result.get("desc") or "Could not save expedition"))
            # end if
            return redirect("/admin/settings?tab=shipping&ok=" + quote("Shipping expedition saved"))
        # end if
        if action == "receive_account_delete":
            account_pkey = (params.get("account_pkey") or "").strip()
            if account_pkey != "":
                proc.soft_delete("db_receive_account", account_pkey)
            # end if
            return redirect("/admin/settings?tab=finance&ok=" + quote("Account deleted"))
        # end if
        if action in ["receive_account_add", "receive_account_edit"]:
            account_pkey = ""
            if action == "receive_account_edit":
                account_pkey = (params.get("account_pkey") or "").strip()
            # end if
            result = proc.save_receive_account(account_pkey, params)
            if result.get("status") != "SUCCESS":
                return redirect("/admin/settings?tab=finance&error=" + quote(result.get("desc") or "Could not save account"))
            # end if
            return redirect("/admin/settings?tab=finance&ok=" + quote("Account saved"))
        # end if
        if action == "support_proposal_save":
            result = proc.save_support_proposal_pdf(params, request.files.get("proposal_pdf"))
            if result.get("status") != "SUCCESS":
                return redirect("/admin/settings?tab=support&error=" + quote(result.get("desc") or "Could not save proposal PDF"))
            # end if
            return redirect("/admin/settings?tab=support&ok=" + quote("Support proposal PDF saved"))
        # end if
        if action == "import_images":
            db_stats = proc.migrate_remote_images()
            tpl_stats = proc.migrate_template_remote_images()
            msg = (
                "Imported images. DB rows updated: " + str(db_stats.get("updated")) +
                " (checked " + str(db_stats.get("checked")) + ", failed " + str(db_stats.get("failed")) + "). " +
                "Template files updated: " + str(tpl_stats.get("updated_files")) +
                " (" + str(tpl_stats.get("replacements")) + " replacements, failed " + str(tpl_stats.get("failed")) + ")."
            )
            return redirect("/admin/settings?tab=images&ok=" + quote(msg))
        # end if
        site = proc.site.get_site()
        contribution_num = proc.parse_int(params.get("contribution_num"))
        if contribution_num < 0:
            contribution_num = 0
        # end if
        contribution = proc.unescape_value(params.get("contribution") or "").strip()
        if contribution == "" and contribution_num > 0:
            contribution = proc.format_rp(contribution_num)
        # end if
        if contribution == "":
            contribution = "Rp 0"
        # end if
        proc.mgdDB.db_site.update_one(
            {"pkey": site.get("pkey")},
            {"$set": {
                "announcement": proc.unescape_value(params.get("announcement") or ""),
                "announcement_id": proc.unescape_value(params.get("announcement_id") or ""),
                "tagline": proc.unescape_value(params.get("tagline") or ""),
                "tagline_id": proc.unescape_value(params.get("tagline_id") or ""),
                "subtitle": proc.unescape_value(params.get("subtitle") or ""),
                "subtitle_id": proc.unescape_value(params.get("subtitle_id") or ""),
                "description": proc.unescape_value(params.get("description") or ""),
                "description_id": proc.unescape_value(params.get("description_id") or ""),
                "presented_by": proc.unescape_value(params.get("presented_by") or ""),
                "presented_by_id": proc.unescape_value(params.get("presented_by_id") or ""),
                "phone": proc.unescape_value(params.get("phone") or ""),
                "whatsapp_url": proc.unescape_value(params.get("whatsapp_url") or ""),
                "contribution": contribution,
                "contribution_num": contribution_num
            }}
        )
        return redirect("/admin/settings?tab=website")
    # end if
    form_ok = (request.args.get("ok") or "").strip()
    form_error = (request.args.get("error") or "").strip()
    settings_tab = (request.args.get("tab") or "website").strip().lower()
    if settings_tab not in ["website", "merchandise", "finance", "shipping", "images", "support"]:
        settings_tab = "website"
    # end if
    site = proc.site.get_site() or {}
    shipping_minimum = site.get("shipping_minimum_progress_num")
    if shipping_minimum == None:
        shipping_minimum = 100000
    # end if
    shipping_service_fee = site.get("shipping_service_fee_num")
    if shipping_service_fee == None:
        shipping_service_fee = 10000
    # end if
    data = proc.page("settings", {
        "settings_tab": settings_tab,
        "form_ok": form_ok,
        "form_error": form_error,
        "merchandise_categories": proc.merchandise_category_rows(False),
        "shipping_expeditions": proc.shipping_expedition_rows(False),
        "shipping_minimum_progress_num": shipping_minimum,
        "shipping_service_fee_num": shipping_service_fee,
        "receive_accounts": proc.receive_accounts(),
        "announcement": site.get("announcement") or "",
        "announcement_id": site.get("announcement_id") or "",
        "tagline": site.get("tagline") or "",
        "tagline_id": site.get("tagline_id") or "",
        "subtitle": site.get("subtitle") or "",
        "subtitle_id": site.get("subtitle_id") or "",
        "description": site.get("description") or "",
        "description_id": site.get("description_id") or "",
        "presented_by": site.get("presented_by") or "",
        "presented_by_id": site.get("presented_by_id") or "",
        "phone": site.get("phone") or "",
        "whatsapp_url": site.get("whatsapp_url") or "",
        "contribution": site.get("contribution") or "",
        "contribution_num": site.get("contribution_num") or 2000000,
        "donation_settings": proc.get_donation_settings()
    })
    return render_template("admin_settings.html", data=data)
# end def

def html_users():
    gate = _gate("users")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    extra = proc.table_users()
    data = proc.page("users", extra)
    return render_template("admin_users.html", data=data)
# end def

def html_user_form(pkey=""):
    gate = _gate("users")
    if gate != None:
        return gate
    # end if
    proc = admin_proc()
    admin = proc.current_admin()
    rec = {}
    if pkey != "":
        rec = proc.get_row("db_user", pkey) or {}
        if rec == {} or proc.staff_role(rec.get("role")) == "":
            return "Not found", 404
        # end if
        rec["role_kind"] = proc.staff_role(rec.get("role"))
    # end if
    if request.method == "POST":
        params = sanitize.clean_html_dic(request.form.to_dict())
        raw = request.form.get("password") or ""
        if (params.get("action") or "") == "deactivate" and pkey != "":
            result = proc.deactivate_staff_user(admin, pkey)
            if result.get("status") == "SUCCESS":
                return redirect("/admin/users")
            # end if
            rec = proc.get_row("db_user", pkey) or rec
            rec["role_kind"] = proc.staff_role(rec.get("role"))
            data = proc.page("users", {
                "row": rec,
                "roles": proc.STAFF_ROLES,
                "form_error": result.get("desc", "")
            })
            return render_template("admin_user_form.html", data=data)
        # end if
        result = proc.save_staff_user(admin, pkey, params, raw)
        if result.get("status") == "SUCCESS":
            return redirect("/admin/users")
        # end if
        rec = {
            "pkey": pkey,
            "name": params.get("name") or "",
            "email": params.get("email") or "",
            "phone": params.get("phone") or "",
            "role": params.get("role") or "OFFICER",
            "status": params.get("status") or "ENABLE"
        }
        rec["role_kind"] = proc.staff_role(rec.get("role"))
        data = proc.page("users", {
            "row": rec,
            "roles": proc.STAFF_ROLES,
            "form_error": result.get("desc", "")
        })
        return render_template("admin_user_form.html", data=data)
    # end if
    data = proc.page("users", {"row": rec, "roles": proc.STAFF_ROLES})
    return render_template("admin_user_form.html", data=data)
# end def
