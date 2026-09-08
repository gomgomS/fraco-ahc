import sys

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from slapz102_core import database
from slapz102_core import config
from ahc_site.ahc_site_seed import ahc_site_seed

class ahc_site_proc:

    mgdDB = database.get_db_conn(config.mainDB)

    # CMS fields that can switch EN <-> ID (admin Settings). Not for news/events/products.
    LANG_FIELDS = [
        "announcement",
        "tagline",
        "subtitle",
        "description",
        "presented_by"
    ]

    UI = {
        "en": {
            "explore": "Explore FRACO",
            "shop": "Shop Merchandise",
            "about_title": "About FRACO",
            "learn_more": "Learn More",
            "programs_title": "Our Programs",
            "view_all": "View All",
            "merch_title": "Merchandise",
            "shop_all": "Shop All Merchandise",
            "add_cart": "Add to Cart",
            "view": "View",
            "partners_title": "Partners",
            "partners_kicker": "Build it with us",
            "partners_heading": "Let's Build with FRACO",
            "partners_body": "Companies, brands, businesses, and organizations can collaborate with FRACO — class of 2017 — on {event} through sponsorship, vendor services, and university booths.",
            "become_sponsor": "Become a Sponsor",
            "download_proposal": "Download Proposal",
            "updates_title": "Latest Updates",
            "gallery_title": "Gallery"
        },
        "id": {
            "explore": "Jelajahi FRACO",
            "shop": "Belanja Merchandise",
            "about_title": "Tentang FRACO",
            "learn_more": "Selengkapnya",
            "programs_title": "Program Kami",
            "view_all": "Lihat Semua",
            "merch_title": "Merchandise",
            "shop_all": "Belanja Semua Merchandise",
            "add_cart": "Tambah ke Keranjang",
            "view": "Lihat",
            "partners_title": "Mitra",
            "partners_kicker": "Bangun bersama kami",
            "partners_heading": "Mari Bangun bersama FRACO",
            "partners_body": "Perusahaan, merek, bisnis, dan organisasi dapat berkolaborasi dengan FRACO — angkatan 2017 — pada {event} melalui sponsorship, layanan vendor, dan booth universitas.",
            "become_sponsor": "Jadi Sponsor",
            "download_proposal": "Unduh Proposal",
            "updates_title": "Update Terbaru",
            "gallery_title": "Galeri"
        }
    }

    def __init__(self, app=None):
        self.webapp = app
        seeder = ahc_site_seed(app)
        seeder.seed_if_empty()
    # end def

    def get_lang(self):
        lang = "en"
        try:
            from flask import has_request_context, request, session
            if not has_request_context():
                return "en"
            # end if
            q = (request.args.get("lang") or "").strip().lower()
            if q in ["en", "id"]:
                return q
            # end if
            cookie = (request.cookies.get("fraco_lang") or "").strip().lower()
            if cookie in ["en", "id"]:
                return cookie
            # end if
            sess = (session.get("fraco_lang") or "").strip().lower()
            if sess in ["en", "id"]:
                return sess
            # end if
        except Exception:
            lang = "en"
        # end try
        return lang
    # end def

    def get_site(self):
        rec = self.mgdDB.db_site.find_one({"is_deleted": False}, {"_id": 0})
        if rec == None:
            return {}
        # end if
        return rec
    # end def

    def apply_lang(self, site, lang="en"):
        data = dict(site or {})
        if lang == "id":
            for key in self.LANG_FIELDS:
                alt = (data.get(key + "_id") or "").strip()
                if alt != "":
                    data[key] = alt
                # end if
            # end for
        # end if
        data["lang"] = lang
        ui = dict(self.UI.get(lang) or self.UI["en"])
        event = (data.get("event_full_name") or "Alumni Home Coming 2027").strip()
        ui["partners_body"] = ui["partners_body"].replace("{event}", event)
        data["ui"] = ui
        return data
    # end def

    def get_auth_user(self):
        user = None
        try:
            from flask import has_request_context, session
            if not has_request_context():
                return None
            # end if
            pkey = session.get("auth_pkey", "")
            if pkey == "":
                return None
            # end if
            user = self.mgdDB.db_user.find_one(
                {"pkey": pkey, "is_deleted": False, "status": "ENABLE"},
                {"_id": 0, "password": 0}
            )
        except Exception:
            user = None
        # end try
        return user
    # end def

    def with_site(self, extra):
        data = self.apply_lang(self.get_site(), self.get_lang())
        data["cart_count"] = self.get_cart_count()
        data["auth_user"] = self.get_auth_user()
        data.update(extra)
        return data
    # end def

    def get_cart_count(self):
        total = 0
        try:
            from flask import has_request_context, session
            if not has_request_context():
                return 0
            # end if
            sid = session.get("cart_sid", "")
            if sid == "":
                return 0
            # end if
            rows = self.mgdDB.db_cart.find(
                {"session_id": sid, "is_deleted": False},
                {"qty": 1}
            )
            for row in rows:
                total = total + int(row.get("qty", 0))
            # end for
        except Exception:
            total = 0
        # end try
        return total
    # end def
# end class
