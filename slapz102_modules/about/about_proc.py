import sys

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from slapz102_core import database
from slapz102_core import config
from ahc_site.ahc_site_proc import ahc_site_proc

class about_proc:

    mgdDB = database.get_db_conn(config.mainDB)

    def __init__(self, app=None):
        self.webapp = app
        self.site = ahc_site_proc(app)
    # end def

    def get_timeline(self):
        recs = list(self.mgdDB.db_timeline.find(
            {"is_deleted": False},
            {"_id": 0}
        ).sort("order", 1))
        return recs
    # end def

    def get_divisions(self):
        recs = list(self.mgdDB.db_division.find(
            {"is_deleted": False},
            {"_id": 0}
        ).sort("order", 1))
        return recs
    # end def

    def get_programs(self):
        recs = list(self.mgdDB.db_program.find(
            {"is_deleted": False},
            {"_id": 0}
        ))
        return recs
    # end def

    def get_about(self):
        return self.site.with_site({
            "timeline": self.get_timeline(),
            "divisions": self.get_divisions(),
            "programs": self.get_programs()
        })
    # end def
# end class
