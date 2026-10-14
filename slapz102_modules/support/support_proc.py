import sys

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

import os
import re
import time
from slapz102_core import database
from slapz102_core import config
from ahc_site.ahc_site_proc import ahc_site_proc

class support_proc:

    mgdDB = database.get_db_conn(config.mainDB)

    def __init__(self, app=None):
        self.webapp = app
        self.site = ahc_site_proc(app)
    # end def

    def default_settings(self):
        return {
            "title": "Support Us",
            "intro": "",
            "email": "",
            "whatsapp": "",
            "whatsapp_url": "",
            "phone": "",
            "follow_up_note": "",
            "top_limit": 10,
            "list_mode": "LIMIT",
            "public_total_mode": "ACCUMULATED",
            "public_total_num": 0,
            "proposal_pdf_url": "",
            "proposal_pdf_label": "Download proposal (PDF)",
            "status": "ENABLE"
        }
    # end def

    def resolve_proposal_pdf_path(self):
        url = (self.get_settings().get("proposal_pdf_url") or "").strip()
        if url == "":
            return None
        # end if
        prefix = config.G_UPLOAD_URL_PATH + "/"
        path = url.replace("\\", "/")
        if path.find(prefix) != 0:
            return None
        # end if
        rel = path[len(prefix):].lstrip("/")
        parts = rel.split("/")
        if rel == "" or ".." in parts:
            return None
        # end if
        full = os.path.join(config.G_UPLOAD_PATH, *parts)
        if os.path.isfile(full):
            return full
        # end if
        return None
    # end def

    def get_settings(self):
        rec = self.mgdDB.db_donation_settings.find_one(
            {"is_deleted": False},
            {"_id": 0}
        )
        if rec == None:
            fields = self.default_settings()
            row = database.new(self.mgdDB, "db_donation_settings")
            for key in fields:
                row.put(key, fields[key])
            # end for
            row.insert()
            rec = row.get()
            if "_id" in rec:
                del rec["_id"]
            # end if
            if "__db__name__" in rec:
                del rec["__db__name__"]
            # end if
        # end if
        return rec
    # end def

    def parse_amount(self, value):
        digits = re.sub(r"[^0-9]", "", str(value or "0"))
        if digits == "":
            return 0
        # end if
        return int(digits)
    # end def

    def format_rp(self, amount):
        n = int(amount or 0)
        if n <= 0:
            return ""
        # end if
        text = "{:,}".format(n).replace(",", ".")
        return "Rp " + text
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

    def check_referral_code(self, code):
        clean = re.sub(r"[^a-zA-Z0-9]", "", (code or "").strip().lower())
        if clean == "":
            return {
                "status": "SUCCESS",
                "desc": "Optional - leave blank if none",
                "valid": True,
                "empty": True,
                "code": "",
                "referrer_name": ""
            }
        # end if
        referrer = self.find_referrer(clean)
        if referrer == None:
            return {
                "status": "FAILED",
                "desc": "Referral code not found. Check the code or leave it blank.",
                "valid": False,
                "empty": False,
                "code": clean,
                "referrer_name": ""
            }
        # end if
        return {
            "status": "SUCCESS",
            "desc": "Valid - referred by " + (referrer.get("full_name") or clean),
            "valid": True,
            "empty": False,
            "code": (referrer.get("referral_code") or clean),
            "referrer_name": referrer.get("full_name") or ""
        }
    # end def

    def normalize_phone(self, phone):
        return re.sub(r"[^0-9]", "", str(phone or ""))
    # end def

    def find_recent_duplicate(self, name, phone, amount_num, referral_code="", window_ms=120000):
        phone_digits = self.normalize_phone(phone)
        name_clean = (name or "").strip().lower()
        code = (referral_code or "").strip().lower()
        if phone_digits == "" and name_clean == "":
            return None
        # end if
        since = int(time.time() * 1000) - int(window_ms)
        for item in self.mgdDB.db_donor.find(
            {
                "is_deleted": False,
                "amount_num": int(amount_num or 0),
                "rec_timestamp": {"$gte": since}
            },
            {"_id": 0}
        ).sort("rec_timestamp", -1):
            same_phone = phone_digits != "" and self.normalize_phone(item.get("phone")) == phone_digits
            same_name = name_clean != "" and (item.get("name") or "").strip().lower() == name_clean
            same_ref = (item.get("referral_code") or "").strip().lower() == code
            if (same_phone or same_name) and same_ref:
                return item
            # end if
        # end for
        return None
    # end def

    def save_pledge(self, params):
        name = (params.get("name") or "").strip()
        phone = (params.get("phone") or "").strip()
        commitment = (params.get("commitment") or "").strip()
        referral_raw = (params.get("referral_code") or params.get("referred_by") or "").strip()
        if name == "":
            return {"status": "FAILED", "desc": "Name is required", "field": "name"}
        # end if
        if phone == "":
            return {"status": "FAILED", "desc": "Phone number is required", "field": "phone"}
        # end if
        if commitment == "":
            return {"status": "FAILED", "desc": "Total commitment is required", "field": "commitment"}
        # end if
        amount_num = self.parse_amount(commitment)
        amount_label = commitment
        if amount_num > 0 and commitment.lower().find("rp") < 0:
            amount_label = self.format_rp(amount_num) or commitment
        # end if
        referral_code = ""
        fk_referrer_id = ""
        fk_referrer_reg_id = ""
        if referral_raw != "":
            check = self.check_referral_code(referral_raw)
            if check.get("valid") != True:
                return {
                    "status": "FAILED",
                    "desc": check.get("desc") or "Referral code not found",
                    "field": "referral_code"
                }
            # end if
            referrer = self.find_referrer(referral_raw)
            referral_code = (referrer.get("referral_code") or "").lower()
            fk_referrer_id = referrer.get("pkey") or ""
            fk_referrer_reg_id = referrer.get("reg_id") or ""
        # end if
        dup = self.find_recent_duplicate(name, phone, amount_num, referral_code)
        if dup != None:
            return {"status": "SUCCESS", "desc": "Already received", "duplicate": True}
        # end if
        rec = database.new(self.mgdDB, "db_donor")
        rec.put("name", name)
        rec.put("phone", phone)
        rec.put("amount_label", amount_label)
        rec.put("amount_num", amount_num)
        rec.put("score", amount_num)
        rec.put("note", "")
        rec.put("referral_code", referral_code)
        rec.put("fk_referrer_id", fk_referrer_id)
        rec.put("fk_referrer_reg_id", fk_referrer_reg_id)
        rec.put("pledge_source", "PUBLIC")
        rec.put("follow_status", "FOLLOW_UP")
        rec.put("status", "HIDDEN")
        rec.insert()
        return {"status": "SUCCESS"}
    # end def

    def is_self_pledge(self, item):
        if item == None:
            return False
        # end if
        if (item.get("pledge_source") or "").strip().upper() == "SELF":
            return True
        # end if
        note = (item.get("note") or "").lower()
        return note.find("self pledge") >= 0
    # end def

    def list_donors(self, enabled_only=True):
        query = {
            "is_deleted": False,
            "follow_status": "RECEIVED"
        }
        if enabled_only:
            query["status"] = "ENABLE"
        # end if
        return list(self.mgdDB.db_donor.find(query, {"_id": 0}).sort([
            ("score", -1),
            ("amount_num", -1),
            ("name", 1)
        ]))
    # end def

    def top_donors(self, settings=None):
        if settings == None:
            settings = self.get_settings()
        # end if
        donors = self.list_donors(True)
        mode = (settings.get("list_mode") or "LIMIT").upper()
        limit = int(settings.get("top_limit") or 0)
        show_all = mode == "ALL" or limit <= 0
        if show_all:
            return donors, True
        # end if
        return donors[:limit], False
    # end def

    def decorate_donor(self, item, site=None):
        row = dict(item)
        if item.get("is_anonymous") == True:
            row["name"] = "Anonymous"
        # end if
        is_member = self.is_self_pledge(item)
        row["is_member"] = is_member
        row["member_badge"] = ""
        if is_member:
            year = ""
            label = ""
            if site != None:
                year = (site.get("graduation_year") or "").strip()
                label = (site.get("class_label") or "").strip()
            # end if
            if label != "":
                row["member_badge"] = label
            elif year != "":
                row["member_badge"] = "Class of " + year
            else:
                row["member_badge"] = "AHC classmate"
            # end if
        # end if
        return row
    # end def

    def get_support_social_proof(self, settings=None):
        if settings == None:
            settings = self.get_settings()
        # end if
        donors = list(self.mgdDB.db_donor.find(
            {
                "is_deleted": False,
                "follow_status": "RECEIVED",
                "status": "ENABLE"
            },
            {
                "_id": 0,
                "name": 1,
                "is_anonymous": 1,
                "amount_label": 1,
                "amount_num": 1,
                "rec_timestamp": 1
            }
        ).sort("rec_timestamp", -1))
        total_num = 0
        ticker = []
        for item in donors:
            total_num = total_num + int(item.get("amount_num") or 0)
            if len(ticker) < 16:
                ticker.append({
                    "name": "Anonymous" if item.get("is_anonymous") == True else (item.get("name") or "FRACO supporter"),
                    "amount": item.get("amount_label") or self.format_rp(item.get("amount_num")) or "Support"
                })
            # end if
        # end for
        total_mode = (settings.get("public_total_mode") or "ACCUMULATED").strip().upper()
        if total_mode not in ["ACCUMULATED", "CUSTOM", "HIDDEN"]:
            total_mode = "ACCUMULATED"
        # end if
        display_total = total_num
        if total_mode == "CUSTOM":
            display_total = int(settings.get("public_total_num") or 0)
        # end if
        return {
            "supporter_count": len(donors),
            "total": self.format_rp(display_total) or "Rp 0",
            "total_mode": total_mode,
            "show_total": total_mode != "HIDDEN",
            "ticker": ticker
        }
    # end def

    def get_support_page(self, form_ok=False, form_error="", form_values=None, form_field=""):
        settings = self.get_settings()
        site = self.site.get_site() or {}
        donors, show_all = self.top_donors(settings)
        ranked = []
        rank = 1
        for item in donors:
            row = self.decorate_donor(item, site)
            row["rank"] = rank
            ranked.append(row)
            rank = rank + 1
        # end for
        if form_values == None:
            form_values = {}
        # end if
        return self.site.with_site({
            "donation": settings,
            "donors": ranked,
            "donors_show_all": show_all,
            "social_proof": self.get_support_social_proof(settings),
            "form_ok": form_ok,
            "form_error": form_error,
            "form_field": form_field or "",
            "form_values": form_values
        })
    # end def
# end class
