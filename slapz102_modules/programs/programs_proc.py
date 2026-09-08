import sys

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from slapz102_core import database
from slapz102_core import config
from ahc_site.ahc_site_proc import ahc_site_proc

class programs_proc:

    mgdDB = database.get_db_conn(config.mainDB)

    def __init__(self, app=None):
        self.webapp = app
        self.site = ahc_site_proc(app)
    # end def

    def get_programs(self):
        recs = list(self.mgdDB.db_program.find(
            {"is_deleted": False, "status": {"$ne": "DRAFT"}},
            {"_id": 0}
        ).sort("order", 1))
        return recs
    # end def

    def get_programs_page(self):
        return self.site.with_site({
            "programs": self.get_programs()
        })
    # end def

    def get_program(self, slug):
        rec = self.mgdDB.db_program.find_one(
            {"slug": slug, "is_deleted": False},
            {"_id": 0}
        )
        return rec
    # end def

    def get_faqs(self, slug):
        recs = list(self.mgdDB.db_faq.find(
            {"fk_program_slug": slug, "is_deleted": False},
            {"_id": 0}
        ).sort("order", 1))
        return recs
    # end def

    def get_schedule(self, slug):
        recs = list(self.mgdDB.db_schedule.find(
            {"fk_program_slug": slug, "is_deleted": False},
            {"_id": 0}
        ).sort("order", 1))
        return recs
    # end def

    def get_updates(self, slug):
        recs = list(self.mgdDB.db_update.find(
            {
                "fk_program_slug": slug,
                "is_deleted": False,
                "status": "PUBLISHED"
            },
            {"_id": 0}
        ).sort("rec_timestamp", -1))
        return recs
    # end def

    def get_universities(self):
        # Participant campuses = University Fair applications marked show_campus
        recs = list(self.mgdDB.db_program_reg.find(
            {
                "is_deleted": False,
                "fk_program_slug": "university-fair",
                "show_campus": {"$in": [True, "1", "YES", "true", "on"]}
            },
            {"_id": 0}
        ).sort("organization", 1))
        out = []
        for item in recs:
            name = (item.get("organization") or item.get("full_name") or "").strip()
            if name == "":
                continue
            # end if
            out.append({
                "name": name,
                "booth": (item.get("booth") or "").strip(),
                "description": (item.get("notes") or "").strip(),
                "logo": (item.get("logo") or "").strip(),
                "city": (item.get("city") or "").strip()
            })
        # end for
        return out
    # end def

    def get_speakers(self):
        recs = list(self.mgdDB.db_speaker.find(
            {"is_deleted": False},
            {"_id": 0}
        ))
        return recs
    # end def

    def get_activities(self):
        recs = list(self.mgdDB.db_activity.find(
            {"is_deleted": False},
            {"_id": 0}
        ))
        return recs
    # end def

    def get_events(self):
        recs = list(self.mgdDB.db_event.find(
            {"is_deleted": False},
            {"_id": 0}
        ))
        return recs
    # end def

    def get_program_page(self, slug):
        program = self.get_program(slug)
        if program == None:
            return None
        # end if
        extra = {
            "program": program,
            "faqs": self.get_faqs(slug),
            "schedule": self.get_schedule(slug),
            "updates": self.get_updates(slug),
            "universities": [],
            "speakers": [],
            "activities": [],
            "events": [],
            "form_ok": False,
            "form_error": ""
        }
        if slug == "university-fair":
            extra["universities"] = self.get_universities()
        # end if
        if slug == "career-workshop":
            extra["speakers"] = self.get_speakers()
        # end if
        if slug == "spiritual-affairs":
            extra["activities"] = self.get_activities()
        # end if
        if slug == "events":
            extra["events"] = self.get_events()
        # end if
        return self.site.with_site(extra)
    # end def

    def get_register_page(self, slug):
        data = self.get_program_page(slug)
        return data
    # end def

    def save_registration(self, slug, params):
        response = {
            "status": "FAILED",
            "desc": ""
        }
        program = self.get_program(slug)
        if program == None:
            response["desc"] = "Program not found"
            return response
        # end if
        full_name = (params.get("full_name") or "").strip()
        email = (params.get("email") or "").strip()
        phone = (params.get("phone") or "").strip()
        organization = (params.get("organization") or "").strip()
        if full_name == "" or email == "" or phone == "":
            response["desc"] = "Name, email, and phone are required"
            return response
        # end if
        rec = database.new(self.mgdDB, "db_program_reg")
        rec.put("fk_program_slug", slug)
        rec.put("full_name", full_name)
        rec.put("email", email)
        rec.put("phone", phone)
        rec.put("organization", organization)
        rec.put("city", (params.get("city") or "").strip())
        rec.put("notes", (params.get("notes") or "").strip())
        rec.put("booth", "")
        rec.put("logo", "")
        rec.put("show_campus", False)
        rec.put("status", "PENDING")
        rec.insert()
        response["status"] = "SUCCESS"
        response["desc"] = "Registration received"
        return response
    # end def
# end class
