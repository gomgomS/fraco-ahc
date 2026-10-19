import sys
import re
import time
import uuid

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from flask import has_request_context, session
from slapz102_core import database
from slapz102_core import config
from ahc_site.ahc_site_proc import ahc_site_proc
from merchandise.merchandise_proc import merchandise_proc
from address.address_proc import address_proc

class cart_proc:

    mgdDB = database.get_db_conn(config.mainDB)

    def __init__(self, app=None):
        self.webapp = app
        self.site = ahc_site_proc(app)
        self.merch = merchandise_proc(app)
        self.address = address_proc(app)
    # end def

    def format_rp(self, amount):
        n = int(amount or 0)
        if n <= 0:
            return "Rp 0"
        # end if
        text = "{:,}".format(n).replace(",", ".")
        return "Rp " + text
    # end def

    def get_session_id(self, create=True):
        if not has_request_context():
            return ""
        # end if
        sid = session.get("cart_sid", "")
        if sid == "" and create:
            sid = str(uuid.uuid4())
            session["cart_sid"] = sid
        # end if
        return sid
    # end def

    def get_cart_rows(self):
        sid = self.get_session_id(False)
        if sid == "":
            return []
        # end if
        recs = list(self.mgdDB.db_cart.find(
            {"session_id": sid, "is_deleted": False},
            {"_id": 0}
        ))
        return recs
    # end def

    def decorate_rows(self, rows):
        items = []
        subtotal = 0
        profit_total = 0
        bahan_total = 0
        for row in rows:
            product = self.merch.get_product(row.get("slug", ""))
            if product == None:
                continue
            # end if
            qty = int(row.get("qty", 1))
            unit = int(product.get("price_num", 0))
            bahan = int(product.get("bahan_baku_num") or 0)
            if bahan < 0:
                bahan = 0
            # end if
            unit_profit = unit - bahan
            if unit_profit < 0:
                unit_profit = 0
            # end if
            line = unit * qty
            line_bahan = bahan * qty
            line_profit = unit_profit * qty
            subtotal = subtotal + line
            bahan_total = bahan_total + line_bahan
            profit_total = profit_total + line_profit
            items.append({
                "pkey": row.get("pkey", ""),
                "product_pkey": product.get("pkey", ""),
                "slug": row.get("slug", ""),
                "name": product.get("name", ""),
                "image": product.get("image", ""),
                "size": row.get("size", ""),
                "color": row.get("color", ""),
                "qty": qty,
                "sku": (product.get("sku") or "").strip(),
                "is_preorder": self.merch.is_preorder(product),
                "preorder_eta": (product.get("preorder_eta") or "").strip(),
                "preorder_note": (product.get("preorder_note") or "").strip(),
                "discount": (product.get("discount") or "").strip(),
                "discount_type": (product.get("discount_type") or "PCT").strip().upper() or "PCT",
                "discount_num": int(product.get("discount_num") or 0),
                "discount_note": (product.get("discount_note") or "").strip(),
                "discount_enabled": self.discount_is_enabled(product),
                "unit_price": self.format_rp(unit),
                "unit_price_num": unit,
                "unit_bahan_baku": self.format_rp(bahan),
                "unit_bahan_baku_num": bahan,
                "unit_profit": self.format_rp(unit_profit),
                "unit_profit_num": unit_profit,
                "line_price": self.format_rp(line),
                "line_num": line,
                "line_bahan_baku": self.format_rp(line_bahan),
                "line_bahan_baku_num": line_bahan,
                "line_profit": self.format_rp(line_profit),
                "line_profit_num": line_profit,
                "line_status": "Preorder" if self.merch.is_preorder(product, row.get("size") or "") else "Pending Payment"
            })
        # end for
        return items, subtotal, bahan_total, profit_total
    # end def

    def parse_product_discount(self, product_or_item):
        row = product_or_item or {}
        dtype = (row.get("discount_type") or "").strip().upper()
        try:
            dnum = int(row.get("discount_num") or 0)
        except Exception:
            dnum = 0
        # end try
        if dnum < 0:
            dnum = 0
        # end if
        if dnum <= 0:
            raw = (row.get("discount") or "").strip().replace(" ", "")
            if raw.endswith("%"):
                dtype = "PCT"
                try:
                    dnum = int(re.sub(r"[^0-9]", "", raw[:-1]) or 0)
                except Exception:
                    dnum = 0
                # end try
            elif raw.lower().startswith("rp"):
                dtype = "FIXED"
                try:
                    dnum = int(re.sub(r"[^0-9]", "", raw) or 0)
                except Exception:
                    dnum = 0
                # end try
            elif re.sub(r"[^0-9]", "", raw) != "":
                try:
                    dnum = int(re.sub(r"[^0-9]", "", raw) or 0)
                except Exception:
                    dnum = 0
                # end try
                if dtype not in ["PCT", "FIXED"]:
                    dtype = "PCT" if dnum <= 100 else "FIXED"
                # end if
            # end if
        # end if
        if dtype not in ["PCT", "FIXED"]:
            dtype = "PCT"
        # end if
        if dtype == "PCT" and dnum > 100:
            dnum = 100
        # end if
        note = (row.get("discount_note") or "").strip()
        # Optional: referral can credit a member without any buyer discount.
        enabled = self.discount_is_enabled(row)
        if not enabled:
            dnum = 0
        # end if
        return {"type": dtype, "num": dnum, "note": note, "enabled": enabled}
    # end def

    def discount_is_enabled(self, product_or_item):
        row = product_or_item or {}
        flag = row.get("discount_enabled")
        if flag == True or flag in ["1", "YES", "true", "on", "True"]:
            return True
        # end if
        if flag == False or flag in ["0", "NO", "false", "off", "False"]:
            return False
        # end if
        # Legacy products (no flag yet): keep discount if a value was already saved
        try:
            return int(row.get("discount_num") or 0) > 0
        except Exception:
            return False
        # end try
    # end def

    def unit_referral_amount(self, product_or_item):
        # Rupiah off per unit from product referral discount (buyer price only).
        row = product_or_item or {}
        unit = int(row.get("unit_price_num") or row.get("price_num") or 0)
        if unit < 0:
            unit = 0
        # end if
        spec = self.parse_product_discount(row)
        dtype = spec["type"]
        dnum = spec["num"]
        amount = 0
        label = ""
        if dnum <= 0 or unit <= 0:
            return {
                "amount": 0,
                "label": "",
                "type": dtype,
                "num": 0,
                "note": spec["note"]
            }
        # end if
        if dtype == "FIXED":
            amount = dnum
            if amount > unit:
                amount = unit
            # end if
            label = self.format_rp(dnum) + " off / unit"
        else:
            amount = int(round(unit * dnum / 100.0))
            if amount > unit:
                amount = unit
            # end if
            label = str(dnum) + "%"
        # end if
        return {
            "amount": amount,
            "label": label,
            "type": dtype,
            "num": dnum,
            "note": spec["note"]
        }
    # end def

    def line_referral_amount(self, item):
        qty = int(item.get("qty") or 1)
        if qty < 1:
            qty = 1
        # end if
        line_num = int(item.get("line_num") or 0)
        unit_info = self.unit_referral_amount(item)
        amount = int(unit_info["amount"] or 0) * qty
        if amount > line_num and line_num > 0:
            amount = line_num
        # end if
        if int(unit_info["num"] or 0) <= 0 or amount <= 0:
            return {
                "amount": 0,
                "label": "",
                "type": unit_info["type"],
                "num": 0,
                "note": unit_info["note"]
            }
        # end if
        return {
            "amount": amount,
            "label": unit_info["label"],
            "type": unit_info["type"],
            "num": unit_info["num"],
            "note": unit_info["note"]
        }
    # end def

    def profit_after_unit_discount(self, unit_profit, unit_discount):
        # Discount cuts member/org profit only — bahan baku stays unchanged.
        base = int(unit_profit or 0)
        disc = int(unit_discount or 0)
        if base < 0:
            base = 0
        # end if
        if disc < 0:
            disc = 0
        # end if
        after = base - disc
        if after < 0:
            after = 0
        # end if
        return after
    # end def

    def adjust_items_profit_for_referral(self, items, apply_referral):
        # When referral discount applies, subtract it from line profit (not bahan).
        profit_total = 0
        for item in items or []:
            unit_profit = int(item.get("unit_profit_num") or 0)
            qty = int(item.get("qty") or 1)
            if qty < 1:
                qty = 1
            # end if
            unit_disc = 0
            if apply_referral:
                unit_disc = int(self.unit_referral_amount(item).get("amount") or 0)
            # end if
            unit_after = self.profit_after_unit_discount(unit_profit, unit_disc)
            line_after = unit_after * qty
            item["unit_profit_num"] = unit_after
            item["unit_profit"] = self.format_rp(unit_after)
            item["line_profit_num"] = line_after
            item["line_profit"] = self.format_rp(line_after)
            item["unit_discount_num"] = unit_disc
            item["line_discount_num"] = unit_disc * qty
            profit_total = profit_total + line_after
        # end for
        return profit_total
    # end def

    def referral_discount_preview(self, items):
        labels = []
        notes = []
        potential = 0
        for item in items or []:
            info = self.line_referral_amount(item)
            if info["amount"] <= 0:
                continue
            # end if
            potential = potential + info["amount"]
            name = item.get("name") or "Item"
            labels.append(name + " · " + info["label"])
            if info["note"] != "" and info["note"] not in notes:
                notes.append(info["note"])
            # end if
        # end for
        return {
            "labels": labels,
            "notes": notes,
            "potential_num": potential,
            "potential": self.format_rp(potential),
            "has_discount": potential > 0
        }
    # end def

    def find_referrer(self, code):
        clean = re.sub(r"[^a-zA-Z0-9]", "", (code or "").strip().lower())
        if clean == "":
            return None
        # end if
        return self.mgdDB.db_participant.find_one({
            "referral_code": clean,
            "member_type": "AHC_MEMBER",
            "is_deleted": False
        }, {"_id": 0})
    # end def

    def calc_totals(self, subtotal, referral_code="", items=None):
        # Referral discount comes only from each product (admin product form).
        general_pct = 0
        general_num = 0
        referral_pct = 0
        referral_num = 0
        referrer = None
        code = re.sub(r"[^a-zA-Z0-9]", "", (referral_code or "").strip().lower())
        preview = self.referral_discount_preview(items or [])
        if code != "":
            referrer = self.find_referrer(code)
            if referrer != None:
                for item in items or []:
                    info = self.line_referral_amount(item)
                    referral_num = referral_num + info["amount"]
                    if info["type"] == "PCT" and info["num"] > referral_pct:
                        referral_pct = info["num"]
                    # end if
                # end for
            # end if
        # end if
        discount_total = general_num + referral_num
        if discount_total > subtotal:
            discount_total = subtotal
        # end if
        total = subtotal - discount_total
        if total < 0:
            total = 0
        # end if
        return {
            "general_pct": general_pct,
            "general_num": general_num,
            "referral_pct": referral_pct,
            "referral_num": referral_num,
            "discount_total_num": discount_total,
            "total_num": total,
            "referral_code": code if referrer != None else "",
            "referrer": referrer,
            "referral_preview": preview
        }
    # end def

    def get_cart_page(self, message=""):
        rows = self.get_cart_rows()
        items, subtotal, bahan_total, profit_total = self.decorate_rows(rows)
        has_preorder = False
        preorder_eta = ""
        for item in items:
            if item.get("is_preorder"):
                has_preorder = True
                if preorder_eta == "" and (item.get("preorder_eta") or "") != "":
                    preorder_eta = item.get("preorder_eta")
                # end if
            # end if
        # end for
        return self.site.with_site({
            "cart_items": items,
            "subtotal": self.format_rp(subtotal),
            "subtotal_num": subtotal,
            "bahan_baku_total": self.format_rp(bahan_total),
            "bahan_baku_total_num": bahan_total,
            "profit_total": self.format_rp(profit_total),
            "profit_total_num": profit_total,
            "has_preorder": has_preorder,
            "preorder_eta": preorder_eta,
            "shipping": "Confirmed after order",
            "total": self.format_rp(subtotal),
            "cart_message": message
        })
    # end def

    def add_item(self, params):
        response = {"status": "FAILED", "desc": ""}
        slug = (params.get("slug") or "").strip()
        product = self.merch.get_product(slug)
        if not self.merch.can_buy(product):
            response["desc"] = "This item cannot be added to the bag"
            return response
        # end if
        size = (params.get("size") or "").strip()
        color = (params.get("color") or "").strip()
        try:
            qty = int(params.get("qty") or 1)
        except Exception:
            qty = 1
        # end try
        if qty < 1:
            qty = 1
        # end if
        sizes = product.get("sizes") or []
        if sizes != [] and size == "":
            size = sizes[0]
        # end if
        colors = product.get("colors") or []
        if colors != [] and color == "":
            color = colors[0]
        # end if
        if not self.merch.can_buy(product, size):
            response["desc"] = "This size is not available"
            return response
        # end if
        sid = self.get_session_id(True)
        existing = self.mgdDB.db_cart.find_one({
            "session_id": sid,
            "slug": slug,
            "size": size,
            "color": color,
            "is_deleted": False
        })
        stock = self.merch.buy_limit(product, size)
        if stock <= 0:
            response["desc"] = "This size is not available"
            return response
        # end if
        if existing != None:
            new_qty = int(existing.get("qty", 1)) + qty
            if new_qty > stock:
                new_qty = stock
            # end if
            self.mgdDB.db_cart.update_one(
                {"pkey": existing.get("pkey")},
                {"$set": {"qty": new_qty}}
            )
        else:
            if qty > stock:
                qty = stock
            # end if
            rec = database.new(self.mgdDB, "db_cart")
            rec.put("session_id", sid)
            rec.put("fk_user_id", "")
            rec.put("fk_product_id", product.get("pkey", ""))
            rec.put("slug", slug)
            rec.put("qty", qty)
            rec.put("size", size)
            rec.put("color", color)
            rec.insert()
        # end if
        response["status"] = "SUCCESS"
        response["desc"] = "Added to bag"
        return response
    # end def

    def update_item(self, params):
        response = {"status": "FAILED", "desc": ""}
        pkey = (params.get("pkey") or "").strip()
        sid = self.get_session_id(False)
        try:
            qty = int(params.get("qty") or 0)
        except Exception:
            qty = 0
        # end try
        row = self.mgdDB.db_cart.find_one({
            "pkey": pkey,
            "session_id": sid,
            "is_deleted": False
        })
        if row == None:
            response["desc"] = "Item not found"
            return response
        # end if
        if qty <= 0:
            self.mgdDB.db_cart.update_one(
                {"pkey": pkey},
                {"$set": {"is_deleted": True}}
            )
        else:
            product = self.merch.get_product(row.get("slug", ""))
            stock = self.merch.buy_limit(product, row.get("size") or "")
            if stock <= 0:
                stock = 1
            # end if
            if qty > stock:
                qty = stock
            # end if
            self.mgdDB.db_cart.update_one(
                {"pkey": pkey},
                {"$set": {"qty": qty}}
            )
        # end if
        response["status"] = "SUCCESS"
        return response
    # end def

    def remove_item(self, params):
        params["qty"] = "0"
        return self.update_item(params)
    # end def

    def get_checkout_page(self, error="", referral_code=""):
        data = self.get_cart_page()
        items = data.get("cart_items") or []
        subtotal = int(data.get("subtotal_num") or 0)
        code_raw = (referral_code or "").strip()
        totals = self.calc_totals(subtotal, code_raw, items)
        preview = totals.get("referral_preview") or {}
        data["form_error"] = error
        data["referral_code"] = totals.get("referral_code") or ""
        data["discount_general_pct"] = totals["general_pct"]
        data["discount_general"] = self.format_rp(totals["general_num"])
        data["discount_general_num"] = int(totals.get("general_num") or 0)
        data["discount_referral_pct"] = totals["referral_pct"]
        data["discount_referral"] = self.format_rp(totals["referral_num"])
        data["discount_referral_num"] = int(totals.get("referral_num") or 0)
        data["discount_referral_applied"] = totals["referrer"] != None and int(totals.get("referral_num") or 0) > 0
        data["discount_total"] = self.format_rp(totals["discount_total_num"])
        data["discount_total_num"] = totals["discount_total_num"]
        data["total"] = self.format_rp(totals["total_num"])
        data["total_num"] = totals["total_num"]
        data["referral_valid"] = totals["referrer"] != None
        data["referral_preview"] = preview
        data["referrer_name"] = ""
        if totals["referrer"] != None:
            data["referrer_name"] = totals["referrer"].get("full_name") or ""
        # end if
        # Invalid typed code: keep it visible so the form can show an error hint
        if code_raw != "" and totals["referrer"] == None:
            data["referral_code"] = code_raw
        # end if
        return data
    # end def

    def credit_referrer_sale(self, referrer, sale_num):
        if referrer == None:
            return
        # end if
        sale = int(sale_num or 0)
        if sale <= 0:
            return
        # end if
        pkey = referrer.get("pkey")
        sold = int(referrer.get("sales_total_num") or 0) + sale
        count = int(referrer.get("sales_count") or 0) + 1
        self.mgdDB.db_participant.update_one(
            {"pkey": pkey},
            {"$set": {
                "sales_total_num": sold,
                "sales_total": self.format_rp(sold),
                "sales_count": count
            }}
        )
    # end def

    def place_order(self, params):
        response = {"status": "FAILED", "desc": "", "order_id": ""}
        rows = self.get_cart_rows()
        items, subtotal, bahan_total, profit_total = self.decorate_rows(rows)
        if items == []:
            response["desc"] = "Your bag is empty"
            return response
        # end if
        full_name = (params.get("full_name") or "").strip()
        email = (params.get("email") or "").strip()
        phone = (params.get("phone") or "").strip()
        addr = self.address.collect(params)
        addr_check = self.address.validate(addr)
        if full_name == "" or email == "" or phone == "":
            response["desc"] = "Name, email, and phone are required"
            return response
        # end if
        if addr_check.get("status") != "SUCCESS":
            response["desc"] = addr_check.get("desc") or "Alamat pengiriman belum lengkap"
            return response
        # end if
        referral_raw = (params.get("referral_code") or "").strip()
        totals = self.calc_totals(subtotal, referral_raw, items)
        if referral_raw != "" and totals["referrer"] == None:
            response["desc"] = "Referral code not found. Leave it blank or use a valid AHC member code."
            return response
        # end if
        sid = self.get_session_id(False)
        order_id = "FR" + str(int(time.time()))
        referrer = totals["referrer"]
        has_preorder = False
        preorder_eta = ""
        for item in items:
            if item.get("is_preorder"):
                has_preorder = True
                if preorder_eta == "" and (item.get("preorder_eta") or "") != "":
                    preorder_eta = item.get("preorder_eta")
                # end if
            # end if
        # end for
        order_status = "Pending Payment"
        if has_preorder:
            order_status = "Preorder"
        # end if
        apply_referral = referrer != None and int(totals.get("referral_num") or 0) > 0
        profit_total = self.adjust_items_profit_for_referral(items, apply_referral)
        rec = database.new(self.mgdDB, "db_order")
        rec.put("order_id", order_id)
        rec.put("session_id", sid)
        rec.put("fk_user_id", "")
        rec.put("items", items)
        rec.put("subtotal", self.format_rp(subtotal))
        rec.put("subtotal_num", subtotal)
        rec.put("bahan_baku_total", self.format_rp(bahan_total))
        rec.put("bahan_baku_total_num", bahan_total)
        rec.put("profit_total", self.format_rp(profit_total))
        rec.put("profit_total_num", profit_total)
        rec.put("has_preorder", has_preorder)
        rec.put("preorder_eta", preorder_eta)
        rec.put("shipping", "Confirmed after order")
        rec.put("shipping_num", 0)
        rec.put("discount_general_pct", totals["general_pct"])
        rec.put("discount_general_num", totals["general_num"])
        rec.put("discount_referral_pct", totals["referral_pct"])
        rec.put("discount_referral_num", totals["referral_num"])
        rec.put("discount_total", self.format_rp(totals["discount_total_num"]))
        rec.put("discount_total_num", totals["discount_total_num"])
        rec.put("total", self.format_rp(totals["total_num"]))
        rec.put("total_num", totals["total_num"])
        rec.put("referral_code", totals["referral_code"])
        rec.put("fk_referrer_id", (referrer or {}).get("pkey") or "")
        rec.put("fk_referrer_reg_id", (referrer or {}).get("reg_id") or "")
        rec.put("full_name", full_name)
        rec.put("email", email)
        rec.put("phone", phone)
        rec.put("address", addr.get("address") or "")
        rec.put("street", addr.get("street") or "")
        rec.put("address_detail", addr.get("address_detail") or "")
        rec.put("province", addr.get("province") or "")
        rec.put("province_id", addr.get("province_id") or "")
        rec.put("city", addr.get("city") or "")
        rec.put("city_id", addr.get("city_id") or "")
        rec.put("district", addr.get("district") or "")
        rec.put("district_id", addr.get("district_id") or "")
        rec.put("village", addr.get("village") or "")
        rec.put("village_id", addr.get("village_id") or "")
        rec.put("postal_code", addr.get("postal_code") or "")
        rec.put("notes", (params.get("notes") or "").strip())
        rec.put("payment_status", "Pending")
        rec.put("order_status", order_status)
        rec.insert()
        self.credit_referrer_sale(referrer, profit_total)
        self.mgdDB.db_cart.update_many(
            {"session_id": sid, "is_deleted": False},
            {"$set": {"is_deleted": True}}
        )
        response["status"] = "SUCCESS"
        response["order_id"] = order_id
        return response
    # end def

    def get_order_page(self, order_id):
        sid = self.get_session_id(False)
        rec = self.mgdDB.db_order.find_one(
            {"order_id": order_id, "session_id": sid, "is_deleted": False},
            {"_id": 0}
        )
        if rec == None:
            return None
        # end if
        return self.site.with_site({
            "order": rec
        })
    # end def
# end class
