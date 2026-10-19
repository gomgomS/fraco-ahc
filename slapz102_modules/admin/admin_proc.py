import html as html_lib
import hashlib
import os
import re
import sys
import urllib.error
import urllib.request

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from flask import has_request_context, session, request
from urllib.parse import quote_plus, urlparse
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from slapz102_core import database
from slapz102_core import config
from slapz102_core import model
from ahc_site.ahc_site_proc import ahc_site_proc
from ahc_site.ahc_site_seed import ahc_site_seed
import idgen
import sanitize

class admin_proc:

    mgdDB = database.get_db_conn(config.mainDB)
    ALLOWED_EXT = ["pdf", "doc", "docx", "jpg", "jpeg", "png", "webp"]
    IMAGE_EXT = ["jpg", "jpeg", "png", "webp", "gif"]
    PAGE_SIZE = 20
    DEFAULT_MERCHANDISE_CATEGORIES = ["Apparel", "Accessories", "Member Kit", "Other"]
    DEFAULT_SHIPPING_EXPEDITIONS = ["JNE", "J&T Express", "SiCepat", "AnterAja", "POS Indonesia", "GoSend", "GrabExpress", "Other"]
    SHIPPING_HANDLERS = ["OFFICER", "SELF"]
    SHIPPING_STATUSES = ["NOT_REQUESTED", "REQUESTED", "PROCESSING", "SHIPPED", "COMPLETED"]
    SHIPPING_STATUS_LABELS = {
        "NOT_REQUESTED": "Not requested",
        "REQUESTED": "Waiting for officer",
        "PROCESSING": "Being processed",
        "SHIPPED": "Shipped",
        "COMPLETED": "Completed"
    }
    STAFF_ROLES = [
        "OFFICER",
        "ADMIN",
        "FINANCE",
        "MERCHANDISE_ADMIN",
        "PROGRAM_ADMIN",
        "SPONSORSHIP_ADMIN",
        "VENDOR_ADMIN",
        "CONTENT_ADMIN",
        "SUPER_ADMIN"
    ]
    ADMIN_ROLES = STAFF_ROLES
    ROLE_LABELS = {
        "SUPER_ADMIN": "Super admin",
        "ADMIN": "Admin",
        "FINANCE": "Finance",
        "OFFICER": "Officer",
        "MERCHANDISE_ADMIN": "Merchandise admin",
        "PROGRAM_ADMIN": "Program admin",
        "SPONSORSHIP_ADMIN": "Sponsorship admin",
        "VENDOR_ADMIN": "Vendor admin",
        "CONTENT_ADMIN": "Content admin"
    }
    ROLE_HELP = [
        ("SUPER_ADMIN", "Full access, including Users."),
        ("ADMIN", "Website, participants, orders, programs, partners, content, Support Us, and settings. Not Users."),
        ("FINANCE", "Payments, orders, participant money, and Support Us donors. View participants. No delete."),
        ("OFFICER", "Participants, programs, and content. No money, merch, or settings."),
        ("MERCHANDISE_ADMIN", "Products, inventory, and merchandise orders."),
        ("PROGRAM_ADMIN", "Programs and universities."),
        ("SPONSORSHIP_ADMIN", "Sponsors."),
        ("VENDOR_ADMIN", "Vendors."),
        ("CONTENT_ADMIN", "Updates, gallery, and team.")
    ]
    PERMS = {
        "ADMIN": {
            "overview": "read",
            "participants": "write",
            "orders": "write",
            "products": "write",
            "programs": "write",
            "events": "write",
            "sponsors": "write",
            "vendors": "write",
            "universities": "write",
            "payments": "write",
            "content": "write",
            "gallery": "write",
            "team": "write",
            "donations": "write",
            "settings": "write"
        },
        "FINANCE": {
            "overview": "read",
            "participants": "read",
            "orders": "write",
            "payments": "write",
            "donations": "write"
        },
        "OFFICER": {
            "overview": "read",
            "participants": "write",
            "programs": "write",
            "events": "write",
            "content": "write",
            "gallery": "write",
            "team": "write"
        },
        "MERCHANDISE_ADMIN": {
            "overview": "read",
            "products": "write",
            "orders": "write"
        },
        "PROGRAM_ADMIN": {
            "overview": "read",
            "programs": "write",
            "events": "write",
            "universities": "write"
        },
        "SPONSORSHIP_ADMIN": {
            "overview": "read",
            "sponsors": "write"
        },
        "VENDOR_ADMIN": {
            "overview": "read",
            "vendors": "write"
        },
        "CONTENT_ADMIN": {
            "overview": "read",
            "content": "write",
            "gallery": "write",
            "team": "write"
        }
    }
    PAY_ROLES = ["SUPER_ADMIN", "ADMIN", "FINANCE"]
    DELETE_ROLES = {
        "participants": ["SUPER_ADMIN", "ADMIN"],
        "orders": ["SUPER_ADMIN", "ADMIN", "MERCHANDISE_ADMIN"],
        "products": ["SUPER_ADMIN", "ADMIN", "MERCHANDISE_ADMIN"],
        "programs": ["SUPER_ADMIN", "ADMIN", "PROGRAM_ADMIN"],
        "events": ["SUPER_ADMIN", "ADMIN", "PROGRAM_ADMIN"],
        "universities": ["SUPER_ADMIN", "ADMIN", "PROGRAM_ADMIN"],
        "content": ["SUPER_ADMIN", "ADMIN", "CONTENT_ADMIN"],
        "gallery": ["SUPER_ADMIN", "ADMIN", "CONTENT_ADMIN"],
        "team": ["SUPER_ADMIN", "ADMIN", "CONTENT_ADMIN"],
        "donations": ["SUPER_ADMIN", "ADMIN", "FINANCE"],
        "vendors": ["SUPER_ADMIN", "ADMIN", "VENDOR_ADMIN"],
        "users": ["SUPER_ADMIN"]
    }
    NAV = [
        ("overview", "/admin", "Dashboard"),
        ("participants", "/admin/participants", "Participants"),
        ("orders", "/admin/orders", "Orders"),
        ("products", "/admin/products", "Products"),
        ("programs", "/admin/programs", "Programs"),
        ("sponsors", "/admin/sponsors", "Sponsors"),
        ("vendors", "/admin/vendors", "Vendors"),
        ("universities", "/admin/universities", "Universities"),
        ("payments", "/admin/payments", "Finance"),
        ("donations", "/admin/donations", "Support Us"),
        ("content", "/admin/content", "Content"),
        ("gallery", "/admin/gallery", "Gallery"),
        ("team", "/admin/team", "Team"),
        ("users", "/admin/users", "Users"),
        ("settings", "/admin/settings", "Settings")
    ]
    ORDER_STATUSES = [
        "Pending Payment", "Preorder", "Paid", "Ready", "Processing", "Shipped", "Completed", "Cancelled"
    ]
    ORDER_PAY_STATUSES = ["Pending", "Paid"]
    SPONSOR_STATUSES = [
        "PENDING", "New", "Under Review", "Contacted", "Negotiating", "Approved", "Rejected", "Completed"
    ]
    VENDOR_STATUSES = [
        "PENDING", "New", "Reviewing", "Contacted", "Negotiating", "Approved", "Rejected", "Contracted"
    ]
    UNI_STATUSES = [
        "PENDING", "Applied", "Approved", "Payment Pending", "Confirmed", "Cancelled"
    ]
    PAY_STATUSES = ["PENDING", "PAID", "FAILED", "REFUNDED"]
    PAY_TYPES = [
        "Participant Contribution", "Merchandise", "University Booth", "Sponsorship"
    ]
    TRANSACTION_TYPES = ["Contribution", "Merch Sales", "Proposal", "Sponsor", "Shipping", "Other"]
    TRANSACTION_KINDS = ["INCOME", "EXPENSE"]
    EVENT_STATUSES = [
        "Draft", "Published", "Upcoming", "Registration Open", "Registration Closed", "Completed"
    ]
    PRODUCT_STATUSES = ["ACTIVE", "DRAFT", "OUT_OF_STOCK", "ARCHIVED"]
    UPDATE_CATEGORIES = [
        "News", "Announcements", "Event Updates", "Behind the Scenes", "Throwback", "Community"
    ]
    VENUE_MODES = ["OFFLINE", "ONLINE", "HYBRID"]
    GALLERY_ALBUMS = [
        "Preparation", "Alumni", "Events", "University Fair",
        "Career Workshop", "Spiritual Affairs", "Behind The Scenes", "AHC 2027"
    ]
    DONOR_FOLLOW_STATUSES = ["FOLLOW_UP", "RECEIVED"]
    DONOR_FOLLOW_LABELS = {
        "FOLLOW_UP": "Follow up",
        "RECEIVED": "Received"
    }

    def __init__(self, app=None):
        self.webapp = app
        self.site = ahc_site_proc(app)
        seeder = ahc_site_seed(app)
        seeder.ensure_admin_user()
        seeder.ensure_ops_admin_user()
        seeder.ensure_finance_user()
        seeder.ensure_officer_user()
    # end def

    def staff_role(self, role):
        if role in self.STAFF_ROLES:
            return role
        # end if
        return ""
    # end def

    def role_label(self, role):
        kind = self.staff_role(role)
        return self.ROLE_LABELS.get(kind, kind)
    # end def

    def is_super(self, admin):
        if admin == None:
            return False
        # end if
        return self.staff_role(admin.get("role")) == "SUPER_ADMIN"
    # end def

    def access_level(self, role, page_key):
        kind = self.staff_role(role)
        if kind == "":
            return "NONE"
        # end if
        if kind == "SUPER_ADMIN":
            return "WRITE"
        # end if
        allowed = self.PERMS.get(kind) or {}
        level = (allowed.get(page_key) or "").upper()
        if level in ["READ", "WRITE"]:
            return level
        # end if
        return "NONE"
    # end def

    def can_access(self, role, page_key):
        return self.access_level(role, page_key) != "NONE"
    # end def

    def can_write(self, role, page_key):
        return self.access_level(role, page_key) == "WRITE"
    # end def

    def can_delete(self, role, page_key):
        kind = self.staff_role(role)
        if kind == "SUPER_ADMIN":
            return True
        # end if
        allowed = self.DELETE_ROLES.get(page_key)
        if allowed == None:
            return kind == "ADMIN" and self.can_write(kind, page_key)
        # end if
        return kind in allowed
    # end def

    def can_pay(self, role):
        return self.staff_role(role) in self.PAY_ROLES
    # end def

    def format_rp(self, amount):
        n = int(amount or 0)
        if n <= 0:
            return "Rp 0"
        # end if
        text = "{:,}".format(n).replace(",", ".")
        return "Rp " + text
    # end def

    def parse_int(self, value):
        digits = re.sub(r"[^0-9]", "", str(value or "0"))
        if digits == "":
            return 0
        # end if
        return int(digits)
    # end def

    def parse_list(self, value):
        if isinstance(value, list):
            return value
        # end if
        text = (value or "").strip()
        if text == "":
            return []
        # end if
        parts = []
        for item in text.split(","):
            piece = item.strip()
            if piece != "":
                parts.append(piece)
            # end if
        # end for
        return parts
    # end def

    def slugify(self, text):
        raw = (text or "").strip().lower()
        out = []
        for ch in raw:
            if ch.isalnum():
                out.append(ch)
            elif ch in " -_":
                out.append("-")
            # end if
        # end for
        slug = "".join(out)
        while "--" in slug:
            slug = slug.replace("--", "-")
        # end while
        return slug.strip("-")
    # end def

    def schema_keys(self, table):
        rec = model.db.get(table) or {}
        keys = []
        for key in rec:
            keys.append(key)
        # end for
        return keys
    # end def

    def current_admin(self):
        if not has_request_context():
            return None
        # end if
        pkey = session.get("admin_pkey", "")
        if pkey == "":
            return None
        # end if
        rec = self.mgdDB.db_user.find_one(
            {"pkey": pkey, "is_deleted": False, "status": "ENABLE"},
            {"_id": 0, "password": 0}
        )
        if rec == None:
            return None
        # end if
        if rec.get("role") not in self.ADMIN_ROLES:
            return None
        # end if
        return rec
    # end def

    def nav_for(self, role):
        items = []
        for key, href, label in self.NAV:
            if self.can_access(role, key):
                items.append((key, href, label))
            # end if
        # end for
        return items
    # end def

    def login(self, params, raw_password):
        response = {"status": "FAILED", "desc": ""}
        email = (params.get("email") or "").strip().lower()
        if email == "" or raw_password == "":
            response["desc"] = "Email and password are required"
            return response
        # end if
        user = self.mgdDB.db_user.find_one({
            "email": email,
            "is_deleted": False,
            "status": "ENABLE"
        })
        if user == None:
            response["desc"] = "Email or password is not right"
            return response
        # end if
        if user.get("role") not in self.ADMIN_ROLES:
            response["desc"] = "This account is not staff"
            return response
        # end if
        if not check_password_hash(user.get("password") or "", raw_password):
            response["desc"] = "Email or password is not right"
            return response
        # end if
        session["admin_pkey"] = user.get("pkey", "")
        response["status"] = "SUCCESS"
        return response
    # end def

    def logout(self):
        session.pop("admin_pkey", None)
    # end def

    def gate(self, page_key):
        admin = self.current_admin()
        if admin == None:
            return {"status": "LOGIN"}
        # end if
        if not self.can_access(admin.get("role"), page_key):
            return {"status": "FORBIDDEN"}
        # end if
        return {"status": "SUCCESS", "admin": admin}
    # end def

    def page(self, page_key, extra=None):
        admin = self.current_admin()
        role = (admin or {}).get("role", "")
        payload = {
            "admin_user": admin,
            "admin_nav": self.nav_for(role),
            "admin_page": page_key,
            "admin_role": self.staff_role(role),
            "admin_role_label": self.role_label(role),
            "can_write": self.can_write(role, page_key),
            "can_delete": self.can_delete(role, page_key),
            "can_pay": self.can_pay(role),
            "role_labels": self.ROLE_LABELS,
            "role_help": self.ROLE_HELP,
            "form_error": "",
            "form_ok": False
        }
        if extra != None:
            payload.update(extra)
        # end if
        return self.site.with_site(payload)
    # end def

    def list_rows(self, table, extra_filter=None, sort_field="rec_timestamp", direction=-1):
        query = {"is_deleted": False}
        if extra_filter != None:
            query.update(extra_filter)
        # end if
        recs = list(self.mgdDB[table].find(query, {"_id": 0}).sort(sort_field, direction))
        return recs
    # end def

    def dash(self, value):
        text = str(value or "").strip()
        if text == "":
            return "—"
        # end if
        return text
    # end def

    def display_date(self, rec):
        text = rec.get("rec_timestamp_str") or rec.get("date") or ""
        return self.dash(text)
    # end def

    def parse_page(self, key="page"):
        if not has_request_context():
            return 1
        # end if
        digits = re.sub(r"[^0-9]", "", str(request.args.get(key) or "1"))
        if digits == "":
            return 1
        # end if
        n = int(digits)
        if n < 1:
            return 1
        # end if
        return n
    # end def

    def page_href(self, path, page, extra_qs, page_key="page"):
        href = path + "?" + page_key + "=" + str(page)
        if extra_qs != "":
            href = href + extra_qs
        # end if
        return href
    # end def

    def build_pager(self, total, page, per_page, path, extra_qs="", page_key="page"):
        if per_page < 1:
            per_page = self.PAGE_SIZE
        # end if
        pages = int((total + per_page - 1) / per_page)
        if pages < 1:
            pages = 1
        # end if
        if page > pages:
            page = pages
        # end if
        skip = (page - 1) * per_page
        start = 0
        end = 0
        if total > 0:
            start = skip + 1
            end = skip + per_page
            if end > total:
                end = total
            # end if
        # end if
        links = []
        window = []
        n = 1
        while n <= pages:
            show = n == 1 or n == pages or (n >= page - 2 and n <= page + 2)
            if show:
                window.append(n)
            # end if
            n = n + 1
        # end while
        last = 0
        for n in window:
            if last != 0 and n > last + 1:
                links.append({"text": "…", "href": "", "current": False, "gap": True})
            # end if
            links.append({
                "text": str(n),
                "href": self.page_href(path, n, extra_qs, page_key),
                "current": n == page,
                "gap": False
            })
            last = n
        # end for
        summary = "No rows"
        if total > 0:
            summary = "Showing " + str(start) + "–" + str(end) + " of " + str(total)
        # end if
        return {
            "page": page,
            "pages": pages,
            "total": total,
            "per_page": per_page,
            "skip": skip,
            "has_prev": page > 1,
            "has_next": page < pages,
            "prev_href": self.page_href(path, page - 1, extra_qs, page_key) if page > 1 else "",
            "next_href": self.page_href(path, page + 1, extra_qs, page_key) if page < pages else "",
            "links": links,
            "summary": summary,
            "show": pages > 1
        }
    # end def

    def fetch_page(self, table, path, extra_filter=None, sort_field="rec_timestamp", direction=-1, extra_qs="", page_key="page"):
        page = self.parse_page(page_key)
        query = {"is_deleted": False}
        if extra_filter != None:
            query.update(extra_filter)
        # end if
        total = self.mgdDB[table].count_documents(query)
        pager = self.build_pager(total, page, self.PAGE_SIZE, path, extra_qs, page_key)
        recs = list(
            self.mgdDB[table].find(query, {"_id": 0}).sort(sort_field, direction).skip(pager["skip"]).limit(self.PAGE_SIZE)
        )
        return recs, pager
    # end def

    def slice_page(self, docs, path, extra_qs="", page_key="page"):
        page = self.parse_page(page_key)
        pager = self.build_pager(len(docs), page, self.PAGE_SIZE, path, extra_qs, page_key)
        rows = docs[pager["skip"]:pager["skip"] + self.PAGE_SIZE]
        return rows, pager
    # end def

    def cell(self, text, kind="text", href="", src="", alt="", pkey="", options=None, status="", wrap=False, html="", source_table="", index=""):
        rec = {
            "kind": kind,
            "text": self.dash(text),
            "href": href or "",
            "src": src or "",
            "alt": alt or "",
            "pkey": pkey or "",
            "status": status if kind == "receive_account" else (status or str(text or "")),
            "options": options or [],
            "wrap": wrap,
            "html": html or "",
            "source_table": source_table or "",
            "index": index
        }
        return rec
    # end def

    def make_table(self, columns, rows, pager, empty):
        return {
            "columns": columns,
            "rows": rows,
            "pager": pager,
            "empty": empty,
            "colspan": len(columns)
        }
    # end def

    def table_participants(self, member_type="", extra_qs_base=""):
        kind = (member_type or "").strip().upper()
        extra = {}
        extra_qs = extra_qs_base or ""
        if has_request_context():
            if kind == "":
                kind = (request.args.get("type") or "").strip().upper()
            # end if
        # end if
        if kind in ["AHC_MEMBER", "ALUMNI"]:
            extra["member_type"] = kind
            if "&type=" not in extra_qs and "type=" not in extra_qs:
                extra_qs = extra_qs + "&type=" + quote_plus(kind)
            # end if
        # end if
        if extra == {}:
            extra = None
        # end if
        if kind == "AHC_MEMBER":
            query = {
                "is_deleted": False,
                "member_type": {"$ne": "ALUMNI"}
            }
            recs = list(self.mgdDB.db_participant.find(query, {"_id": 0}).sort("full_name", 1))
            pager = None
        else:
            recs, pager = self.fetch_page(
                "db_participant",
                "/admin/participants",
                extra,
                extra_qs=extra_qs
            )
        # end if
        rows = []
        for rec in recs:
            if kind == "ALUMNI":
                rows.append({"cells": [
                    self.cell(rec.get("full_name"), "link", "/admin/participants/" + rec.get("pkey", "")),
                    self.cell(rec.get("password_hint") or "—"),
                    self.cell("Delete", "delete", pkey=rec.get("pkey", ""))
                ]})
            else:
                prop, self_amt = self._member_pledge_totals(rec)
                rows.append({"cells": [
                    self.cell(rec.get("full_name"), "link", "/admin/participants/" + rec.get("pkey", "")),
                    self.cell(rec.get("email") or "—"),
                    self.cell(rec.get("password_hint") or "—"),
                    self.cell(rec.get("sales_total") or "Rp 0"),
                    self.cell(self.format_rp(prop)),
                    self.cell(self.format_rp(self_amt)),
                    self.cell("Delete", "delete", pkey=rec.get("pkey", ""))
                ]})
            # end if
        # end for
        if kind == "ALUMNI":
            columns = ["Name", "Password", ""]
            empty = "No alumni yet."
        else:
            columns = ["Name", "Username", "Password", "Merch profit", "Proposal", "Contribution", ""]
            empty = "No AHC members yet."
        # end if
        return self.make_table(columns, rows, pager, empty)
    # end def

    def _is_self_pledge(self, item):
        if item == None:
            return False
        # end if
        if (item.get("pledge_source") or "").strip().upper() == "SELF":
            return True
        # end if
        note = (item.get("note") or "").lower()
        return note.find("self pledge") >= 0
    # end def

    def _member_pledge_totals(self, rec):
        pkey = rec.get("pkey") or ""
        code = (rec.get("referral_code") or "").strip().lower()
        clauses = []
        if pkey != "":
            clauses.append({"fk_referrer_id": pkey})
        # end if
        if code != "":
            clauses.append({"referral_code": code})
        # end if
        proposal = 0
        self_amt = 0
        if clauses == []:
            return proposal, self_amt
        # end if
        for item in self.mgdDB.db_donor.find(
            {"is_deleted": False, "follow_status": "RECEIVED", "$or": clauses},
            {"_id": 0}
        ):
            amount = int(item.get("amount_num") or 0)
            if self._is_self_pledge(item):
                self_amt = self_amt + amount
            else:
                proposal = proposal + amount
            # end if
        # end for
        return proposal, self_amt
    # end def

    def _member_target(self, rec):
        target = int(rec.get("contribution_num") or 0)
        if target <= 0:
            site = self.site.get_site() or {}
            target = int(site.get("contribution_num") or 0)
        # end if
        if target <= 0:
            target = 2000000
        # end if
        return target
    # end def

    def _track_pct(self, raised, target):
        if target <= 0:
            return 0
        # end if
        pct = int(round(100.0 * raised / target))
        if pct < 0:
            pct = 0
        # end if
        return pct
    # end def

    def _marker_pct(self, pct):
        if pct > 100:
            return 100
        # end if
        if pct < 0:
            return 0
        # end if
        return pct
    # end def

    def participant_overview_stats(self):
        ahc = self.list_rows("db_participant", {"member_type": "AHC_MEMBER"})
        alumni = self.list_rows("db_participant", {"member_type": "ALUMNI"})
        legacy = self.list_rows("db_participant", {"member_type": {"$nin": ["AHC_MEMBER", "ALUMNI"]}})
        ahc_all = list(ahc)
        for rec in legacy:
            if (rec.get("member_type") or "AHC_MEMBER") != "ALUMNI":
                ahc_all.append(rec)
            # end if
        # end for
        merch_total = 0
        proposal_total = 0
        self_total = 0
        sellers = 0
        proposers = 0
        self_givers = 0
        achieved = 0
        for rec in ahc_all:
            sold = int(rec.get("sales_total_num") or 0)
            prop, self_amt = self._member_pledge_totals(rec)
            target = self._member_target(rec)
            merch_total = merch_total + sold
            proposal_total = proposal_total + prop
            self_total = self_total + self_amt
            if sold > 0:
                sellers = sellers + 1
            # end if
            if prop > 0:
                proposers = proposers + 1
            # end if
            if self_amt > 0:
                self_givers = self_givers + 1
            # end if
            if sold + prop + self_amt >= target and target > 0:
                achieved = achieved + 1
            # end if
        # end for
        return {
            "total": len(ahc_all) + len(alumni),
            "ahc_count": len(ahc_all),
            "alumni_count": len(alumni),
            "merch_total": self.format_rp(merch_total),
            "merch_total_num": merch_total,
            "proposal_total": self.format_rp(proposal_total),
            "proposal_total_num": proposal_total,
            "contribution_total": self.format_rp(self_total),
            "contribution_total_num": self_total,
            "sellers": sellers,
            "proposers": proposers,
            "contributors": self_givers,
            "achieved": achieved
        }
    # end def

    def ahc_member_cards(self, focus="all"):
        focus = (focus or "all").strip().lower()
        recs = self.list_rows("db_participant", {"member_type": "AHC_MEMBER"}, "full_name", 1)
        legacy = self.list_rows("db_participant", {"member_type": {"$nin": ["AHC_MEMBER", "ALUMNI"]}}, "full_name", 1)
        for rec in legacy:
            recs.append(rec)
        # end for
        cards = []
        for rec in recs:
            sold = int(rec.get("sales_total_num") or 0)
            prop, self_amt = self._member_pledge_totals(rec)
            pkey = rec.get("pkey") or ""
            if focus == "sellers" and sold <= 0:
                continue
            # end if
            if focus == "contributors" and prop <= 0:
                continue
            # end if
            if focus == "own" and self_amt <= 0:
                continue
            # end if
            if focus == "active" and sold <= 0 and prop <= 0 and self_amt <= 0:
                continue
            # end if
            target = self._member_target(rec)
            shipping_expense = self.member_shipping_expense_num(rec)
            combined = sold + prop + self_amt - shipping_expense
            if combined < 0:
                combined = 0
            # end if
            left = target - combined
            if left < 0:
                left = 0
            # end if
            merch_pct = self._track_pct(sold, target)
            prop_pct = self._track_pct(prop, target)
            self_pct = self._track_pct(self_amt, target)
            combined_pct = self._track_pct(combined, target)
            cards.append({
                "pkey": pkey,
                "reg_id": rec.get("reg_id") or "",
                "name": rec.get("full_name") or "—",
                "referral_code": rec.get("referral_code") or "—",
                "href": "/admin/participants/" + pkey,
                "target": self.format_rp(target),
                "target_num": target,
                "merch": self.format_rp(sold),
                "merch_num": sold,
                "merch_pct": merch_pct,
                "merch_marker": self._marker_pct(merch_pct),
                "proposal": self.format_rp(prop),
                "proposal_num": prop,
                "proposal_pct": prop_pct,
                "proposal_marker": self._marker_pct(prop_pct),
                "self_contribution": self.format_rp(self_amt),
                "self_contribution_num": self_amt,
                "self_pct": self_pct,
                "self_marker": self._marker_pct(self_pct),
                "shipping_expense": self.format_rp(shipping_expense),
                "shipping_expense_num": shipping_expense,
                "combined": self.format_rp(combined),
                "combined_num": combined,
                "combined_pct": combined_pct,
                "combined_marker": self._marker_pct(combined_pct),
                "left": self.format_rp(left),
                "sales_count": int(rec.get("sales_count") or 0),
                "achieved": left <= 0 and combined > 0
            })
        # end for
        cards.sort(key=lambda item: (-item["combined_num"], -item["merch_num"], item["name"].lower()))
        return cards
    # end def

    def participants_hub(self, section="overview", ahc_tab="list", focus="all"):
        section = (section or "overview").strip().lower()
        if section not in ["overview", "ahc", "alumni"]:
            section = "overview"
        # end if
        ahc_tab = (ahc_tab or "list").strip().lower()
        if ahc_tab not in ["list", "overview"]:
            ahc_tab = "list"
        # end if
        focus = (focus or "all").strip().lower()
        if focus not in ["all", "active", "own", "sellers", "contributors"]:
            focus = "all"
        # end if
        payload = {
            "part_section": section,
            "ahc_tab": ahc_tab,
            "ahc_focus": focus,
            "overview_stats": self.participant_overview_stats(),
            "list_table": None,
            "ahc_cards": []
        }
        if section == "ahc" and ahc_tab == "list":
            payload["list_table"] = self.table_participants(
                "AHC_MEMBER",
                "&section=ahc&ahc_tab=list&type=AHC_MEMBER"
            )
        elif section == "alumni":
            payload["list_table"] = self.table_participants(
                "ALUMNI",
                "&section=alumni&type=ALUMNI"
            )
        elif section == "ahc" and ahc_tab == "overview":
            payload["ahc_cards"] = self.ahc_member_cards(focus)
        # end if
        return payload
    # end def

    def order_incharge_filter(self, q):
        clean = (q or "").strip()
        if clean == "":
            return None
        # end if
        pattern = re.escape(clean)
        parts = list(self.mgdDB.db_participant.find(
            {
                "is_deleted": False,
                "$or": [
                    {"referral_code": {"$regex": pattern, "$options": "i"}},
                    {"full_name": {"$regex": pattern, "$options": "i"}},
                    {"reg_id": {"$regex": pattern, "$options": "i"}}
                ]
            },
            {"_id": 0, "pkey": 1, "referral_code": 1}
        ))
        pkeys = []
        codes = []
        for part in parts:
            pid = (part.get("pkey") or "").strip()
            if pid != "" and pid not in pkeys:
                pkeys.append(pid)
            # end if
            code = (part.get("referral_code") or "").strip().lower()
            if code != "" and code not in codes:
                codes.append(code)
            # end if
        # end for
        clauses = [
            {"referral_code": {"$regex": pattern, "$options": "i"}},
            {"fk_referrer_reg_id": {"$regex": pattern, "$options": "i"}}
        ]
        if pkeys != []:
            clauses.append({"fk_referrer_id": {"$in": pkeys}})
        # end if
        if codes != []:
            clauses.append({"referral_code": {"$in": codes}})
        # end if
        return {"$or": clauses}
    # end def

    def table_orders(self):
        status = ""
        pay = ""
        shipping = ""
        q = ""
        extra_qs = ""
        clauses = []
        if has_request_context():
            status = (request.args.get("status") or "").strip()
            pay = (request.args.get("pay") or "").strip()
            shipping = (request.args.get("shipping") or "").strip().upper()
            q = (request.args.get("q") or "").strip()
        # end if
        if status != "":
            clauses.append({"order_status": status})
            extra_qs = extra_qs + "&status=" + quote_plus(status)
        # end if
        if pay != "":
            clauses.append({"payment_status": pay})
            extra_qs = extra_qs + "&pay=" + quote_plus(pay)
        # end if
        if shipping in ["OFFICER", "SELF"]:
            clauses.append({"shipping_handler": shipping})
            extra_qs = extra_qs + "&shipping=" + quote_plus(shipping)
        elif shipping == "NOT_SELECTED":
            clauses.append({"shipping_handler": {"$in": ["", None]}})
            extra_qs = extra_qs + "&shipping=NOT_SELECTED"
        # end if
        if q != "":
            pattern = re.escape(q)
            clauses.append({"$or": [
                {"order_id": {"$regex": pattern, "$options": "i"}},
                {"full_name": {"$regex": pattern, "$options": "i"}}
            ]})
            extra_qs = extra_qs + "&q=" + quote_plus(q)
        # end if
        if clauses == []:
            extra = None
        elif len(clauses) == 1:
            extra = clauses[0]
        else:
            extra = {"$and": clauses}
        # end if
        recs, pager = self.fetch_page("db_order", "/admin/orders", extra, extra_qs=extra_qs)
        rows = []
        for rec in recs:
            pay_val = rec.get("payment_status") or ""
            econ = self.order_seller_economics(rec)
            cuts_html = (
                '<div class="admin-econ-cell"><strong>−' + econ.get("cuts", "Rp 0") + '</strong>'
                '<p class="product-meta" style="margin:4px 0 0">Bahan −' + econ.get("bahan", "Rp 0") + '</p>'
            )
            if econ.get("shipping_show"):
                cuts_html = cuts_html + (
                    '<p class="product-meta" style="margin:2px 0 0">Ship −' + econ.get("shipping_delivery", "Rp 0") +
                    ' · Pack −' + econ.get("shipping_service_fee", "Rp 0") + '</p>'
                )
            # end if
            cuts_html = cuts_html + '</div>'
            cells = [
                self.cell(rec.get("order_id"), "link", "/admin/orders/" + rec.get("pkey", "")),
                self.cell(rec.get("full_name")),
                self.cell(self.order_referrer_label(rec), wrap=True),
                self.cell(self.display_date(rec)),
                self.cell(rec.get("total")),
                self.cell("", "html_block", html=cuts_html, wrap=True),
                self.cell(econ.get("net_seller", "Rp 0"), wrap=True),
                self.cell(
                    pay_val,
                    "order_pay",
                    pkey=rec.get("pkey", ""),
                    status=pay_val,
                    options=self.order_pay_options(pay_val)
                ),
                self.cell(
                    "Officer" if rec.get("shipping_handler") == "OFFICER"
                    else ("Self-arranged" if rec.get("shipping_handler") == "SELF" else "Not selected"),
                    "status",
                    status=rec.get("shipping_handler") or "NOT_SELECTED"
                ),
                self.cell(rec.get("order_status"), "status"),
                self.cell("Delete", "delete", pkey=rec.get("pkey", ""))
            ]
            if shipping == "OFFICER":
                cells.insert(0, self.cell(
                    "",
                    "order_print_select",
                    pkey=rec.get("pkey", "")
                ))
            # end if
            rows.append({"cells": cells})
        # end for
        def with_q(href):
            if q == "":
                return href
            # end if
            if "?" in href:
                return href + "&q=" + quote_plus(q)
            # end if
            return href + "?q=" + quote_plus(q)
        # end def
        def with_shipping(href):
            if shipping == "":
                return href
            # end if
            if "?" in href:
                return href + "&shipping=" + quote_plus(shipping)
            # end if
            return href + "?shipping=" + quote_plus(shipping)
        # end def
        all_href = "/admin/orders"
        if pay != "":
            all_href = "/admin/orders?pay=" + quote_plus(pay)
        # end if
        filters = [{"label": "All", "href": with_q(with_shipping(all_href)), "active": status == ""}]
        for item in self.ORDER_STATUSES:
            href = "/admin/orders?status=" + quote_plus(item)
            if pay != "":
                href = href + "&pay=" + quote_plus(pay)
            # end if
            filters.append({
                "label": item,
                "href": with_q(with_shipping(href)),
                "active": status == item
            })
        # end for
        pay_base = "/admin/orders"
        if status != "":
            pay_base = "/admin/orders?status=" + quote_plus(status)
        # end if
        pay_filters = [{"label": "All payments", "href": with_q(with_shipping(pay_base)), "active": pay == ""}]
        for item in self.ORDER_PAY_STATUSES:
            if status != "":
                href = "/admin/orders?status=" + quote_plus(status) + "&pay=" + quote_plus(item)
            else:
                href = "/admin/orders?pay=" + quote_plus(item)
            # end if
            pay_filters.append({
                "label": item,
                "href": with_q(with_shipping(href)),
                "active": pay == item
            })
        # end for
        shipping_base = "/admin/orders"
        if status != "":
            shipping_base = shipping_base + "?status=" + quote_plus(status)
        # end if
        if pay != "":
            separator = "&" if "?" in shipping_base else "?"
            shipping_base = shipping_base + separator + "pay=" + quote_plus(pay)
        # end if
        shipping_filters = [{"label": "All shipping", "href": with_q(shipping_base), "active": shipping == ""}]
        for value, label in [
            ("OFFICER", "Officer"),
            ("SELF", "Self-arranged"),
            ("NOT_SELECTED", "Not selected")
        ]:
            separator = "&" if "?" in shipping_base else "?"
            shipping_filters.append({
                "label": label,
                "href": with_q(shipping_base + separator + "shipping=" + quote_plus(value)),
                "active": shipping == value
            })
        # end for
        empty_msg = "No orders yet."
        if q != "":
            empty_msg = "No orders found for order ID or customer name \"" + q + "\"."
        # end if
        columns = [
            "Order ID", "Customer", "In charge (referral)", "Date", "Total",
            "Total cuts", "Seller net", "Payment", "Shipping", "Status", ""
        ]
        if shipping == "OFFICER":
            columns.insert(0, "Select")
        # end if
        table = self.make_table(
            columns,
            rows,
            pager,
            empty_msg
        )
        table["filters"] = filters
        table["pay_filters"] = pay_filters
        table["shipping_filters"] = shipping_filters
        table["search_q"] = q
        table["search_status"] = status
        table["search_pay"] = pay
        table["search_shipping"] = shipping
        table["search_label"] = "Search by order ID or customer name"
        table["search_placeholder"] = "Order ID or customer name"
        table["search_hint"] = "Find orders using the transaction/order ID or the customer's name."
        return table
    # end def

    def table_products(self):
        recs, pager = self.fetch_page("db_product", "/admin/products", sort_field="name", direction=1)
        rows = []
        for rec in recs:
            stock = int(rec.get("stock") or 0)
            by_size = rec.get("stock_by_size") or {}
            if isinstance(by_size, dict) and by_size != {}:
                stock = 0
                for key in by_size:
                    try:
                        stock = stock + int(by_size.get(key) or 0)
                    except Exception:
                        pass
                    # end try
                # end for
            # end if
            allow = rec.get("allow_preorder") == True or rec.get("allow_preorder") in ["1", "YES"] or rec.get("is_preorder") == True
            if stock > 0:
                sale_type = "In stock (" + str(stock) + ")"
                if isinstance(by_size, dict) and by_size != {}:
                    bits = []
                    for key in by_size:
                        bits.append(str(key) + ":" + str(by_size.get(key) or 0))
                    # end for
                    sale_type = sale_type + " · " + ", ".join(bits)
                # end if
            elif allow:
                sale_type = "Out of stock · Preorder open"
                if (rec.get("preorder_eta") or "") != "":
                    sale_type = sale_type + " · " + (rec.get("preorder_eta") or "")
                # end if
            else:
                sale_type = "Out of stock"
            # end if
            profit_label = rec.get("profit") or "Rp 0"
            dnum = int(rec.get("discount_num") or 0)
            flag = rec.get("discount_enabled")
            disc_on = flag == True or flag in ["1", "YES", "true", "on", "True"]
            if flag == False or flag in ["0", "NO", "false", "off", "False"]:
                disc_on = False
            elif flag == None and dnum > 0:
                disc_on = True
            # end if
            if disc_on and dnum > 0:
                price_num = int(rec.get("price_num") or 0)
                bahan_num = int(rec.get("bahan_baku_num") or 0)
                base = price_num - bahan_num
                if base < 0:
                    base = 0
                # end if
                dtype = (rec.get("discount_type") or "PCT").strip().upper()
                if dtype == "FIXED":
                    disc = dnum
                else:
                    disc = int(round(price_num * dnum / 100.0))
                # end if
                if disc > price_num:
                    disc = price_num
                # end if
                after = base - disc
                if after < 0:
                    after = 0
                # end if
                profit_label = self.format_rp(base) + " → " + self.format_rp(after) + " w/ disc"
            # end if
            rows.append({"cells": [
                self.cell(rec.get("name"), "link", "/admin/products/" + rec.get("pkey", "")),
                self.cell(rec.get("sku")),
                self.cell(rec.get("category")),
                self.cell(rec.get("price")),
                self.cell(rec.get("bahan_baku") or "Rp 0"),
                self.cell(profit_label),
                self.cell(sale_type),
                self.cell(rec.get("stock")),
                self.cell(rec.get("reserved")),
                self.cell(rec.get("sold")),
                self.cell(rec.get("status"), "status"),
                self.cell("Delete", "delete", pkey=rec.get("pkey", ""))
            ]})
        # end for
        return self.make_table(
            ["Product", "SKU", "Category", "Price", "Bahan baku", "Profit", "Stock state", "Stock", "Reserved", "Sold", "Status", ""],
            rows,
            pager,
            "No products."
        )
    # end def

    def table_programs(self):
        recs, pager = self.fetch_page("db_program", "/admin/programs", sort_field="order", direction=1)
        rows = []
        for rec in recs:
            rows.append({"cells": [
                self.cell(rec.get("title"), "link", "/admin/programs/" + rec.get("pkey", "")),
                self.cell(rec.get("slug")),
                self.cell(rec.get("status"), "status")
            ]})
        # end for
        return self.make_table(["Program", "Slug", "Status"], rows, pager, "No programs.")
    # end def

    def table_events(self):
        recs, pager = self.fetch_page("db_event", "/admin/events")
        rows = []
        for rec in recs:
            rows.append({"cells": [
                self.cell(rec.get("title"), "link", "/admin/events/" + rec.get("pkey", "")),
                self.cell(rec.get("date")),
                self.cell(rec.get("event_status"), "status")
            ]})
        # end for
        return self.make_table(["Event", "Date", "Status"], rows, pager, "No events.")
    # end def

    def table_sponsors(self):
        recs, pager = self.fetch_page("db_sponsor_app", "/admin/sponsors")
        rows = []
        for rec in recs:
            rows.append({"cells": [
                self.cell(rec.get("company_name"), "link", "/admin/sponsors/" + rec.get("pkey", "")),
                self.cell(rec.get("contact_person")),
                self.cell(rec.get("email")),
                self.cell(rec.get("package_slug")),
                self.cell(rec.get("status"), "status"),
                self.cell(self.display_date(rec)),
                self.cell(rec.get("assigned_pic"))
            ]})
        # end for
        return self.make_table(
            ["Company", "PIC", "Email", "Package", "Status", "Date", "Assigned"],
            rows,
            pager,
            "No applications."
        )
    # end def

    def table_sponsor_packages(self):
        recs, pager = self.fetch_page(
            "db_sponsor_package",
            "/admin/sponsors/packages",
            sort_field="order",
            direction=1
        )
        rows = []
        for rec in recs:
            benefits = rec.get("benefits") or []
            if isinstance(benefits, list):
                benefit_n = str(len(benefits))
            else:
                benefit_n = "—"
            # end if
            rows.append({"cells": [
                self.cell(rec.get("name"), "link", "/admin/sponsors/packages/" + rec.get("pkey", "")),
                self.cell(rec.get("slug")),
                self.cell(rec.get("amount")),
                self.cell(benefit_n),
                self.cell(rec.get("order")),
                self.cell(rec.get("status"), "status"),
                self.cell("Delete", "delete", pkey=rec.get("pkey", ""))
            ]})
        # end for
        return self.make_table(
            ["Package", "Slug", "Amount", "Benefits", "Order", "Status", ""],
            rows,
            pager,
            "No packages yet. Create one to show on /partners and /sponsorship."
        )
    # end def

    def parse_lines(self, value):
        if isinstance(value, list):
            return value
        # end if
        text = (value or "").replace("\r", "")
        parts = []
        for item in text.split("\n"):
            piece = item.strip()
            if piece != "":
                parts.append(piece)
            # end if
        # end for
        return parts
    # end def

    def table_vendors(self):
        recs, pager = self.fetch_page("db_vendor_app", "/admin/vendors", extra_qs="&tab=list")
        rows = []
        for rec in recs:
            status_val = rec.get("status") or "PENDING"
            status_opts = list(self.VENDOR_STATUSES)
            if status_val != "" and status_val not in status_opts:
                status_opts.insert(0, status_val)
            # end if
            rows.append({"cells": [
                self.cell(rec.get("business_name"), "link", "/admin/vendors/" + rec.get("pkey", "")),
                self.cell(
                    rec.get("business_name"),
                    "modal",
                    html=sanitize.clean_rich_html(rec.get("description") or "")
                ),
                self.cell(rec.get("contact_person")),
                self.cell(rec.get("division") or "—"),
                self.cell(rec.get("email")),
                self.cell(rec.get("phone")),
                self.cell(rec.get("notes") or "—", wrap=True),
                self.cell(
                    status_val,
                    "pay_status",
                    pkey=rec.get("pkey", ""),
                    status=status_val,
                    options=status_opts
                ),
                self.cell("Delete", "delete", pkey=rec.get("pkey", ""))
            ]})
        # end for
        return self.make_table(
            ["Business", "Description", "PIC", "Division", "Email", "Phone", "Notes", "Status", ""],
            rows,
            pager,
            "No vendors yet. Public applications and manual adds appear here."
        )
    # end def

    def vendor_categories(self):
        recs = self.list_rows("db_vendor_category", {"status": "ENABLE"}, "order", 1)
        names = []
        for rec in recs:
            name = (rec.get("name") or "").strip()
            if name != "":
                names.append(name)
            # end if
        # end for
        if names == []:
            names = [
                "Catering", "Audio Visual", "Event Equipment", "Media",
                "Venue Support", "Decoration", "Transportation", "Other Event Services"
            ]
        # end if
        return names
    # end def

    def division_names(self):
        recs = self.list_rows("db_division", {"status": "ENABLE"}, "order", 1)
        names = []
        for rec in recs:
            name = (rec.get("name") or "").strip()
            if name != "":
                names.append(name)
            # end if
        # end for
        if names == []:
            names = [
                "Sponsorship", "Proposal Handler", "Merchandise", "University Fair",
                "FRACO Member Kit", "Career Workshop", "Gift Planner",
                "Social Media Admin", "Spiritual Affairs", "Event Vendor Handler"
            ]
        # end if
        return names
    # end def

    def save_vendor_app(self, pkey, params):
        response = {"status": "FAILED", "desc": "", "pkey": pkey}
        business_name = (params.get("business_name") or "").strip()
        if business_name == "":
            response["desc"] = "Business name is required"
            return response
        # end if
        status = (params.get("status") or "Approved").strip()
        if status not in self.VENDOR_STATUSES:
            status = "Approved"
        # end if
        fields = {
            "business_name": business_name,
            "contact_person": (params.get("contact_person") or "").strip(),
            "email": (params.get("email") or "").strip().lower(),
            "phone": (params.get("phone") or "").strip(),
            "division": (params.get("division") or "").strip(),
            "description": (params.get("description") or "").strip(),
            "services": (params.get("services") or "").strip(),
            "profile": (params.get("profile") or "").strip(),
            "portfolio": (params.get("portfolio") or "").strip(),
            "pricing": (params.get("pricing") or "").strip(),
            "notes": (params.get("notes") or "").strip(),
            "assigned_pic": (params.get("assigned_pic") or "").strip(),
            "status": status
        }
        if "category" in params:
            fields["category"] = (params.get("category") or "").strip()
        # end if
        return self.save_row(
            "db_vendor_app",
            pkey,
            fields,
            preserve_html=["description"]
        )
    # end def

    def table_universities(self):
        return self.table_university_applications()
    # end def

    def table_university_applications(self):
        apps, app_pager = self.fetch_page(
            "db_program_reg",
            "/admin/universities",
            {"fk_program_slug": "university-fair"}
        )
        app_rows = []
        for rec in apps:
            show = rec.get("show_campus") == True or rec.get("show_campus") in ["1", "YES", "true", "on"]
            logo = (rec.get("logo") or "").strip()
            app_rows.append({"cells": [
                self.cell(
                    rec.get("organization") or rec.get("full_name") or "Application",
                    "link",
                    "/admin/universities/" + rec.get("pkey", "")
                ),
                self.cell(rec.get("full_name")),
                self.cell(rec.get("email")),
                self.cell(rec.get("phone")),
                self.cell("Yes" if show else "No"),
                self.cell("Yes" if logo != "" else "—"),
                self.cell(rec.get("status"), "status"),
                self.cell(self.display_date(rec))
            ]})
        # end for
        return self.make_table(
            ["Campus / org", "Contact", "Email", "Phone", "Show on site", "Logo", "Status", "Date"],
            app_rows,
            app_pager,
            "No booth applications."
        )
    # end def

    def receive_account_label(self, rec):
        if rec == None:
            return "Not assigned"
        # end if
        label = (rec.get("label") or "").strip()
        if label != "":
            return label
        # end if
        bank = (rec.get("bank_name") or "").strip()
        number = (rec.get("account_number") or "").strip()
        if bank != "" and number != "":
            return bank + " · " + number
        # end if
        return bank or number or "Not assigned"
    # end def

    def merchandise_category_rows(self, enabled_only=False):
        if self.mgdDB.db_merchandise_category.count_documents({}) == 0:
            for index, name in enumerate(self.DEFAULT_MERCHANDISE_CATEGORIES):
                rec = database.new(self.mgdDB, "db_merchandise_category")
                rec.put("name", name)
                rec.put("order", index + 1)
                rec.put("status", "ENABLE")
                rec.insert()
            # end for
        # end if
        query = {}
        if enabled_only:
            query["status"] = "ENABLE"
        # end if
        return self.list_rows("db_merchandise_category", query, "order", 1)
    # end def

    def merchandise_categories(self):
        names = []
        for rec in self.merchandise_category_rows(True):
            name = (rec.get("name") or "").strip()
            if name != "" and name not in names:
                names.append(name)
            # end if
        # end for
        return names
    # end def

    def finance_member_options(self):
        recs = self.list_rows("db_participant", {"member_type": "AHC_MEMBER"}, "full_name", 1)
        legacy = self.list_rows(
            "db_participant",
            {"member_type": {"$nin": ["AHC_MEMBER", "ALUMNI"]}},
            "full_name",
            1
        )
        recs.extend(legacy)
        options = []
        for rec in recs:
            name = (rec.get("full_name") or "").strip()
            if name == "":
                continue
            # end if
            options.append({
                "pkey": rec.get("pkey") or "",
                "name": name,
                "referral_code": rec.get("referral_code") or "",
                "reg_id": rec.get("reg_id") or ""
            })
        # end for
        return options
    # end def

    def finance_member(self, pkey):
        member = self.get_row("db_participant", pkey)
        if member == None:
            return None
        # end if
        if (member.get("member_type") or "") == "ALUMNI":
            return None
        # end if
        return member
    # end def

    def save_merchandise_category(self, pkey, params):
        name = (params.get("name") or "").strip()
        if name == "":
            return {"status": "FAILED", "desc": "Category name is required"}
        # end if
        for rec in self.merchandise_category_rows(False):
            if rec.get("pkey") != pkey and (rec.get("name") or "").strip().lower() == name.lower():
                return {"status": "FAILED", "desc": "Category already exists"}
            # end if
        # end for
        status = (params.get("status") or "ENABLE").strip().upper()
        if status not in ["ENABLE", "DISABLE"]:
            status = "ENABLE"
        # end if
        return self.save_row("db_merchandise_category", pkey, {
            "name": name,
            "order": self.parse_int(params.get("order")),
            "status": status
        })
    # end def

    def shipping_expedition_rows(self, enabled_only=False):
        if self.mgdDB.db_shipping_expedition.count_documents({}) == 0:
            for index, name in enumerate(self.DEFAULT_SHIPPING_EXPEDITIONS):
                rec = database.new(self.mgdDB, "db_shipping_expedition")
                rec.put("name", name)
                rec.put("order", index + 1)
                rec.put("status", "ENABLE")
                rec.insert()
            # end for
        # end if
        query = {}
        if enabled_only:
            query["status"] = "ENABLE"
        # end if
        return self.list_rows("db_shipping_expedition", query, "order", 1)
    # end def

    def shipping_expeditions(self):
        return [
            rec.get("name") for rec in self.shipping_expedition_rows(True)
            if (rec.get("name") or "").strip() != ""
        ]
    # end def

    def save_shipping_expedition(self, pkey, params):
        name = (params.get("name") or "").strip()
        if name == "":
            return {"status": "FAILED", "desc": "Expedition name is required"}
        # end if
        for rec in self.shipping_expedition_rows(False):
            if rec.get("pkey") != pkey and (rec.get("name") or "").strip().lower() == name.lower():
                return {"status": "FAILED", "desc": "Expedition already exists"}
            # end if
        # end for
        status = (params.get("status") or "ENABLE").strip().upper()
        if status not in ["ENABLE", "DISABLE"]:
            status = "ENABLE"
        # end if
        return self.save_row("db_shipping_expedition", pkey, {
            "name": name,
            "order": self.parse_int(params.get("order")),
            "status": status
        })
    # end def

    def receive_accounts(self, enabled_only=False):
        query = {}
        if enabled_only:
            query["status"] = "ENABLE"
        # end if
        recs = self.list_rows("db_receive_account", query, "order", 1)
        for rec in recs:
            rec["display_label"] = self.receive_account_label(rec)
        # end for
        return recs
    # end def

    def save_receive_account(self, pkey, params):
        bank = (params.get("bank_name") or "").strip()
        number = (params.get("account_number") or "").strip()
        holder = (params.get("account_holder") or "").strip()
        if bank == "" or number == "" or holder == "":
            return {"status": "FAILED", "desc": "Bank, account number, and account holder are required"}
        # end if
        label = (params.get("label") or "").strip()
        if label == "":
            label = bank + " · " + number
        # end if
        status = (params.get("status") or "ENABLE").strip().upper()
        if status not in ["ENABLE", "DISABLE"]:
            status = "ENABLE"
        # end if
        return self.save_row("db_receive_account", pkey, {
            "label": label,
            "bank_name": bank,
            "account_number": number,
            "account_holder": holder,
            "order": self.parse_int(params.get("order")),
            "status": status
        })
    # end def

    def transaction_type_from_payment(self, rec):
        value = (rec.get("source_type") or rec.get("pay_type") or "Other").strip()
        aliases = {
            "participant contribution": "Contribution",
            "contribution": "Contribution",
            "merchandise": "Merch Sales",
            "merch sales": "Merch Sales",
            "proposal": "Proposal",
            "sponsorship": "Sponsor",
            "sponsor": "Sponsor",
            "shipping": "Shipping",
            "university booth": "Other",
            "other": "Other"
        }
        return aliases.get(value.lower(), "Other")
    # end def

    def transaction_page(self, source_filter="", account_filter="", kind_filter=""):
        transactions = []
        for rec in self.list_rows("db_payment"):
            source_type = self.transaction_type_from_payment(rec)
            transactions.append({
                "rec_timestamp": int(rec.get("rec_timestamp") or 0),
                "date": rec.get("transaction_date") or self.display_date(rec),
                "month_key": (rec.get("transaction_date") or rec.get("rec_timestamp_str") or "")[0:7],
                "name": rec.get("name") or rec.get("email") or rec.get("fk_reg_id") or "—",
                "transaction_kind": (rec.get("transaction_kind") or "INCOME").upper(),
                "source_type": source_type,
                "transaction_code": rec.get("source_ref") or "—",
                "referral_code": rec.get("referral_code") or "—",
                "account_pkey": rec.get("fk_receive_account") or "",
                "account_label": rec.get("receive_account_label") or "Not assigned",
                "amount_num": int(rec.get("amount_num") or 0),
                "amount": rec.get("amount") or self.format_rp(rec.get("amount_num")),
                "credit_num": 0,
                "credit": "—",
                "status": (rec.get("status") or "PENDING").upper(),
                "origin": "Manual",
                "pkey": rec.get("pkey") or "",
                "source_table": "db_payment",
                "source_pkey": rec.get("pkey") or ""
            })
        # end for
        for rec in self.list_rows("db_order", {
            "payment_status": "Paid",
            "order_status": {"$ne": "Cancelled"}
        }):
            profit_num = int(rec.get("profit_total_num") or 0)
            transactions.append({
                "rec_timestamp": int(rec.get("rec_timestamp") or 0),
                "date": self.display_date(rec),
                "month_key": (rec.get("rec_timestamp_str") or "")[0:7],
                "name": rec.get("full_name") or rec.get("email") or "—",
                "transaction_kind": "INCOME",
                "source_type": "Merch Sales",
                "transaction_code": rec.get("order_id") or "—",
                "referral_code": rec.get("referral_code") or "—",
                "account_pkey": rec.get("fk_receive_account") or "",
                "account_label": rec.get("receive_account_label") or "Not assigned",
                "amount_num": int(rec.get("total_num") or 0),
                "amount": rec.get("total") or self.format_rp(rec.get("total_num")),
                "credit_num": profit_num,
                "credit": rec.get("profit_total") or self.format_rp(profit_num),
                "status": "PAID",
                "origin": "Merch order",
                "pkey": "",
                "source_table": "db_order",
                "source_pkey": rec.get("pkey") or ""
            })
        # end for
        for rec in self.list_rows("db_order", {
            "shipping_handler": "OFFICER",
            "shipping_request_status": {"$in": ["PROCESSING", "SHIPPED", "COMPLETED"]},
            "order_status": {"$ne": "Cancelled"}
        }):
            shipping_expense_num = self.order_shipping_expense_num(rec)
            if shipping_expense_num <= 0:
                continue
            # end if
            transactions.append({
                "rec_timestamp": int(rec.get("rec_timestamp") or 0),
                "date": self.display_date(rec),
                "month_key": (rec.get("rec_timestamp_str") or "")[0:7],
                "name": rec.get("full_name") or rec.get("email") or "—",
                "transaction_kind": "EXPENSE",
                "source_type": "Shipping",
                "transaction_code": rec.get("order_id") or "—",
                "referral_code": rec.get("referral_code") or "—",
                "account_pkey": rec.get("fk_receive_account") or "",
                "account_label": rec.get("receive_account_label") or "Not assigned",
                "amount_num": shipping_expense_num,
                "amount": self.format_rp(shipping_expense_num),
                "credit_num": 0,
                "credit": "—",
                "status": "PAID",
                "origin": "Order shipping + packing service",
                "pkey": "",
                "source_table": "db_order",
                "source_pkey": rec.get("pkey") or ""
            })
        # end for
        for rec in self.list_rows("db_donor", {"follow_status": "RECEIVED"}):
            source_type = "Proposal"
            if self._is_self_pledge(rec):
                source_type = "Contribution"
            # end if
            transactions.append({
                "rec_timestamp": int(rec.get("rec_timestamp") or 0),
                "date": self.display_date(rec),
                "month_key": (rec.get("rec_timestamp_str") or "")[0:7],
                "name": rec.get("name") or "—",
                "transaction_kind": "INCOME",
                "source_type": source_type,
                "transaction_code": "—",
                "referral_code": rec.get("referral_code") or "—",
                "account_pkey": rec.get("fk_receive_account") or "",
                "account_label": rec.get("receive_account_label") or "Not assigned",
                "amount_num": int(rec.get("amount_num") or 0),
                "amount": rec.get("amount_label") or self.format_rp(rec.get("amount_num")),
                "credit_num": int(rec.get("amount_num") or 0),
                "credit": rec.get("amount_label") or self.format_rp(rec.get("amount_num")),
                "status": "PAID",
                "origin": "Support Us",
                "pkey": "",
                "source_table": "db_donor",
                "source_pkey": rec.get("pkey") or ""
            })
        # end for
        transactions.sort(key=lambda item: item.get("rec_timestamp") or 0, reverse=True)

        totals = {}
        monthly_totals = {}
        income_total = 0
        expense_total = 0
        fundraising_total = 0
        income_count = 0
        expense_count = 0
        for source_type in self.TRANSACTION_TYPES:
            totals[source_type] = 0
        # end for
        for item in transactions:
            if item.get("status") != "PAID":
                continue
            # end if
            source_type = item.get("source_type") or "Other"
            amount_num = int(item.get("amount_num") or 0)
            if item.get("transaction_kind") == "EXPENSE":
                expense_total = expense_total + amount_num
                expense_count = expense_count + 1
                continue
            # end if
            totals[source_type] = totals.get(source_type, 0) + amount_num
            income_total = income_total + amount_num
            fundraising_total = fundraising_total + int(item.get("credit_num") or 0)
            income_count = income_count + 1
            month_key = item.get("month_key") or ""
            if re.match(r"^\d{4}-\d{2}$", month_key):
                monthly_totals[month_key] = monthly_totals.get(month_key, 0) + amount_num
            # end if
        # end for

        source_clean = (source_filter or "").strip()
        account_clean = (account_filter or "").strip()
        kind_clean = (kind_filter or "").strip().upper()
        filtered = []
        for item in transactions:
            if kind_clean != "" and item.get("transaction_kind") != kind_clean:
                continue
            # end if
            if source_clean != "" and item.get("source_type") != source_clean:
                continue
            # end if
            if account_clean != "" and item.get("account_pkey") != account_clean:
                continue
            # end if
            filtered.append(item)
        # end for
        extra_qs = "&tab=transactions"
        if source_clean != "":
            extra_qs = extra_qs + "&type=" + quote_plus(source_clean)
        # end if
        if account_clean != "":
            extra_qs = extra_qs + "&account=" + quote_plus(account_clean)
        # end if
        if kind_clean != "":
            extra_qs = extra_qs + "&kind=" + quote_plus(kind_clean)
        # end if
        page_rows, pager = self.slice_page(filtered, "/admin/payments", extra_qs)
        rows = []
        for rec in page_rows:
            rows.append({"cells": [
                self.cell(rec.get("date")),
                self.cell(rec.get("transaction_kind").title()),
                self.cell(rec.get("source_type")),
                self.cell(rec.get("name")),
                self.cell(rec.get("transaction_code")),
                self.cell(rec.get("referral_code")),
                self.cell(rec.get("account_label")),
                self.cell(rec.get("amount")),
                self.cell(rec.get("credit")),
                self.cell(rec.get("status"), "status")
            ]})
        # end for
        table = self.make_table(
            ["Date", "Type", "Source", "Name", "Transaction code", "Referral code", "Account", "Cash amount", "Fundraising credit", "Status"],
            rows,
            pager,
            "No transactions match this filter."
        )
        source_totals = []
        for item in self.TRANSACTION_TYPES:
            amount_num = totals.get(item, 0)
            pct = 0
            if income_total > 0:
                pct = int(round(100.0 * amount_num / income_total))
            # end if
            source_totals.append({
                "label": item,
                "amount": self.format_rp(amount_num),
                "pct": pct
            })
        # end for
        month_keys = sorted(monthly_totals.keys())[-12:]
        month_max = 0
        for month_key in month_keys:
            if monthly_totals.get(month_key, 0) > month_max:
                month_max = monthly_totals.get(month_key, 0)
            # end if
        # end for
        income_by_month = []
        for month_key in month_keys:
            amount_num = monthly_totals.get(month_key, 0)
            pct = 0
            if month_max > 0:
                pct = int(round(100.0 * amount_num / month_max))
            # end if
            income_by_month.append({
                "label": month_key,
                "amount": self.format_rp(amount_num),
                "pct": pct
            })
        # end for
        net_total = income_total - expense_total
        net_label = self.format_rp(net_total)
        if net_total < 0:
            net_label = "-" + self.format_rp(abs(net_total))
        # end if
        return {
            "table": table,
            "paid_total": self.format_rp(income_total),
            "income_total": self.format_rp(income_total),
            "expense_total": self.format_rp(expense_total),
            "net_total": net_label,
            "fundraising_total": self.format_rp(fundraising_total),
            "paid_count": income_count,
            "income_count": income_count,
            "expense_count": expense_count,
            "source_totals": source_totals,
            "income_by_month": income_by_month
        }
    # end def

    def table_payments(self):
        return self.transaction_page().get("table")
    # end def

    def table_content(self):
        recs, pager = self.fetch_page("db_update", "/admin/content")
        rows = []
        for rec in recs:
            rows.append({"cells": [
                self.cell(rec.get("title"), "link", "/admin/content/" + rec.get("pkey", "")),
                self.cell(rec.get("category")),
                self.cell(rec.get("date")),
                self.cell(rec.get("status"), "status")
            ]})
        # end for
        return self.make_table(["Title", "Category", "Date", "Status"], rows, pager, "No articles.")
    # end def

    def table_gallery(self):
        recs, pager = self.fetch_page("db_gallery", "/admin/gallery", sort_field="order", direction=1)
        rows = []
        for rec in recs:
            rows.append({"cells": [
                self.cell(rec.get("alt"), "image", src=rec.get("image") or "", alt=rec.get("alt") or ""),
                self.cell(rec.get("album")),
                self.cell(rec.get("alt")),
                self.cell(rec.get("order")),
                self.cell("Delete", "delete", pkey=rec.get("pkey", ""))
            ]})
        # end for
        return self.make_table(["Image", "Album", "Caption", "Order", ""], rows, pager, "No images.")
    # end def

    def table_team(self):
        recs, pager = self.fetch_page("db_team", "/admin/team", sort_field="order", direction=1)
        rows = []
        for rec in recs:
            rows.append({"cells": [
                self.cell(rec.get("name")),
                self.cell(rec.get("position")),
                self.cell(rec.get("division")),
                self.cell(rec.get("order")),
                self.cell("Delete", "delete", pkey=rec.get("pkey", ""))
            ]})
        # end for
        return self.make_table(
            ["Name", "Position", "Division", "Order", ""],
            rows,
            pager,
            "No people listed. Divisions on the public About page stay as they are."
        )
    # end def

    def table_donors(self):
        follow = (request.args.get("follow") or "").strip().upper()
        extra = None
        extra_qs = "&tab=pledges"
        if follow in self.DONOR_FOLLOW_STATUSES:
            extra = {"follow_status": follow}
            extra_qs = extra_qs + "&follow=" + quote_plus(follow)
        # end if
        recs, pager = self.fetch_page(
            "db_donor",
            "/admin/donations",
            extra,
            sort_field="rec_timestamp",
            direction=-1,
            extra_qs=extra_qs
        )
        rows = []
        for rec in recs:
            follow_key = (rec.get("follow_status") or "FOLLOW_UP").upper()
            follow_label = self.DONOR_FOLLOW_LABELS.get(follow_key, follow_key)
            amount = rec.get("amount_label") or self.format_rp(rec.get("amount_num"))
            ref = (rec.get("referral_code") or "").strip()
            ref_label = ref if ref != "" else "—"
            if self._is_self_pledge(rec):
                source_label = "Own contribution"
            else:
                source_label = "Support Us"
            # end if
            rows.append({"cells": [
                self.cell(rec.get("name"), "link", "/admin/donations?tab=add&edit=" + rec.get("pkey", "")),
                self.cell(
                    "Anonymous" if rec.get("is_anonymous") == True else "Full name",
                    "donor_anonymous",
                    pkey=rec.get("pkey", ""),
                    status="YES" if rec.get("is_anonymous") == True else "NO"
                ),
                self.cell(rec.get("phone") or "—"),
                self.cell(amount or "—"),
                self.cell(source_label),
                self.cell(ref_label),
                self.cell(rec.get("score")),
                self.cell(
                    follow_label,
                    "donor_follow",
                    pkey=rec.get("pkey", ""),
                    status=follow_key,
                    options=[
                        {"value": "FOLLOW_UP", "label": self.DONOR_FOLLOW_LABELS["FOLLOW_UP"]},
                        {"value": "RECEIVED", "label": self.DONOR_FOLLOW_LABELS["RECEIVED"]}
                    ]
                ),
                self.cell("Delete", "delete", pkey=rec.get("pkey", ""))
            ]})
        # end for
        table = self.make_table(
            ["Name", "Public display", "Phone", "Nominal", "Source", "Referral", "Score", "Follow-up", ""],
            rows,
            pager,
            "No pledges yet. Public form submissions and manual adds appear here."
        )
        filters = [{
            "label": "All",
            "href": "/admin/donations?tab=pledges",
            "active": follow == ""
        }]
        for key in self.DONOR_FOLLOW_STATUSES:
            filters.append({
                "label": self.DONOR_FOLLOW_LABELS.get(key, key),
                "href": "/admin/donations?tab=pledges&follow=" + quote_plus(key),
                "active": follow == key
            })
        # end for
        table["filters"] = filters
        table["follow_filter"] = follow
        return table
    # end def

    def get_donation_settings(self):
        from support.support_proc import support_proc
        return support_proc().get_settings()
    # end def

    def save_donation_settings(self, params):
        settings = self.get_donation_settings()
        pkey = settings.get("pkey") or ""
        list_mode = (params.get("list_mode") or "LIMIT").upper()
        if list_mode not in ["LIMIT", "ALL"]:
            list_mode = "LIMIT"
        # end if
        public_total_mode = (params.get("public_total_mode") or "ACCUMULATED").upper()
        if public_total_mode not in ["ACCUMULATED", "CUSTOM", "HIDDEN"]:
            public_total_mode = "ACCUMULATED"
        # end if
        fields = {
            "title": params.get("title") or "Support Us",
            "intro": "",
            "email": params.get("email") or "",
            "whatsapp": params.get("whatsapp") or "",
            "whatsapp_url": params.get("whatsapp_url") or "",
            "phone": params.get("phone") or "",
            "follow_up_note": "",
            "top_limit": self.parse_int(params.get("top_limit")),
            "list_mode": list_mode,
            "public_total_mode": public_total_mode,
            "public_total_num": self.parse_int(params.get("public_total_num")),
            "status": params.get("status") or "ENABLE"
        }
        return self.save_row("db_donation_settings", pkey, fields)
    # end def

    def save_support_proposal_pdf(self, params, file_obj=None):
        settings = self.get_donation_settings()
        pkey = settings.get("pkey") or ""
        label = (params.get("proposal_pdf_label") or "Download proposal (PDF)").strip()
        if label == "":
            label = "Download proposal (PDF)"
        # end if
        fields = {
            "proposal_pdf_label": label,
            "proposal_pdf_url": settings.get("proposal_pdf_url") or ""
        }
        remove = (params.get("remove_proposal_pdf") or "").upper() == "YES"
        if remove:
            self.delete_local_upload(settings.get("proposal_pdf_url"))
            fields["proposal_pdf_url"] = ""
            return self.save_row("db_donation_settings", pkey, fields)
        # end if
        if file_obj != None and file_obj.filename != "":
            stored, rel = self.save_upload(file_obj, "support")
            if stored == "ERR_TYPE":
                return {"status": "FAILED", "desc": "Upload a PDF file only."}
            # end if
            if stored == "":
                return {"status": "FAILED", "desc": "Could not save the PDF file."}
            # end if
            ext = stored.rsplit(".", 1)[-1].lower() if "." in stored else ""
            if ext != "pdf":
                self.delete_local_upload(rel)
                return {"status": "FAILED", "desc": "Upload a PDF file only."}
            # end if
            old_url = settings.get("proposal_pdf_url") or ""
            if old_url != "":
                self.delete_local_upload(old_url)
            # end if
            fields["proposal_pdf_url"] = rel
        # end if
        return self.save_row("db_donation_settings", pkey, fields)
    # end def

    def save_donor(self, pkey, params):
        name = (params.get("name") or "").strip()
        if name == "":
            return {"status": "FAILED", "desc": "Name is required"}
        # end if
        follow_status = (params.get("follow_status") or "FOLLOW_UP").upper()
        if follow_status not in self.DONOR_FOLLOW_STATUSES:
            follow_status = "FOLLOW_UP"
        # end if
        if follow_status == "RECEIVED":
            status = "ENABLE"
        else:
            status = "HIDDEN"
        # end if
        amount_num = self.parse_int(params.get("amount_num") or params.get("amount_label"))
        amount_label = (params.get("amount_label") or "").strip()
        if amount_label == "" and amount_num > 0:
            amount_label = self.format_rp(amount_num)
        # end if
        score = self.parse_int(params.get("score"))
        if score <= 0 and amount_num > 0:
            score = amount_num
        # end if
        old = None
        if pkey != "":
            old = self.get_row("db_donor", pkey)
        # end if
        result = self.save_row("db_donor", pkey, {
            "name": name,
            "is_anonymous": params.get("is_anonymous") in ["YES", "1", "true", "on", "True"],
            "phone": params.get("phone") or "",
            "amount_label": amount_label,
            "amount_num": amount_num,
            "score": score,
            "note": params.get("note") or "",
            "follow_status": follow_status,
            "status": status
        })
        referrer_ids = []
        if old != None:
            self.sync_donor_referrers(old)
        # end if
        if result.get("status") == "SUCCESS":
            saved = self.get_row("db_donor", result.get("pkey") or pkey)
            self.sync_donor_referrers(saved)
        # end if
        return result
    # end def

    def update_donor_anonymous(self, pkey, is_anonymous):
        value = (is_anonymous or "").strip().upper() == "YES"
        return self.save_row("db_donor", pkey, {"is_anonymous": value})
    # end def

    def update_donor_follow(self, pkey, follow_status):
        response = {"status": "FAILED", "desc": ""}
        rec = self.get_row("db_donor", pkey)
        if rec == None:
            response["desc"] = "Pledge not found"
            return response
        # end if
        follow = (follow_status or "").strip().upper()
        if follow not in self.DONOR_FOLLOW_STATUSES:
            response["desc"] = "Invalid follow-up status"
            return response
        # end if
        fields = {"follow_status": follow}
        if follow == "RECEIVED":
            fields["status"] = "ENABLE"
        elif follow == "FOLLOW_UP":
            fields["status"] = "HIDDEN"
        # end if
        result = self.save_row("db_donor", pkey, fields)
        if result.get("status") == "SUCCESS":
            self.sync_donor_referrers(rec)
            saved = self.get_row("db_donor", pkey)
            self.sync_donor_referrers(saved)
        # end if
        return result
    # end def

    def table_users(self):
        recs, pager = self.fetch_page(
            "db_user",
            "/admin/users",
            {"role": {"$in": self.ADMIN_ROLES}},
            sort_field="name",
            direction=1
        )
        rows = []
        for rec in recs:
            rows.append({"cells": [
                self.cell(rec.get("name"), "link", "/admin/users/" + rec.get("pkey", "")),
                self.cell(rec.get("email")),
                self.cell(self.role_label(rec.get("role"))),
                self.cell(rec.get("status"), "status")
            ]})
        # end for
        help_rows = []
        for item in self.ROLE_HELP:
            help_rows.append({"cells": [
                self.cell(self.role_label(item[0])),
                self.cell(item[1], wrap=True)
            ]})
        # end for
        return {
            "list_table": self.make_table(["Name", "Email", "Role", "Status"], rows, pager, "No staff users."),
            "help_table": self.make_table(["Role", "Access"], help_rows, None, "")
        }
    # end def

    def table_participant_payments(self, recs):
        rows = []
        for rec in recs:
            rows.append({"cells": [
                self.cell(self.display_date(rec)),
                self.cell(rec.get("amount")),
                self.cell(rec.get("status"), "status"),
                self.cell(rec.get("note"), wrap=True)
            ]})
        # end for
        return self.make_table(["Date", "Amount", "Status", "Note"], rows, None, "No payment rows.")
    # end def

    def table_participant_orders(self, recs):
        rows = []
        for rec in recs:
            rows.append({"cells": [
                self.cell(rec.get("order_id"), "link", "/admin/orders/" + rec.get("pkey", "")),
                self.cell(rec.get("full_name")),
                self.cell(self.display_date(rec)),
                self.cell(rec.get("subtotal")),
                self.cell(rec.get("total")),
                self.cell(rec.get("payment_status") or "—", "status"),
                self.cell(rec.get("order_status"), "status")
            ]})
        # end for
        return self.make_table(
            ["Order ID", "Buyer", "Date", "Subtotal", "Total", "Payment", "Status"],
            rows,
            None,
            "No merchandise orders with this referral."
        )
    # end def

    def table_member_pledges(self, recs, empty="No pledges."):
        rows = []
        for rec in recs:
            follow_key = (rec.get("follow_status") or "FOLLOW_UP").upper()
            follow_label = self.DONOR_FOLLOW_LABELS.get(follow_key, follow_key)
            amount = rec.get("amount_label") or self.format_rp(rec.get("amount_num"))
            rows.append({"cells": [
                self.cell(rec.get("name"), "link", "/admin/donations?tab=add&edit=" + rec.get("pkey", "")),
                self.cell(rec.get("phone") or "—"),
                self.cell(amount or "—"),
                self.cell(follow_label, "status", status=follow_key),
                self.cell(self.display_date(rec)),
                self.cell(rec.get("note") or "—", wrap=True)
            ]})
        # end for
        return self.make_table(
            ["Name", "Phone", "Amount", "Follow-up", "Date", "Note"],
            rows,
            None,
            empty
        )
    # end def

    def member_referral_orders(self, rec):
        if rec == None:
            return []
        # end if
        orders = []
        pkey = rec.get("pkey") or ""
        if pkey != "":
            orders = self.list_rows("db_order", {"fk_referrer_id": pkey})
        # end if
        if orders == [] and (rec.get("referral_code") or "") != "":
            orders = self.list_rows("db_order", {
                "referral_code": (rec.get("referral_code") or "").strip().lower()
            })
        # end if
        return orders
    # end def

    def configured_shipping_service_fee_num(self):
        site = self.site.get_site() or {}
        value = site.get("shipping_service_fee_num")
        fee = int(10000 if value == None else value)
        return max(0, fee)
    # end def

    def order_shipping_service_fee_num(self, order):
        if "shipping_service_fee_num" in (order or {}):
            return max(0, int(order.get("shipping_service_fee_num") or 0))
        # end if
        return self.configured_shipping_service_fee_num()
    # end def

    def order_shipping_expense_num(self, order):
        return (
            int((order or {}).get("shipping_budget_num") or 0) +
            self.order_shipping_service_fee_num(order)
        )
    # end def

    def member_shipping_expense_num(self, rec, exclude_order_pkey=""):
        total = 0
        for order in self.member_referral_orders(rec):
            if order.get("pkey") == exclude_order_pkey:
                continue
            # end if
            if order.get("shipping_handler") != "OFFICER":
                continue
            # end if
            if (order.get("shipping_request_status") or "").strip().upper() not in ["PROCESSING", "SHIPPED", "COMPLETED"]:
                continue
            # end if
            if (order.get("order_status") or "") == "Cancelled":
                continue
            # end if
            total = total + self.order_shipping_expense_num(order)
        # end for
        return total
    # end def

    def member_linked_pledges(self, rec):
        if rec == None:
            return []
        # end if
        pkey = rec.get("pkey") or ""
        code = (rec.get("referral_code") or "").strip().lower()
        clauses = []
        if pkey != "":
            clauses.append({"fk_referrer_id": pkey})
        # end if
        if code != "":
            clauses.append({"referral_code": code})
        # end if
        if clauses == []:
            return []
        # end if
        return list(self.mgdDB.db_donor.find(
            {"is_deleted": False, "$or": clauses},
            {"_id": 0}
        ).sort("rec_timestamp", -1))
    # end def

    def participant_detail(self, rec, tab="details"):
        tab = (tab or "details").strip().lower()
        is_alumni = (rec.get("member_type") or "") == "ALUMNI"
        allowed = ["details"]
        if not is_alumni:
            allowed = ["details", "summary", "merch", "proposal", "contribution"]
        # end if
        if tab not in allowed:
            tab = "details"
        # end if
        self.sync_participant_money(rec.get("pkey") or "")
        rec = self.get_row("db_participant", rec.get("pkey") or "") or rec
        target = self._member_target(rec)
        prop, self_amt = self._member_pledge_totals(rec)
        sold = int(rec.get("sales_total_num") or 0)
        shipping_expense = self.member_shipping_expense_num(rec)
        combined = sold + prop + self_amt - shipping_expense
        if combined < 0:
            combined = 0
        # end if
        left = target - combined
        if left < 0:
            left = 0
        # end if
        orders = self.member_referral_orders(rec)
        pledges = self.member_linked_pledges(rec)
        proposal_rows = []
        own_rows = []
        proposal_pending = 0
        own_pending = 0
        for item in pledges:
            amount = int(item.get("amount_num") or 0)
            follow = (item.get("follow_status") or "").upper()
            if self._is_self_pledge(item):
                own_rows.append(item)
                if follow != "RECEIVED":
                    own_pending = own_pending + amount
                # end if
            else:
                proposal_rows.append(item)
                if follow != "RECEIVED":
                    proposal_pending = proposal_pending + amount
                # end if
            # end if
        # end for
        paid_orders = 0
        for order in orders:
            if (order.get("payment_status") or "") == "Paid":
                paid_orders = paid_orders + 1
            # end if
        # end for
        merch_pct = self._track_pct(sold, target)
        prop_pct = self._track_pct(prop, target)
        self_pct = self._track_pct(self_amt, target)
        combined_pct = self._track_pct(combined, target)
        return {
            "part_tab": tab,
            "row": rec,
            "login": self.get_participant_login(rec),
            "is_alumni": is_alumni,
            "summary": {
                "target": self.format_rp(target),
                "target_num": target,
                "merch": self.format_rp(sold),
                "merch_num": sold,
                "merch_pct": merch_pct,
                "merch_marker": self._marker_pct(merch_pct),
                "proposal": self.format_rp(prop),
                "proposal_num": prop,
                "proposal_pct": prop_pct,
                "proposal_marker": self._marker_pct(prop_pct),
                "proposal_pending": self.format_rp(proposal_pending),
                "own": self.format_rp(self_amt),
                "own_num": self_amt,
                "own_pct": self_pct,
                "own_marker": self._marker_pct(self_pct),
                "own_pending": self.format_rp(own_pending),
                "shipping_expense": self.format_rp(shipping_expense),
                "shipping_expense_num": shipping_expense,
                "combined": self.format_rp(combined),
                "combined_num": combined,
                "combined_pct": combined_pct,
                "combined_marker": self._marker_pct(combined_pct),
                "left": self.format_rp(left),
                "pct": combined_pct,
                "order_count": len(orders),
                "paid_order_count": paid_orders,
                "proposal_count": len(proposal_rows),
                "own_count": len(own_rows),
                "achieved": left <= 0 and combined > 0
            },
            "referral_table": self.table_participant_orders(orders),
            "proposal_table": self.table_member_pledges(
                proposal_rows,
                "No Support Us pledges from others for this referral."
            ),
            "contribution_table": self.table_member_pledges(
                own_rows,
                "No own contribution pledges yet."
            )
        }
    # end def

    def find_order_referrer(self, order):
        if order == None:
            return None
        # end if
        rid = (order.get("fk_referrer_id") or "").strip()
        if rid != "":
            referrer = self.get_row("db_participant", rid)
            if referrer != None:
                return referrer
            # end if
        # end if
        code = (order.get("referral_code") or "").strip().lower()
        if code != "":
            return self.mgdDB.db_participant.find_one(
                {"referral_code": code, "is_deleted": False},
                {"_id": 0}
            )
        # end if
        return None
    # end def

    def order_referrer_label(self, order):
        code = (order.get("referral_code") or "").strip().lower()
        referrer = self.find_order_referrer(order)
        if referrer != None:
            name = (referrer.get("full_name") or "").strip()
            ref_code = (referrer.get("referral_code") or code or "").strip().lower()
            if name != "" and ref_code != "":
                return name + " · " + ref_code
            # end if
            if name != "":
                return name
            # end if
            if ref_code != "":
                return ref_code
            # end if
        # end if
        if code != "":
            return code
        # end if
        return "—"
    # end def

    def shipping_document_data(self, order):
        referrer = self.find_order_referrer(order) or {}
        sender_name = (referrer.get("full_name") or "").strip()
        sender_phone = (referrer.get("phone") or "").strip()
        participant_login = self.get_participant_login(referrer) if referrer != {} else {}
        sender_user = participant_login.get("user") or {}
        if sender_name == "":
            sender_name = (sender_user.get("name") or "").strip()
        # end if
        if sender_phone == "":
            sender_phone = (sender_user.get("phone") or "").strip()
        # end if
        items = []
        for line in order.get("items") or []:
            item_options = []
            if (line.get("size") or "").strip() != "":
                item_options.append("Size: " + (line.get("size") or "").strip())
            # end if
            if (line.get("color") or "").strip() != "":
                item_options.append("Color: " + (line.get("color") or "").strip())
            # end if
            sku = (line.get("sku") or line.get("variant_sku") or "").strip()
            if sku != "":
                item_options.append("SKU: " + sku)
            # end if
            items.append({
                "name": line.get("name") or "Merchandise",
                "qty": int(line.get("qty") or 1),
                "options": " · ".join(item_options)
            })
        # end for
        return {
            "order_id": order.get("order_id") or order.get("pkey") or "",
            "sender_name": sender_name or "—",
            "sender_phone": sender_phone or "—",
            "recipient_name": order.get("shipping_name") or order.get("full_name") or "—",
            "recipient_phone": order.get("shipping_phone") or order.get("phone") or "—",
            "recipient_address": order.get("shipping_address") or order.get("address") or "—",
            "recipient_city": order.get("shipping_city") or order.get("city") or "",
            "recipient_postal_code": order.get("shipping_postal_code") or order.get("postal_code") or "",
            "package_note": order.get("shipping_package_note") or "",
            "items": items
        }
    # end def

    def officer_shipping_documents(self, status="", pay="", q="", order_pkeys=None):
        clauses = [
            {"is_deleted": False},
            {"shipping_handler": "OFFICER"}
        ]
        selected_pkeys = [
            pkey for pkey in (order_pkeys or []) if (pkey or "").strip() != ""
        ]
        if order_pkeys is not None:
            clauses.append({"pkey": {"$in": selected_pkeys}})
        # end if
        if status in self.ORDER_STATUSES:
            clauses.append({"order_status": status})
        # end if
        if pay in self.ORDER_PAY_STATUSES:
            clauses.append({"payment_status": pay})
        # end if
        clean_q = (q or "").strip()
        if clean_q != "":
            pattern = re.escape(clean_q)
            clauses.append({"$or": [
                {"order_id": {"$regex": pattern, "$options": "i"}},
                {"full_name": {"$regex": pattern, "$options": "i"}}
            ]})
        # end if
        rows = list(self.mgdDB.db_order.find(
            {"$and": clauses},
            {"_id": 0}
        ).sort("rec_timestamp", -1))
        return [self.shipping_document_data(row) for row in rows]
    # end def

    def table_order_items(self, rec):
        rows = []
        for index, line in enumerate(rec.get("items") or []):
            line_status = (line.get("line_status") or rec.get("order_status") or "Pending Payment").strip()
            rows.append({"cells": [
                self.cell(line.get("name"), wrap=True),
                self.cell(line.get("qty")),
                self.cell(line.get("size")),
                self.cell(line.get("color")),
                self.cell(line.get("line_price")),
                self.cell(line.get("line_bahan_baku") or "—"),
                self.cell(line.get("line_profit") or "—"),
                self.cell("Preorder" if line.get("is_preorder") else "Ready"),
                self.cell(
                    line_status,
                    "order_line_status",
                    pkey=rec.get("pkey") or "",
                    index=index,
                    status=line_status,
                    options=self.order_status_options(line_status)
                )
            ]})
        # end for
        return self.make_table(
            ["Item", "Qty", "Size", "Color", "Line price", "Bahan baku", "Profit", "Type", "Shipment status"],
            rows,
            None,
            "No items."
        )
    # end def

    def order_status_options(self, current=""):
        options = list(self.ORDER_STATUSES)
        if current != "" and current not in options:
            options.insert(0, current)
        # end if
        return options
    # end def

    def shipping_status_options(self):
        return [
            {
                "value": status,
                "label": self.SHIPPING_STATUS_LABELS.get(status, status)
            }
            for status in self.SHIPPING_STATUSES
        ]
    # end def

    def update_order_line_status(self, pkey, index, status):
        order = self.get_row("db_order", pkey)
        if order == None:
            return {"status": "FAILED", "desc": "Order not found"}
        # end if
        if status not in self.ORDER_STATUSES:
            return {"status": "FAILED", "desc": "Invalid shipment status"}
        # end if
        try:
            line_index = int(index)
        except Exception:
            return {"status": "FAILED", "desc": "Invalid order item"}
        # end try
        items = []
        found = False
        for item_index, line in enumerate(order.get("items") or []):
            row = dict(line)
            if item_index == line_index:
                row["line_status"] = status
                found = True
            # end if
            items.append(row)
        # end for
        if not found:
            return {"status": "FAILED", "desc": "Order item not found"}
        # end if
        self.mgdDB.db_order.update_one(
            {"pkey": pkey},
            {"$set": {"items": items}}
        )
        return {"status": "SUCCESS", "desc": ""}
    # end def

    def order_pay_options(self, current=""):
        return list(self.ORDER_PAY_STATUSES)
    # end def

    def pick_order_pay(self, value, fallback):
        if value in self.ORDER_PAY_STATUSES:
            return value
        # end if
        return fallback
    # end def

    def save_order_shipping(self, pkey, params):
        order = self.get_row("db_order", pkey)
        if order == None:
            return {"status": "FAILED", "desc": "Order not found"}
        # end if
        handler = (params.get("shipping_handler") or "").strip().upper()
        if handler not in self.SHIPPING_HANDLERS:
            return {"status": "FAILED", "desc": "Select officer or self-arranged shipping"}
        # end if
        if handler == "SELF":
            return self.save_row("db_order", pkey, {
                "shipping_handler": "SELF",
                "shipping_request_status": "SELF_ARRANGED",
                "shipping_expedition": "",
                "shipping_budget": "",
                "shipping_budget_num": 0,
                "shipping_service_fee": "",
                "shipping_service_fee_num": 0,
                "shipping_tracking_code": "",
                "shipping_tracking_url": ""
            })
        # end if
        expedition = (params.get("shipping_expedition") or "").strip()
        budget_num = self.parse_int(params.get("shipping_budget_num"))
        if budget_num < 0:
            budget_num = 0
        # end if
        shipping_status = (params.get("shipping_request_status") or "REQUESTED").strip().upper()
        if shipping_status not in self.SHIPPING_STATUSES:
            shipping_status = "REQUESTED"
        # end if
        tracking_url = (params.get("shipping_tracking_url") or "").strip()
        if tracking_url != "":
            parsed = urlparse(tracking_url)
            if parsed.scheme not in ["http", "https"] or parsed.netloc == "":
                return {"status": "FAILED", "desc": "Tracking link must be a valid http or https URL"}
            # end if
        # end if
        if shipping_status in ["SHIPPED", "COMPLETED"] and expedition == "":
            return {"status": "FAILED", "desc": "Select an expedition before marking the order as shipped"}
        # end if
        referrer = self.find_order_referrer(order)
        if referrer == None:
            return {"status": "FAILED", "desc": "Officer shipping requires an assigned member referral"}
        # end if
        from dashboard.dashboard_proc import dashboard_proc
        eligibility = dashboard_proc().shipping_eligibility(referrer, order)
        if order.get("shipping_handler") != "OFFICER" and not eligibility.get("eligible"):
            return {
                "status": "FAILED",
                "desc": "Officer shipping requires at least " + eligibility.get("minimum") + " combined progress"
            }
        # end if
        service_fee_value = params.get("shipping_service_fee_num")
        if service_fee_value != None and str(service_fee_value).strip() != "":
            service_fee_num = self.parse_int(service_fee_value)
            if service_fee_num < 0:
                service_fee_num = 0
            # end if
        else:
            service_fee_num = self.configured_shipping_service_fee_num()
            if order.get("shipping_handler") == "OFFICER":
                service_fee_num = self.order_shipping_service_fee_num(order)
            # end if
        # end if
        shipping_updates = {
            "shipping_handler": "OFFICER",
            "shipping_request_status": shipping_status,
            "shipping_expedition": expedition,
            "shipping_budget": self.format_rp(budget_num) if budget_num > 0 else "",
            "shipping_budget_num": budget_num,
            "shipping_service_fee": self.format_rp(service_fee_num) if service_fee_num > 0 else "",
            "shipping_service_fee_num": service_fee_num,
            "shipping_tracking_code": (params.get("shipping_tracking_code") or "").strip(),
            "shipping_tracking_url": tracking_url
        }
        status_map = {
            "PROCESSING": "Processing",
            "SHIPPED": "Shipped",
            "COMPLETED": "Completed"
        }
        order_status = status_map.get(shipping_status)
        if order_status != None:
            items = []
            for line in order.get("items") or []:
                row = dict(line)
                row["line_status"] = order_status
                items.append(row)
            # end for
            shipping_updates["items"] = items
            shipping_updates["order_status"] = order_status
        # end if
        return self.save_row("db_order", pkey, shipping_updates)
    # end def

    def reset_order_shipping(self, pkey):
        if self.get_row("db_order", pkey) == None:
            return {"status": "FAILED", "desc": "Order not found"}
        # end if
        return self.save_row("db_order", pkey, {
            "shipping_handler": "",
            "shipping_recipient_same_buyer": True,
            "shipping_name": "",
            "shipping_phone": "",
            "shipping_address": "",
            "shipping_city": "",
            "shipping_postal_code": "",
            "shipping_package_note": "",
            "shipping_request_status": "NOT_REQUESTED",
            "shipping_expedition": "",
            "shipping_budget": "",
            "shipping_budget_num": 0,
            "shipping_service_fee": "",
            "shipping_service_fee_num": 0,
            "shipping_tracking_code": "",
            "shipping_tracking_url": ""
        })
    # end def

    def order_shipping_eligibility(self, order):
        referrer = self.find_order_referrer(order)
        if referrer == None:
            site = self.site.get_site() or {}
            minimum = self.site.shipping_minimum_num(site)
            service_fee_num = self.configured_shipping_service_fee_num()
            return {
                "available_num": 0,
                "available": "Rp 0",
                "merch_num": 0,
                "merch": "Rp 0",
                "proposal_num": 0,
                "proposal": "Rp 0",
                "self_contribution_num": 0,
                "self_contribution": "Rp 0",
                "spent_num": 0,
                "spent": "Rp 0",
                "minimum_num": minimum,
                "minimum": self.format_rp(minimum),
                "service_fee_num": service_fee_num,
                "service_fee": self.format_rp(service_fee_num),
                "shipping_budget_max_num": 0,
                "shipping_budget_max": "Rp 0",
                "eligible": False
            }
        # end if
        from dashboard.dashboard_proc import dashboard_proc
        payload = dashboard_proc().shipping_eligibility(referrer, order)
        service_fee_num = self.order_shipping_service_fee_num(order)
        if order.get("shipping_handler") != "OFFICER":
            service_fee_num = self.configured_shipping_service_fee_num()
        # end if
        payload["service_fee_num"] = service_fee_num
        payload["service_fee"] = self.format_rp(service_fee_num)
        payload["shipping_budget_max_num"] = max(
            0,
            int(payload.get("available_num") or 0) - service_fee_num
        )
        payload["shipping_budget_max"] = self.format_rp(payload.get("shipping_budget_max_num"))
        return payload
    # end def

    def get_row(self, table, pkey):
        rec = self.mgdDB[table].find_one(
            {"pkey": pkey, "is_deleted": False},
            {"_id": 0}
        )
        return rec
    # end def

    def list_staff_users(self):
        recs = self.list_rows("db_user", {"role": {"$in": self.ADMIN_ROLES}}, sort_field="name", direction=1)
        rows = []
        for rec in recs:
            rec["role_kind"] = self.staff_role(rec.get("role"))
            rec["role_label"] = self.role_label(rec.get("role"))
            rows.append(rec)
        # end for
        return rows
    # end def

    def count_super_admins(self):
        return self.mgdDB.db_user.count_documents({
            "role": "SUPER_ADMIN",
            "is_deleted": False,
            "status": "ENABLE"
        })
    # end def

    def save_staff_user(self, actor, pkey, params, raw_password):
        response = {"status": "FAILED", "desc": "", "pkey": pkey}
        if not self.is_super(actor):
            response["desc"] = "Only a super admin can manage users"
            return response
        # end if
        name = self.unescape_value((params.get("name") or "").strip())
        email = (params.get("email") or "").strip().lower()
        phone = self.unescape_value((params.get("phone") or "").strip())
        role = params.get("role") or "OFFICER"
        status = params.get("status") or "ENABLE"
        if role not in self.STAFF_ROLES:
            role = "OFFICER"
        # end if
        if status not in ["ENABLE", "DISABLE"]:
            status = "ENABLE"
        # end if
        if name == "" or email == "":
            response["desc"] = "Name and email are required"
            return response
        # end if
        dup = self.mgdDB.db_user.find_one({"email": email, "is_deleted": False})
        if dup != None and dup.get("pkey") != pkey:
            if dup.get("role") == "PARTICIPANT":
                response["desc"] = "That email belongs to a participant account"
            else:
                response["desc"] = "That email is already used"
            # end if
            return response
        # end if
        if pkey == "":
            if len(raw_password) < 6:
                response["desc"] = "Password must be at least 6 characters"
                return response
            # end if
            result = self.save_row("db_user", "", {
                "fk_user_id": "",
                "username": email,
                "email": email,
                "name": name,
                "phone": phone,
                "password": generate_password_hash(raw_password),
                "role": role,
                "status": status
            })
            return result
        # end if
        existing = self.get_row("db_user", pkey)
        if existing == None:
            response["desc"] = "User not found"
            return response
        # end if
        if self.staff_role(existing.get("role")) == "":
            response["desc"] = "That account is not staff"
            return response
        # end if
        last_super = existing.get("role") == "SUPER_ADMIN" and existing.get("status") == "ENABLE" and self.count_super_admins() <= 1
        if last_super and (role != "SUPER_ADMIN" or status != "ENABLE"):
            response["desc"] = "Keep at least one active super admin"
            return response
        # end if
        if pkey == actor.get("pkey") and status != "ENABLE":
            response["desc"] = "You cannot disable your own account"
            return response
        # end if
        fields = {
            "username": email,
            "email": email,
            "name": name,
            "phone": phone,
            "role": role,
            "status": status
        }
        if raw_password != "":
            if len(raw_password) < 6:
                response["desc"] = "Password must be at least 6 characters"
                return response
            # end if
            fields["password"] = generate_password_hash(raw_password)
        # end if
        result = self.save_row("db_user", pkey, fields)
        return result
    # end def

    def deactivate_staff_user(self, actor, pkey):
        response = {"status": "FAILED", "desc": ""}
        if not self.is_super(actor):
            response["desc"] = "Only a super admin can manage users"
            return response
        # end if
        if pkey == actor.get("pkey"):
            response["desc"] = "You cannot deactivate your own account"
            return response
        # end if
        existing = self.get_row("db_user", pkey)
        if existing == None:
            response["desc"] = "User not found"
            return response
        # end if
        if existing.get("role") == "SUPER_ADMIN" and existing.get("status") == "ENABLE" and self.count_super_admins() <= 1:
            response["desc"] = "Keep at least one active super admin"
            return response
        # end if
        self.mgdDB.db_user.update_one(
            {"pkey": pkey},
            {"$set": {"status": "DISABLE"}}
        )
        response["status"] = "SUCCESS"
        return response
    # end def

    def unescape_value(self, value):
        if not isinstance(value, str):
            return value
        # end if
        prev = None
        text = value
        while prev != text:
            prev = text
            text = html_lib.unescape(text)
        # end while
        return text
    # end def

    def save_row(self, table, pkey, fields, preserve_html=None):
        response = {"status": "FAILED", "desc": "", "pkey": pkey}
        clean = {}
        keys = self.schema_keys(table)
        html_keys = preserve_html or []
        for key in fields:
            if key in keys:
                if key in html_keys:
                    clean[key] = fields[key]
                else:
                    clean[key] = self.unescape_value(fields[key])
                # end if
            # end if
        # end for
        if pkey == "":
            rec = database.new(self.mgdDB, table)
            for key in clean:
                rec.put(key, clean[key])
            # end for
            rec.insert()
            response["pkey"] = rec.get().get("pkey", "")
            response["status"] = "SUCCESS"
            return response
        # end if
        existing = self.get_row(table, pkey)
        if existing == None:
            response["desc"] = "Record not found"
            return response
        # end if
        self.mgdDB[table].update_one({"pkey": pkey}, {"$set": clean})
        response["status"] = "SUCCESS"
        return response
    # end def

    def soft_delete(self, table, pkey):
        self.mgdDB[table].update_one(
            {"pkey": pkey},
            {"$set": {"is_deleted": True}}
        )
        return {"status": "SUCCESS"}
    # end def

    def release_product_stock(self, pkey, stock_num):
        response = {"status": "FAILED", "desc": "", "released": 0, "stock": 0}
        product = self.get_row("db_product", pkey)
        if product == None:
            response["desc"] = "Product not found"
            return response
        # end if
        try:
            stock = int(stock_num or 0)
        except Exception:
            stock = 0
        # end try
        if stock <= 0:
            response["desc"] = "Stock must be at least 1 when marking stock arrived"
            return response
        # end if
        slug = (product.get("slug") or "").strip()
        availability = "In Stock"
        self.mgdDB.db_product.update_one(
            {"pkey": pkey},
            {"$set": {
                "stock": stock,
                "availability": availability
            }}
        )
        query = {
            "is_deleted": False,
            "order_status": "Preorder",
            "$or": [
                {"items.product_pkey": pkey},
                {"items.slug": slug}
            ]
        }
        if slug == "":
            query = {
                "is_deleted": False,
                "order_status": "Preorder",
                "items.product_pkey": pkey
            }
        # end if
        result = self.mgdDB.db_order.update_many(
            query,
            {"$set": {"order_status": "Ready"}}
        )
        released = int(getattr(result, "modified_count", 0) or 0)
        response["status"] = "SUCCESS"
        response["released"] = released
        response["stock"] = stock
        return response
    # end def

    def debit_referrer_sale(self, order):
        if order == None:
            return
        # end if
        sale = self.order_profit_num(order)
        if sale <= 0:
            return
        # end if
        referrer = None
        rid = (order.get("fk_referrer_id") or "").strip()
        if rid != "":
            referrer = self.get_row("db_participant", rid)
        # end if
        if referrer == None:
            code = (order.get("referral_code") or "").strip().lower()
            if code != "":
                referrer = self.mgdDB.db_participant.find_one(
                    {"referral_code": code, "is_deleted": False},
                    {"_id": 0}
                )
            # end if
        # end if
        if referrer == None:
            return
        # end if
        sold = int(referrer.get("sales_total_num") or 0) - sale
        if sold < 0:
            sold = 0
        # end if
        count = int(referrer.get("sales_count") or 0) - 1
        if count < 0:
            count = 0
        # end if
        self.mgdDB.db_participant.update_one(
            {"pkey": referrer.get("pkey")},
            {"$set": {
                "sales_total_num": sold,
                "sales_total": self.format_rp(sold),
                "sales_count": count
            }}
        )
    # end def

    def order_profit_num(self, order):
        if order == None:
            return 0
        # end if
        if order.get("profit_total_num") != None:
            return int(order.get("profit_total_num") or 0)
        # end if
        total = 0
        has_line = False
        for item in (order.get("items") or []):
            if item.get("line_profit_num") != None:
                total = total + int(item.get("line_profit_num") or 0)
                has_line = True
                continue
            # end if
            slug = (item.get("slug") or "").strip()
            qty = int(item.get("qty") or 1)
            if qty < 1:
                qty = 1
            # end if
            unit = int(item.get("unit_price_num") or 0)
            if unit <= 0:
                line = int(item.get("line_num") or 0)
                if qty > 0:
                    unit = int(line / qty)
                # end if
            # end if
            bahan = 0
            if slug != "":
                product = self.mgdDB.db_product.find_one(
                    {"slug": slug, "is_deleted": False},
                    {"_id": 0, "bahan_baku_num": 1, "price_num": 1}
                )
                if product != None:
                    bahan = int(product.get("bahan_baku_num") or 0)
                    if unit <= 0:
                        unit = int(product.get("price_num") or 0)
                    # end if
                # end if
            # end if
            if bahan < 0:
                bahan = 0
            # end if
            unit_profit = unit - bahan
            if unit_profit < 0:
                unit_profit = 0
            # end if
            total = total + (unit_profit * qty)
            has_line = True
        # end for
        if has_line:
            return total
        # end if
        return int(order.get("subtotal_num") or 0)
    # end def

    def format_signed_rp(self, amount):
        n = int(amount or 0)
        text = self.format_rp(abs(n))
        if n < 0:
            return "−" + text
        # end if
        return text
    # end def

    def order_seller_economics(self, order):
        from dashboard.dashboard_proc import dashboard_proc
        dash = dashboard_proc()
        sale_num = int(order.get("subtotal_num") or 0)
        bahan_num = dash.order_bahan_num(order)
        profit_num = self.order_profit_num(order)
        ship_delivery, ship_fee, ship_total, ship_locked = dash.order_officer_shipping_deduction_display(order)
        discount_num = int(order.get("discount_total_num") or 0)
        cuts_num = bahan_num + ship_total
        net_num = profit_num - ship_total
        return {
            "sale_num": sale_num,
            "sale": self.format_rp(sale_num),
            "bahan_num": bahan_num,
            "bahan": self.format_rp(bahan_num),
            "discount_num": discount_num,
            "discount": self.format_rp(discount_num) if discount_num > 0 else "",
            "profit_num": profit_num,
            "profit": self.format_rp(profit_num),
            "shipping_delivery_num": ship_delivery,
            "shipping_delivery": self.format_rp(ship_delivery),
            "shipping_service_fee_num": ship_fee,
            "shipping_service_fee": self.format_rp(ship_fee),
            "shipping_total_num": ship_total,
            "shipping_total": self.format_rp(ship_total),
            "shipping_locked": ship_locked,
            "shipping_show": ship_total > 0,
            "cuts_num": cuts_num,
            "cuts": self.format_rp(cuts_num),
            "net_seller_num": net_num,
            "net_seller": self.format_signed_rp(net_num)
        }
    # end def

    def delete_order(self, pkey):
        response = {"status": "FAILED", "desc": ""}
        order = self.get_row("db_order", pkey)
        if order == None:
            response["desc"] = "Order not found"
            return response
        # end if
        referrer = self.find_order_referrer(order)
        self.soft_delete("db_order", pkey)
        if referrer != None and (referrer.get("pkey") or "") != "":
            self.sync_participant_money(referrer.get("pkey"))
        # end if
        response["status"] = "SUCCESS"
        return response
    # end def

    def delete_participant(self, pkey):
        response = {"status": "FAILED", "desc": ""}
        part = self.get_row("db_participant", pkey)
        if part == None:
            response["desc"] = "Participant not found"
            return response
        # end if
        self.soft_delete("db_participant", pkey)
        login = self.get_participant_login(part)
        user = login.get("user")
        if user != None and (user.get("role") or "") in ["", "PARTICIPANT"]:
            self.mgdDB.db_user.update_one(
                {"pkey": user.get("pkey")},
                {"$set": {"is_deleted": True, "status": "DISABLE"}}
            )
        # end if
        response["status"] = "SUCCESS"
        return response
    # end def

    def form_indices(self, params, prefix, sample_field):
        head = prefix + "_" + sample_field + "_"
        found = []
        for key in params:
            if key.startswith(head):
                found.append(key[len(head):])
            # end if
        # end for
        def sort_key(item):
            if str(item).isdigit():
                return (0, int(item))
            # end if
            return (1, str(item))
        # end def
        return sorted(set(found), key=sort_key)
    # end def

    def get_program_bundle(self, slug):
        if slug == "":
            return {"schedule": [], "faqs": [], "updates": []}
        # end if
        return {
            "schedule": self.list_rows("db_schedule", {"fk_program_slug": slug}, "order", 1),
            "faqs": self.list_rows("db_faq", {"fk_program_slug": slug}, "order", 1),
            "updates": self.list_rows("db_update", {"fk_program_slug": slug})
        }
    # end def

    def sync_program_schedule(self, slug, params):
        for idx in self.form_indices(params, "sch", "title"):
            pkey = (params.get("sch_pkey_" + idx) or "").strip()
            title = (params.get("sch_title_" + idx) or "").strip()
            if (params.get("sch_del_" + idx) or "") == "1":
                if pkey != "":
                    self.soft_delete("db_schedule", pkey)
                # end if
                continue
            # end if
            if title == "":
                continue
            # end if
            self.save_row("db_schedule", pkey, {
                "fk_program_slug": slug,
                "title": title,
                "time_label": (params.get("sch_time_" + idx) or "").strip(),
                "order": self.parse_int(params.get("sch_order_" + idx)),
                "status": "ENABLE"
            })
        # end for
    # end def

    def sync_program_faqs(self, slug, params):
        for idx in self.form_indices(params, "faq", "q"):
            pkey = (params.get("faq_pkey_" + idx) or "").strip()
            question = (params.get("faq_q_" + idx) or "").strip()
            if (params.get("faq_del_" + idx) or "") == "1":
                if pkey != "":
                    self.soft_delete("db_faq", pkey)
                # end if
                continue
            # end if
            if question == "":
                continue
            # end if
            self.save_row("db_faq", pkey, {
                "fk_program_slug": slug,
                "question": question,
                "answer": (params.get("faq_a_" + idx) or "").strip(),
                "order": self.parse_int(params.get("faq_order_" + idx)),
                "status": "ENABLE"
            })
        # end for
    # end def

    def sync_program_updates(self, slug, params):
        for idx in self.form_indices(params, "upd", "title"):
            pkey = (params.get("upd_pkey_" + idx) or "").strip()
            title = (params.get("upd_title_" + idx) or "").strip()
            if (params.get("upd_del_" + idx) or "") == "1":
                if pkey != "":
                    self.soft_delete("db_update", pkey)
                # end if
                continue
            # end if
            if title == "":
                continue
            # end if
            upd_slug = (params.get("upd_slug_" + idx) or "").strip() or self.slugify(title)
            category = (params.get("upd_category_" + idx) or "").strip() or "Announcements"
            self.save_row("db_update", pkey, {
                "fk_program_slug": slug,
                "title": title,
                "slug": upd_slug,
                "date": (params.get("upd_date_" + idx) or "").strip(),
                "category": category,
                "excerpt": (params.get("upd_excerpt_" + idx) or "").strip(),
                "content": (params.get("upd_content_" + idx) or "").strip(),
                "image": (params.get("upd_image_" + idx) or "").strip(),
                "author": (params.get("upd_author_" + idx) or "").strip() or "FRACO",
                "status": (params.get("upd_status_" + idx) or "").strip() or "DRAFT"
            })
        # end for
    # end def

    def save_program_schedule(self, slug, params, pkey=""):
        title = (params.get("title") or "").strip()
        if slug == "" or title == "":
            return {"status": "FAILED", "desc": "Title is required"}
        # end if
        return self.save_row("db_schedule", pkey, {
            "fk_program_slug": slug,
            "title": title,
            "time_label": (params.get("time_label") or "").strip(),
            "order": self.parse_int(params.get("order")),
            "status": "ENABLE"
        })
    # end def

    def save_program_faq(self, slug, params, pkey=""):
        question = (params.get("question") or "").strip()
        if slug == "" or question == "":
            return {"status": "FAILED", "desc": "Question is required"}
        # end if
        return self.save_row("db_faq", pkey, {
            "fk_program_slug": slug,
            "question": question,
            "answer": (params.get("answer") or "").strip(),
            "order": self.parse_int(params.get("order")),
            "status": "ENABLE"
        })
    # end def

    def save_program_update(self, slug, params, pkey=""):
        title = (params.get("title") or "").strip()
        if slug == "" or title == "":
            return {"status": "FAILED", "desc": "Title is required"}
        # end if
        category = (params.get("category") or "").strip()
        if category not in self.UPDATE_CATEGORIES:
            category = self.UPDATE_CATEGORIES[0]
        # end if
        upd_slug = (params.get("slug") or "").strip() or self.slugify(title)
        return self.save_row("db_update", pkey, {
            "fk_program_slug": slug,
            "title": title,
            "slug": upd_slug,
            "date": (params.get("date") or "").strip(),
            "category": category,
            "excerpt": (params.get("excerpt") or "").strip(),
            "content": (params.get("content") or "").strip(),
            "image": (params.get("image") or "").strip(),
            "author": (params.get("author") or "").strip() or "FRACO",
            "status": (params.get("status") or "").strip() or "DRAFT"
        }, preserve_html=["content"])
    # end def

    def save_program_full(self, pkey, params):
        title = (params.get("title") or "").strip()
        slug = (params.get("slug") or "").strip() or self.slugify(title)
        venue_mode = (params.get("venue_mode") or "OFFLINE").strip().upper()
        if venue_mode not in self.VENUE_MODES:
            venue_mode = "OFFLINE"
        # end if
        result = self.save_row("db_program", pkey, {
            "title": title,
            "slug": slug,
            "description": params.get("description") or "",
            "about": params.get("about") or "",
            "image": params.get("image") or "",
            "venue": params.get("venue") or "",
            "venue_mode": venue_mode,
            "venue_url": params.get("venue_url") or "",
            "cta_label": params.get("cta_label") or "",
            "cta_href": params.get("cta_href") or "",
            "topics": self.parse_list(params.get("topics")),
            "industries": self.parse_list(params.get("industries")),
            "order": self.parse_int(params.get("order")),
            "status": params.get("status") or "DRAFT"
        })
        if result.get("status") != "SUCCESS":
            return result
        # end if
        result["slug"] = slug
        return result
    # end def

    def save_upload(self, file_obj, folder):
        if file_obj == None or file_obj.filename == "":
            return "", ""
        # end if
        name = secure_filename(file_obj.filename)
        ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
        if ext not in self.ALLOWED_EXT:
            return "ERR_TYPE", ""
        # end if
        dest_dir = os.path.join(config.G_UPLOAD_PATH, folder)
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        # end if
        stem = name.rsplit(".", 1)[0] if "." in name else name
        stored = stem + "-" + idgen._get_api_call_id() + "." + ext
        path = os.path.join(dest_dir, stored)
        file_obj.save(path)
        rel = config.G_UPLOAD_URL_PATH + "/" + folder + "/" + stored
        return stored, rel
    # end def

    def is_local_upload_url(self, url):
        path = str(url or "").strip().replace("\\", "/")
        if path == "":
            return False
        # end if
        return path.startswith(config.G_UPLOAD_URL_PATH + "/") or path.startswith("/static/upload/")
    # end def

    def is_remote_http_url(self, url):
        path = str(url or "").strip().lower()
        return path.startswith("http://") or path.startswith("https://")
    # end def

    def guess_image_ext(self, url, content_type=""):
        ctype = (content_type or "").split(";")[0].strip().lower()
        map_ctype = {
            "image/jpeg": "jpg",
            "image/jpg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
            "image/gif": "gif"
        }
        if ctype in map_ctype:
            return map_ctype[ctype]
        # end if
        path = urlparse(url).path or ""
        if "." in path:
            ext = path.rsplit(".", 1)[-1].lower()
            if ext in self.IMAGE_EXT:
                if ext == "jpeg":
                    return "jpg"
                # end if
                return ext
            # end if
        # end if
        return "jpg"
    # end def

    def download_remote_image(self, url, folder="imported"):
        response = {"status": "FAILED", "desc": "", "url": ""}
        src = str(url or "").strip()
        if src == "":
            response["desc"] = "Empty URL"
            return response
        # end if
        if self.is_local_upload_url(src):
            response["status"] = "SUCCESS"
            response["url"] = src
            response["desc"] = "Already local"
            return response
        # end if
        if not self.is_remote_http_url(src):
            response["desc"] = "Not a remote http URL"
            return response
        # end if
        dest_dir = os.path.join(config.G_UPLOAD_PATH, folder)
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        # end if
        digest = hashlib.md5(src.encode("utf-8")).hexdigest()[:20]
        # Reuse existing file with same digest if present
        for ext in self.IMAGE_EXT:
            existing = os.path.join(dest_dir, digest + "." + ext)
            if os.path.isfile(existing):
                response["status"] = "SUCCESS"
                response["url"] = config.G_UPLOAD_URL_PATH + "/" + folder + "/" + digest + "." + ext
                response["desc"] = "Cached"
                return response
            # end if
        # end for
        try:
            req = urllib.request.Request(
                src,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; FRACO-WEB/1.0; +https://fraco.local)",
                    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8"
                }
            )
            last_err = None
            data = None
            ctype = ""
            for _attempt in range(3):
                try:
                    with urllib.request.urlopen(req, timeout=60) as resp:
                        data = resp.read()
                        ctype = resp.headers.get("Content-Type") or ""
                    # end with
                    last_err = None
                    break
                except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as exc:
                    last_err = exc
                # end try
            # end for
            if last_err != None:
                response["desc"] = "Download failed: " + str(last_err)
                return response
            # end if
        except Exception as exc:
            response["desc"] = "Download failed: " + str(exc)
            return response
        # end try
        if data == None or len(data) < 32:
            response["desc"] = "Empty image response"
            return response
        # end if
        ext = self.guess_image_ext(src, ctype)
        if ext not in self.IMAGE_EXT:
            ext = "jpg"
        # end if
        stored = digest + "." + ext
        path = os.path.join(dest_dir, stored)
        with open(path, "wb") as handle:
            handle.write(data)
        # end with
        rel = config.G_UPLOAD_URL_PATH + "/" + folder + "/" + stored
        response["status"] = "SUCCESS"
        response["url"] = rel
        response["desc"] = "Downloaded"
        return response
    # end def

    def localize_url_value(self, url, folder, cache):
        src = str(url or "").strip()
        if src == "":
            return src, False
        # end if
        if src in cache:
            return cache[src], cache[src] != src
        # end if
        result = self.download_remote_image(src, folder)
        if result.get("status") == "SUCCESS" and (result.get("url") or "") != "":
            local = result.get("url")
            cache[src] = local
            return local, local != src
        # end if
        return src, False
    # end def

    def migrate_remote_images(self):
        cache = {}
        stats = {
            "checked": 0,
            "updated": 0,
            "failed": 0,
            "collections": {}
        }
        jobs = [
            {"table": "db_product", "fields": ["image"], "lists": ["images"], "folder": "products"},
            {"table": "db_program", "fields": ["image"], "lists": [], "folder": "programs"},
            {"table": "db_update", "fields": ["image"], "lists": [], "folder": "content"},
            {"table": "db_gallery", "fields": ["image"], "lists": [], "folder": "gallery"},
            {"table": "db_event", "fields": ["image"], "lists": [], "folder": "events"},
            {"table": "db_team", "fields": ["photo", "image"], "lists": [], "folder": "team"}
        ]
        for job in jobs:
            table = job["table"]
            folder = job["folder"]
            updated_here = 0
            recs = list(self.mgdDB[table].find({"is_deleted": False}, {"_id": 0}))
            for rec in recs:
                changes = {}
                for field in job["fields"]:
                    raw = rec.get(field)
                    if not isinstance(raw, str):
                        continue
                    # end if
                    stats["checked"] = stats["checked"] + 1
                    local, changed = self.localize_url_value(raw, folder, cache)
                    if changed:
                        changes[field] = local
                    elif self.is_remote_http_url(raw) and local == raw:
                        stats["failed"] = stats["failed"] + 1
                    # end if
                # end for
                for list_field in job["lists"]:
                    values = rec.get(list_field) or []
                    if not isinstance(values, list) or values == []:
                        continue
                    # end if
                    new_list = []
                    list_changed = False
                    for item in values:
                        if not isinstance(item, str):
                            new_list.append(item)
                            continue
                        # end if
                        stats["checked"] = stats["checked"] + 1
                        local, changed = self.localize_url_value(item, folder, cache)
                        new_list.append(local)
                        if changed:
                            list_changed = True
                        elif self.is_remote_http_url(item) and local == item:
                            stats["failed"] = stats["failed"] + 1
                        # end if
                    # end for
                    if list_changed:
                        changes[list_field] = new_list
                    # end if
                # end for
                # Keep product.image in sync with first gallery image when image empty
                if table == "db_product":
                    images = changes.get("images")
                    if images == None:
                        images = rec.get("images") or []
                    # end if
                    image_val = changes.get("image")
                    if image_val == None:
                        image_val = rec.get("image") or ""
                    # end if
                    if (image_val or "") == "" and isinstance(images, list) and images != []:
                        changes["image"] = images[0]
                    elif isinstance(images, list) and images != [] and changes.get("images") != None:
                        if (image_val or "") != "" and image_val == (rec.get("image") or ""):
                            # if images[0] localized but image field still remote, sync
                            if self.is_remote_http_url(image_val) == False and image_val in images:
                                pass
                            elif self.is_local_upload_url(images[0]) and self.is_remote_http_url(image_val):
                                changes["image"] = images[0]
                            # end if
                        # end if
                    # end if
                # end if
                if changes != {}:
                    self.mgdDB[table].update_one({"pkey": rec.get("pkey")}, {"$set": changes})
                    updated_here = updated_here + 1
                    stats["updated"] = stats["updated"] + 1
                # end if
            # end for
            stats["collections"][table] = updated_here
        # end for
        return stats
    # end def

    def migrate_template_remote_images(self):
        stats = {"checked": 0, "updated_files": 0, "replacements": 0, "failed": 0}
        templates_dir = os.path.join(config.G_HOME_PATH, "templates")
        if not os.path.isdir(templates_dir):
            return stats
        # end if
        pattern = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
        cache = {}
        for name in os.listdir(templates_dir):
            if not name.endswith(".html"):
                continue
            # end if
            path = os.path.join(templates_dir, name)
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    text = handle.read()
                # end with
            except OSError:
                continue
            # end try
            urls = pattern.findall(text)
            if urls == []:
                continue
            # end if
            new_text = text
            file_changed = False
            for url in urls:
                clean = url.rstrip(").,;]")
                lower = clean.lower()
                if not (".jpg" in lower or ".jpeg" in lower or ".png" in lower or ".webp" in lower or ".gif" in lower or "images.unsplash.com" in lower or "/photo-" in lower):
                    continue
                # end if
                stats["checked"] = stats["checked"] + 1
                local, changed = self.localize_url_value(clean, "heroes", cache)
                if changed and local != clean:
                    new_text = new_text.replace(clean, local)
                    file_changed = True
                    stats["replacements"] = stats["replacements"] + 1
                elif self.is_remote_http_url(clean) and local == clean:
                    stats["failed"] = stats["failed"] + 1
                # end if
            # end for
            if file_changed:
                with open(path, "w", encoding="utf-8") as handle:
                    handle.write(new_text)
                # end with
                stats["updated_files"] = stats["updated_files"] + 1
            # end if
        # end for
        return stats
    # end def

    def delete_local_upload(self, url):
        path = str(url or "").strip().replace("\\", "/")
        prefix = config.G_UPLOAD_URL_PATH + "/"
        if path == "" or path.find(prefix) != 0:
            return False
        # end if
        rel = path[len(prefix):].lstrip("/")
        if rel == "" or ".." in rel.split("/"):
            return False
        # end if
        full = os.path.join(config.G_UPLOAD_PATH, *rel.split("/"))
        if os.path.isfile(full):
            try:
                os.remove(full)
                return True
            except OSError:
                return False
            # end try
        # end if
        return False
    # end def

    def delete_program(self, pkey):
        rec = self.get_row("db_program", pkey)
        if rec == None:
            return {"status": "FAILED", "desc": "Not found"}
        # end if
        self.soft_delete("db_program", pkey)
        self.delete_local_upload(rec.get("image"))
        return {"status": "SUCCESS"}
    # end def

    def chart_counts(self, recs, field):
        buckets = {}
        for rec in recs:
            key = rec.get(field) or "Unknown"
            buckets[key] = buckets.get(key, 0) + 1
        # end for
        total = 0
        for key in buckets:
            total = total + buckets[key]
        # end for
        rows = []
        for key in buckets:
            pct = 0
            if total > 0:
                pct = int(round(100.0 * buckets[key] / total))
            # end if
            rows.append({"label": key, "count": buckets[key], "pct": pct})
        # end for
        return rows
    # end def

    def support_money_totals(self):
        proposal = 0
        contribution = 0
        follow_up_count = 0
        received_count = 0
        follow_up_amount = 0
        for item in self.list_rows("db_donor"):
            amount = int(item.get("amount_num") or 0)
            follow = (item.get("follow_status") or "FOLLOW_UP").upper()
            if follow == "RECEIVED":
                received_count = received_count + 1
                if self._is_self_pledge(item):
                    contribution = contribution + amount
                else:
                    proposal = proposal + amount
                # end if
            else:
                follow_up_count = follow_up_count + 1
                follow_up_amount = follow_up_amount + amount
            # end if
        # end for
        return {
            "proposal_num": proposal,
            "proposal": self.format_rp(proposal),
            "contribution_num": contribution,
            "contribution": self.format_rp(contribution),
            "follow_up_count": follow_up_count,
            "follow_up_amount_num": follow_up_amount,
            "follow_up_amount": self.format_rp(follow_up_amount),
            "received_count": received_count
        }
    # end def

    def merch_paid_total(self):
        total = 0
        for rec in self.list_rows("db_order"):
            if rec.get("payment_status") == "Paid":
                total = total + self.order_profit_num(rec)
            # end if
        # end for
        return total
    # end def

    def refresh_participant_money_caches(self):
        for rec in self.list_rows("db_participant", {"member_type": "AHC_MEMBER"}):
            self.sync_participant_money(rec.get("pkey") or "")
        # end for
    # end def

    def sync_donor_referrers(self, donor):
        if donor == None:
            return
        # end if
        seen = []
        rid = (donor.get("fk_referrer_id") or "").strip()
        if rid != "":
            self.sync_participant_money(rid)
            seen.append(rid)
        # end if
        code = (donor.get("referral_code") or "").strip().lower()
        if code != "":
            part = self.mgdDB.db_participant.find_one(
                {"referral_code": code, "is_deleted": False},
                {"_id": 0, "pkey": 1}
            )
            if part != None:
                pk = part.get("pkey") or ""
                if pk != "" and pk not in seen:
                    self.sync_participant_money(pk)
                # end if
            # end if
        # end if
    # end def

    def get_stats(self):
        self.refresh_participant_money_caches()
        parts = self.list_rows("db_participant")
        orders = self.list_rows("db_order")
        payments = self.list_rows("db_payment")
        sponsors = self.list_rows("db_sponsor_app")
        vendors = self.list_rows("db_vendor_app")
        unis = self.list_rows("db_program_reg", {"fk_program_slug": "university-fair"})
        events = self.list_rows("db_event")
        donors = self.list_rows("db_donor")
        support = self.support_money_totals()
        merch = self.merch_paid_total()
        raised = merch + support["proposal_num"] + support["contribution_num"]
        pending_pay = 0
        for rec in payments:
            if rec.get("status") in ["PENDING", "Pending"]:
                pending_pay = pending_pay + 1
            # end if
        # end for
        for rec in orders:
            if rec.get("payment_status") in ["Pending", "Pending Payment"]:
                pending_pay = pending_pay + 1
            # end if
        # end for
        upcoming = 0
        for rec in events:
            st = rec.get("event_status") or ""
            if st not in ["Completed", "Registration Closed"]:
                upcoming = upcoming + 1
            # end if
        # end for
        day_map = {}
        for rec in parts:
            day = (rec.get("rec_timestamp_str") or "")[:10]
            if day == "":
                day = "Unknown"
            # end if
            day_map[day] = day_map.get(day, 0) + 1
        # end for
        days = []
        for key in sorted(day_map.keys()):
            days.append({"label": key, "count": day_map[key], "pct": 0})
        # end for
        max_day = 1
        for row in days:
            if row["count"] > max_day:
                max_day = row["count"]
            # end if
        # end for
        for row in days:
            row["pct"] = int(round(100.0 * row["count"] / max_day))
        # end for
        pledge_chart = []
        for key in self.DONOR_FOLLOW_STATUSES:
            count = 0
            for item in donors:
                if (item.get("follow_status") or "").upper() == key:
                    count = count + 1
                # end if
            # end for
            pledge_chart.append({
                "label": self.DONOR_FOLLOW_LABELS.get(key, key),
                "count": count,
                "pct": 0
            })
        # end for
        pledge_total = len(donors)
        for row in pledge_chart:
            if pledge_total > 0:
                row["pct"] = int(round(100.0 * row["count"] / pledge_total))
            # end if
        # end for
        return {
            "total_participants": len(parts),
            "total_revenue": self.format_rp(raised),
            "total_revenue_num": raised,
            "merch_sold": self.format_rp(merch),
            "merch_sold_num": merch,
            "proposal_total": support["proposal"],
            "proposal_total_num": support["proposal_num"],
            "contribution_total": support["contribution"],
            "contribution_total_num": support["contribution_num"],
            "pledges_follow_up": support["follow_up_count"],
            "pledges_received": support["received_count"],
            "pending_payments": pending_pay,
            "merchandise_orders": len(orders),
            "sponsors": len(sponsors),
            "vendors": len(vendors),
            "universities": len(unis),
            "upcoming_events": upcoming,
            "chart_regs": days,
            "chart_payments": self.chart_counts(payments, "status"),
            "chart_orders": self.chart_counts(orders, "order_status"),
            "chart_pledges": pledge_chart
        }
    # end def

    def get_participant_login(self, part):
        if part == None:
            return {"username": "", "password_hint": "", "user": None, "has_account": False}
        # end if
        user = None
        fk = part.get("fk_user_id") or ""
        if fk != "":
            user = self.mgdDB.db_user.find_one(
                {"pkey": fk, "is_deleted": False},
                {"_id": 0}
            )
        # end if
        if user == None:
            email = (part.get("email") or "").lower()
            if email != "":
                user = self.mgdDB.db_user.find_one(
                    {"email": email, "is_deleted": False, "role": "PARTICIPANT"},
                    {"_id": 0}
                )
            # end if
        # end if
        username = ""
        if user != None:
            username = user.get("username") or user.get("email") or ""
        # end if
        if username == "":
            username = part.get("email") or ""
        # end if
        return {
            "username": username,
            "password_hint": part.get("password_hint") or "",
            "user": user,
            "has_account": user != None
        }
    # end def

    def set_participant_password(self, part, raw_password):
        response = {"status": "FAILED", "desc": ""}
        if part == None:
            response["desc"] = "Participant not found"
            return response
        # end if
        password = raw_password or ""
        if len(password) < 6:
            response["desc"] = "Password must be at least 6 characters"
            return response
        # end if
        login = self.get_participant_login(part)
        user = login.get("user")
        hashed = generate_password_hash(password)
        if user == None:
            email = (part.get("email") or "").lower()
            if email == "":
                response["desc"] = "Participant has no email for a login account"
                return response
            # end if
            rec = database.new(self.mgdDB, "db_user")
            rec.put("fk_user_id", "")
            rec.put("username", email)
            rec.put("password", hashed)
            rec.put("role", "PARTICIPANT")
            rec.put("name", part.get("full_name") or "")
            rec.put("phone", part.get("phone") or "")
            rec.put("email", email)
            rec.put("status", "ENABLE")
            rec.insert()
            user_row = rec.get()
            self.mgdDB.db_participant.update_one(
                {"pkey": part.get("pkey")},
                {"$set": {
                    "fk_user_id": user_row.get("pkey", ""),
                    "password_hint": password
                }}
            )
        else:
            self.mgdDB.db_user.update_one(
                {"pkey": user.get("pkey")},
                {"$set": {"password": hashed}}
            )
            self.mgdDB.db_participant.update_one(
                {"pkey": part.get("pkey")},
                {"$set": {"password_hint": password}}
            )
        # end if
        response["status"] = "SUCCESS"
        return response
    # end def

    def sync_participant_money(self, pkey):
        rec = self.get_row("db_participant", pkey)
        if rec == None:
            return
        # end if
        sold = 0
        count = 0
        for order in self.member_referral_orders(rec):
            status = (order.get("order_status") or "").strip()
            pay = (order.get("payment_status") or "").strip()
            if status == "Cancelled" or pay != "Paid":
                continue
            # end if
            sold = sold + self.order_profit_num(order)
            count = count + 1
        # end for
        proposal, self_amt = self._member_pledge_totals(rec)
        if (rec.get("member_type") or "") == "ALUMNI":
            self.mgdDB.db_participant.update_one(
                {"pkey": pkey},
                {"$set": {
                    "contribution": "Rp 0",
                    "contribution_num": 0,
                    "proposal_total": "Rp 0",
                    "proposal_total_num": 0,
                    "self_contribution": "Rp 0",
                    "self_contribution_num": 0,
                    "sales_total": self.format_rp(sold),
                    "sales_total_num": sold,
                    "sales_count": count
                }}
            )
            return
        # end if
        self.mgdDB.db_participant.update_one(
            {"pkey": pkey},
            {"$set": {
                "sales_total": self.format_rp(sold),
                "sales_total_num": sold,
                "sales_count": count,
                "proposal_total": self.format_rp(proposal),
                "proposal_total_num": proposal,
                "self_contribution": self.format_rp(self_amt),
                "self_contribution_num": self_amt
            }}
        )
    # end def

    def confirm_payment(self, pkey, new_status):
        rec = self.get_row("db_payment", pkey)
        if rec == None:
            return {"status": "FAILED", "desc": "Payment not found"}
        # end if
        self.mgdDB.db_payment.update_one(
            {"pkey": pkey},
            {"$set": {"status": new_status}}
        )
        return {"status": "SUCCESS"}
    # end def
# end class
