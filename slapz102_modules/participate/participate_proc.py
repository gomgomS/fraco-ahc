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
from werkzeug.security import generate_password_hash
from slapz102_core import database
from slapz102_core import config
from ahc_site.ahc_site_proc import ahc_site_proc

class participate_proc:

    mgdDB = database.get_db_conn(config.mainDB)
    MEMBER_TYPES = ["AHC_MEMBER", "ALUMNI"]

    def __init__(self, app=None):
        self.webapp = app
        self.site = ahc_site_proc(app)
    # end def

    def get_participate_page(self):
        return self.site.with_site({})
    # end def

    def format_rp(self, amount):
        n = int(amount or 0)
        if n <= 0:
            return "Rp 0"
        # end if
        text = "{:,}".format(n).replace(",", ".")
        return "Rp " + text
    # end def

    def slug_name(self, full_name):
        raw = (full_name or "").strip().lower()
        out = []
        for ch in raw:
            if ch.isalnum():
                out.append(ch)
            elif ch in " -_.":
                out.append("")
            # end if
        # end for
        text = "".join(out)
        if text == "":
            text = "member"
        # end if
        return text[:24]
    # end def

    def default_referral_code(self, full_name):
        base = self.slug_name(full_name) + "2017"
        return self.unique_referral_code(base)
    # end def

    def unique_referral_code(self, code, skip_pkey=""):
        clean = re.sub(r"[^a-zA-Z0-9]", "", (code or "").strip().lower())
        if clean == "":
            clean = "member2017"
        # end if
        candidate = clean
        n = 0
        while True:
            query = {"referral_code": candidate, "is_deleted": False}
            existing = self.mgdDB.db_participant.find_one(query, {"_id": 0, "pkey": 1})
            if existing == None:
                return candidate
            # end if
            if skip_pkey != "" and existing.get("pkey") == skip_pkey:
                return candidate
            # end if
            n = n + 1
            candidate = clean + str(n)
            if n > 99:
                candidate = clean + str(int(time.time()))[-4:]
                return candidate
            # end if
        # end while
    # end def

    def unique_login_id(self, full_name):
        base = self.slug_name(full_name) + "2017"
        if base == "member2017":
            base = "ahc2017"
        # end if
        candidate = base
        n = 0
        while True:
            existing = self.mgdDB.db_user.find_one({
                "is_deleted": False,
                "$or": [
                    {"email": candidate},
                    {"username": candidate}
                ]
            })
            if existing == None:
                part = self.mgdDB.db_participant.find_one({
                    "email": candidate,
                    "is_deleted": False
                })
                if part == None:
                    return candidate
                # end if
            # end if
            n = n + 1
            candidate = base + str(n)
            if n > 99:
                candidate = base + str(int(time.time()))[-4:]
                return candidate
            # end if
        # end while
    # end def

    def get_register_page(self, error="", form=None, member_type=""):
        site = self.site.get_site()
        contribution_num = int(site.get("contribution_num") or 0)
        if contribution_num <= 0:
            contribution_num = 2000000
        # end if
        contribution = (site.get("contribution") or "").strip()
        if contribution == "":
            contribution = self.format_rp(contribution_num)
        # end if
        kind = (member_type or (form or {}).get("member_type") or "").strip().upper()
        if kind not in self.MEMBER_TYPES:
            kind = ""
        # end if
        form_data = form or {}
        if kind != "" and form_data.get("member_type") != kind:
            form_data = dict(form_data)
            form_data["member_type"] = kind
        # end if
        return self.site.with_site({
            "form": form_data,
            "form_error": error,
            "member_type": kind,
            "phase": "form" if kind != "" else "choose",
            "is_ahc_member": kind == "AHC_MEMBER",
            "member_types": [
                ("AHC_MEMBER", "AHC Member", "Graduated in 2017"),
                ("ALUMNI", "Alumni", "Not class of 2017")
            ],
            "contribution": contribution,
            "contribution_num": contribution_num
        })
    # end def

    def save_registration(self, params):
        response = {"status": "FAILED", "desc": "", "done": False, "reg_id": ""}
        member_type = (params.get("member_type") or "").strip().upper()
        full_name = (params.get("full_name") or "").strip()
        email = (params.get("email") or "").strip().lower()
        phone = (params.get("phone") or "").strip()
        city = (params.get("city") or "").strip()
        password = params.get("password") or ""
        confirm = params.get("password_confirm") or ""
        if member_type not in self.MEMBER_TYPES:
            response["desc"] = "Choose AHC Member or Alumni"
            return response
        # end if
        if full_name == "":
            response["desc"] = "Full name is required"
            return response
        # end if
        if member_type == "ALUMNI":
            if email == "" or phone == "":
                response["desc"] = "Email and phone are required"
                return response
            # end if
        else:
            email = self.unique_login_id(full_name)
            phone = ""
        # end if
        if len(password) < 6:
            response["desc"] = "Password must be at least 6 characters"
            return response
        # end if
        if password != confirm:
            response["desc"] = "Password confirmation does not match"
            return response
        # end if
        existing_user = self.mgdDB.db_user.find_one({
            "is_deleted": False,
            "$or": [{"email": email}, {"username": email}]
        })
        if existing_user != None:
            response["desc"] = "This account already exists. Login instead."
            return response
        # end if
        existing_part = self.mgdDB.db_participant.find_one({
            "email": email,
            "is_deleted": False
        })
        if existing_part != None:
            response["desc"] = "This account is already registered. Login instead."
            return response
        # end if
        site = self.site.get_site()
        if member_type == "AHC_MEMBER":
            contribution_num = int(site.get("contribution_num") or 0)
            if contribution_num <= 0:
                contribution_num = 2000000
            # end if
            contribution = (site.get("contribution") or "").strip()
            if contribution == "":
                contribution = self.format_rp(contribution_num)
            # end if
            payment_plan = "TBD"
            shirt_size = "-"
            referral_code = self.default_referral_code(full_name)
            kit_status = "Pending"
            reg_status = "Registered"
        else:
            contribution = "Rp 0"
            contribution_num = 0
            payment_plan = "NONE"
            shirt_size = "-"
            referral_code = ""
            kit_status = "N/A"
            reg_status = "Registered"
        # end if
        sid = ""
        if has_request_context():
            sid = session.get("cart_sid", "")
            if sid == "":
                sid = str(uuid.uuid4())
                session["cart_sid"] = sid
            # end if
        # end if
        password_hash = generate_password_hash(password)
        reg_id = "FRP" + str(int(time.time()))
        rec = database.new(self.mgdDB, "db_participant")
        rec.put("fk_user_id", "")
        rec.put("session_id", sid)
        rec.put("reg_id", reg_id)
        rec.put("member_type", member_type)
        rec.put("full_name", full_name)
        rec.put("email", email)
        rec.put("phone", phone)
        rec.put("address", "")
        rec.put("city", city)
        rec.put("emergency_contact", "")
        rec.put("notes", "")
        rec.put("payment_plan", payment_plan)
        rec.put("shirt_size", shirt_size)
        rec.put("contribution", contribution)
        rec.put("contribution_num", contribution_num)
        rec.put("amount_paid", "Rp 0")
        rec.put("amount_paid_num", 0)
        rec.put("sales_total", "Rp 0")
        rec.put("sales_total_num", 0)
        rec.put("sales_count", 0)
        rec.put("proposal_total", "Rp 0")
        rec.put("proposal_total_num", 0)
        rec.put("self_contribution", "Rp 0")
        rec.put("self_contribution_num", 0)
        rec.put("remaining", "Rp 0")
        rec.put("remaining_num", 0)
        rec.put("referral_code", referral_code)
        rec.put("password_hint", password)
        rec.put("registration_status", reg_status)
        rec.put("payment_status", "")
        rec.put("member_kit_status", kit_status)
        rec.insert()
        user = database.new(self.mgdDB, "db_user")
        user.put("fk_user_id", "")
        user.put("username", email)
        user.put("password", password_hash)
        user.put("role", "PARTICIPANT")
        user.put("name", full_name)
        user.put("phone", phone)
        user.put("email", email)
        user.put("status", "ENABLE")
        user.insert()
        user_row = user.get()
        self.mgdDB.db_participant.update_one(
            {"reg_id": reg_id},
            {"$set": {"fk_user_id": user_row.get("pkey", "")}}
        )
        if has_request_context():
            session["ahc_reg"] = {}
            session["ahc_reg_id"] = reg_id
            session["auth_pkey"] = user_row.get("pkey", "")
        # end if
        response["status"] = "SUCCESS"
        response["done"] = True
        response["reg_id"] = reg_id
        return response
    # end def

    def get_registration_page(self, reg_id):
        sid = ""
        if has_request_context():
            sid = session.get("cart_sid", "")
        # end if
        query = {"reg_id": reg_id, "is_deleted": False}
        if sid != "":
            query["session_id"] = sid
        # end if
        rec = self.mgdDB.db_participant.find_one(query, {"_id": 0})
        if rec == None:
            rec = self.mgdDB.db_participant.find_one(
                {"reg_id": reg_id, "is_deleted": False},
                {"_id": 0}
            )
        # end if
        if rec == None:
            return None
        # end if
        return self.site.with_site({"registration": rec})
    # end def
# end class
