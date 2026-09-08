import sys

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from slapz102_core import database
from slapz102_core import config
from ahc_site.ahc_site_proc import ahc_site_proc
import sanitize

class updates_proc:

    mgdDB = database.get_db_conn(config.mainDB)
    CATEGORIES = [
        "News", "Announcements", "Event Updates",
        "Behind the Scenes", "Throwback", "Community"
    ]
    ALBUMS = [
        "Preparation", "Alumni", "Events", "University Fair",
        "Career Workshop", "Behind The Scenes", "AHC 2027"
    ]

    def __init__(self, app=None):
        self.webapp = app
        self.site = ahc_site_proc(app)
    # end def

    def get_categories(self):
        cats = list(self.CATEGORIES)
        for rec in self.mgdDB.db_update.find(
            {"is_deleted": False, "status": "PUBLISHED"},
            {"_id": 0, "category": 1}
        ):
            name = (rec.get("category") or "").strip()
            if name != "" and name not in cats:
                cats.append(name)
            # end if
        # end for
        return cats
    # end def

    def get_updates(self, category=""):
        query = {"is_deleted": False, "status": "PUBLISHED"}
        if category != "":
            query["category"] = category
        # end if
        recs = list(self.mgdDB.db_update.find(query, {"_id": 0}).sort("rec_timestamp", -1))
        return recs
    # end def

    def get_updates_page(self, category=""):
        active = (category or "").strip()
        return self.site.with_site({
            "updates": self.get_updates(active),
            "categories": self.get_categories(),
            "active_category": active
        })
    # end def

    def get_article(self, slug):
        rec = self.mgdDB.db_update.find_one(
            {"slug": slug, "is_deleted": False},
            {"_id": 0}
        )
        return rec
    # end def

    def get_related(self, article):
        if article == None:
            return []
        # end if
        recs = list(self.mgdDB.db_update.find(
            {
                "is_deleted": False,
                "status": "PUBLISHED",
                "category": article.get("category", ""),
                "slug": {"$ne": article.get("slug", "")}
            },
            {"_id": 0}
        ).limit(3))
        return recs
    # end def

    def get_article_page(self, slug):
        article = self.get_article(slug)
        if article == None:
            return None
        # end if
        paragraphs = []
        raw = article.get("content") or article.get("excerpt") or ""
        content_html = ""
        is_rich_content = "<" in raw and ">" in raw
        if is_rich_content:
            content_html = sanitize.clean_rich_html(raw)
        else:
            for block in raw.split("\n\n"):
                text = block.strip()
                if text != "":
                    paragraphs.append(text)
                # end if
            # end for
        # end if
        return self.site.with_site({
            "article": article,
            "paragraphs": paragraphs,
            "content_html": content_html,
            "is_rich_content": is_rich_content,
            "related": self.get_related(article)
        })
    # end def

    def get_gallery(self, album=""):
        query = {"is_deleted": False}
        if album != "":
            query["album"] = album
        # end if
        recs = list(self.mgdDB.db_gallery.find(query, {"_id": 0}).sort("order", 1))
        return recs
    # end def

    def get_gallery_page(self, album=""):
        return self.site.with_site({
            "gallery": self.get_gallery(album),
            "albums": self.ALBUMS,
            "active_album": album
        })
    # end def
# end class
