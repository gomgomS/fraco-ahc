import sys

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from slapz102_core import database
from slapz102_core import config
from ahc_site.ahc_site_proc import ahc_site_proc
from merchandise.merchandise_proc import merchandise_proc
from programs.programs_proc import programs_proc
from updates.updates_proc import updates_proc

class home_proc:

    mgdDB = database.get_db_conn(config.mainDB)

    def __init__(self, app=None):
        self.webapp = app
        self.site = ahc_site_proc(app)
        self.merch = merchandise_proc(app)
        self.programs = programs_proc(app)
        self.updates = updates_proc(app)
    # end def

    def get_gallery(self):
        recs = list(self.mgdDB.db_gallery.find(
            {"is_deleted": False},
            {"_id": 0}
        ).sort("order", 1))
        return recs
    # end def

    def get_home(self):
        return self.site.with_site({
            "products": self.merch.get_products(),
            "programs": self.programs.get_programs(),
            "updates": self.updates.get_updates()[:3],
            "gallery": self.get_gallery()
        })
    # end def
# end class
