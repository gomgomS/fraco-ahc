import os
import sys

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from werkzeug.utils import secure_filename
from slapz102_core import database
from slapz102_core import config
from ahc_site.ahc_site_proc import ahc_site_proc
import idgen

class partners_proc:

    mgdDB = database.get_db_conn(config.mainDB)
    ALLOWED_EXT = ["pdf", "doc", "docx", "jpg", "jpeg", "png"]
    MAX_BYTES = 3 * 1024 * 1024

    def __init__(self, app=None):
        self.webapp = app
        self.site = ahc_site_proc(app)
    # end def

    def get_packages(self):
        recs = list(self.mgdDB.db_sponsor_package.find(
            {"is_deleted": False},
            {"_id": 0}
        ).sort("order", 1))
        out = []
        for item in recs:
            status = (item.get("status") or "ENABLE").strip().upper()
            if status == "ENABLE":
                out.append(item)
            # end if
        # end for
        return out
    # end def

    def get_vendor_categories(self):
        recs = list(self.mgdDB.db_vendor_category.find(
            {"is_deleted": False},
            {"_id": 0}
        ).sort("order", 1))
        return recs
    # end def

    def get_partners_page(self):
        return self.site.with_site({
            "packages": self.get_packages(),
            "vendor_categories": self.get_vendor_categories()
        })
    # end def

    def get_sponsorship_page(self):
        return self.get_partners_page()
    # end def

    def get_vendors_page(self):
        return self.get_partners_page()
    # end def

    def get_apply_page(self, kind, error="", ok=False):
        return self.site.with_site({
            "kind": kind,
            "packages": self.get_packages(),
            "vendor_categories": self.get_vendor_categories(),
            "form_error": error,
            "form_ok": ok
        })
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
        file_obj.seek(0, os.SEEK_END)
        size = file_obj.tell()
        file_obj.seek(0)
        if size > self.MAX_BYTES:
            return "ERR_SIZE", ""
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

    def save_sponsor(self, params, file_obj):
        response = {"status": "FAILED", "desc": ""}
        company = (params.get("company_name") or "").strip()
        person = (params.get("contact_person") or "").strip()
        email = (params.get("email") or "").strip()
        phone = (params.get("phone") or "").strip()
        if company == "" or person == "" or email == "" or phone == "":
            response["desc"] = "Company, contact, email, and phone are required"
            return response
        # end if
        file_name, file_path = self.save_upload(file_obj, "sponsors")
        if file_name == "ERR_TYPE":
            response["desc"] = "Attachment must be PDF, Word, or an image"
            return response
        # end if
        if file_name == "ERR_SIZE":
            response["desc"] = "Attachment must be under 3 MB"
            return response
        # end if
        rec = database.new(self.mgdDB, "db_sponsor_app")
        rec.put("company_name", company)
        rec.put("contact_person", person)
        rec.put("email", email)
        rec.put("phone", phone)
        rec.put("website", (params.get("website") or "").strip())
        rec.put("industry", (params.get("industry") or "").strip())
        rec.put("package_slug", (params.get("package_slug") or "").strip())
        rec.put("collaboration", (params.get("collaboration") or "").strip())
        rec.put("message", (params.get("message") or "").strip())
        rec.put("file_name", file_name)
        rec.put("file_path", file_path)
        rec.put("status", "PENDING")
        rec.insert()
        response["status"] = "SUCCESS"
        return response
    # end def

    def save_vendor(self, params, file_obj):
        response = {"status": "FAILED", "desc": ""}
        business = (params.get("business_name") or "").strip()
        person = (params.get("contact_person") or "").strip()
        email = (params.get("email") or "").strip()
        phone = (params.get("phone") or "").strip()
        if business == "" or person == "" or email == "" or phone == "":
            response["desc"] = "Business name, contact, email, and phone are required"
            return response
        # end if
        file_name, file_path = self.save_upload(file_obj, "vendors")
        if file_name == "ERR_TYPE":
            response["desc"] = "Attachment must be PDF, Word, or an image"
            return response
        # end if
        if file_name == "ERR_SIZE":
            response["desc"] = "Attachment must be under 3 MB"
            return response
        # end if
        rec = database.new(self.mgdDB, "db_vendor_app")
        rec.put("business_name", business)
        rec.put("contact_person", person)
        rec.put("email", email)
        rec.put("phone", phone)
        rec.put("category", (params.get("category") or "").strip())
        rec.put("services", (params.get("services") or "").strip())
        rec.put("profile", (params.get("profile") or "").strip())
        rec.put("portfolio", (params.get("portfolio") or "").strip())
        rec.put("pricing", (params.get("pricing") or "").strip())
        rec.put("notes", (params.get("notes") or "").strip())
        rec.put("file_name", file_name)
        rec.put("file_path", file_path)
        rec.put("status", "PENDING")
        rec.insert()
        response["status"] = "SUCCESS"
        return response
    # end def
# end class
