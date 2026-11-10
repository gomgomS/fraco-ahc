import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

import html as html_lib
import math
import os
import re
import time
from werkzeug.utils import secure_filename
from slapz102_core import database
from slapz102_core import config
import idgen

class tutorial_proc:

    mgdDB = database.get_db_conn(config.mainDB)
    STATUSES = ["DRAFT", "PUBLISHED"]
    IMAGE_EXT = ["jpg", "jpeg", "png", "webp", "gif"]
    UPLOAD_FOLDER = "tutorials"

    def __init__(self, app=None):
        self.webapp = app
    # end def

    def now_str(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # end def

    def slugify(self, text):
        raw = (text or "").strip().lower()
        slug = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
        return slug or "tutorial"
    # end def

    def unique_slug(self, text, pkey=""):
        base = self.slugify(text)[0:80].strip("-") or "tutorial"
        slug = base
        counter = 2
        while self.mgdDB.db_tutorial.find_one(
            {"slug": slug, "is_deleted": False, "pkey": {"$ne": pkey}},
            {"_id": 0, "pkey": 1}
        ) != None:
            slug = base + "-" + str(counter)
            counter = counter + 1
        # end while
        return slug
    # end def

    def plain_text(self, content_html):
        text = re.sub(r"<[^>]+>", " ", content_html or "")
        text = html_lib.unescape(text)
        return re.sub(r"\s+", " ", text).strip()
    # end def

    def excerpt(self, content_html, limit=180):
        text = self.plain_text(content_html)
        if len(text) <= limit:
            return text
        # end if
        cut = text[0:limit].rsplit(" ", 1)[0]
        return cut + "…"
    # end def

    def first_image(self, content_html):
        match = re.search(r'<img[^>]+src="([^"]+)"', content_html or "")
        if match == None:
            return ""
        # end if
        return html_lib.unescape(match.group(1))
    # end def

    def read_minutes(self, content_html):
        words = len(self.plain_text(content_html).split(" "))
        return max(1, int(math.ceil(words / 200.0)))
    # end def

    def ago(self, stamp):
        stamp = (stamp or "").strip()
        if stamp == "":
            return ""
        # end if
        try:
            then = time.mktime(time.strptime(stamp[0:19], "%Y-%m-%d %H:%M:%S"))
        except Exception:
            return stamp[0:10]
        # end try
        diff = int(time.time() - then)
        if diff < 60:
            return "just now"
        # end if
        if diff < 3600:
            n = diff // 60
            return str(n) + " minute" + ("" if n == 1 else "s") + " ago"
        # end if
        if diff < 86400:
            n = diff // 3600
            return str(n) + " hour" + ("" if n == 1 else "s") + " ago"
        # end if
        if diff < 86400 * 30:
            n = diff // 86400
            return str(n) + " day" + ("" if n == 1 else "s") + " ago"
        # end if
        return stamp[0:10]
    # end def

    def decorate(self, rec):
        rec["edited_ago"] = self.ago(rec.get("updated_str") or rec.get("rec_timestamp_str"))
        rec["published_ago"] = self.ago(rec.get("published_str"))
        return rec
    # end def

    def counts(self):
        counts = {"DRAFT": 0, "PUBLISHED": 0}
        rows = self.mgdDB.db_tutorial.aggregate([
            {"$match": {"is_deleted": False}},
            {"$group": {"_id": "$status", "n": {"$sum": 1}}}
        ])
        for row in rows:
            key = row.get("_id") or "DRAFT"
            if key in counts:
                counts[key] = int(row.get("n") or 0)
            # end if
        # end for
        return counts
    # end def

    def list_tutorials(self, status="DRAFT"):
        if status not in self.STATUSES:
            status = "DRAFT"
        # end if
        recs = list(self.mgdDB.db_tutorial.find(
            {"is_deleted": False, "status": status},
            {"_id": 0, "content": 0}
        ).sort("updated_str", -1))
        return [self.decorate(rec) for rec in recs]
    # end def

    def get_tutorial(self, pkey):
        rec = self.mgdDB.db_tutorial.find_one(
            {"pkey": pkey, "is_deleted": False},
            {"_id": 0}
        )
        if rec == None:
            return None
        # end if
        return self.decorate(rec)
    # end def

    def save_tutorial(self, pkey, title, content_html, status, admin=None, slug=""):
        response = {"status": "FAILED", "desc": "", "pkey": pkey, "slug": "", "slug_adjusted": False}
        title = (title or "").strip()
        if title == "":
            response["desc"] = "Add a title before saving."
            return response
        # end if
        if status not in self.STATUSES:
            status = "DRAFT"
        # end if
        existing = None
        if pkey != "":
            existing = self.get_tutorial(pkey)
            if existing == None:
                response["desc"] = "Tutorial not found"
                return response
            # end if
        # end if
        # Keep the saved slug when none is typed, so editing the title never breaks a shared link.
        wanted = (slug or "").strip() or ((existing or {}).get("slug") or "") or title
        final_slug = self.unique_slug(wanted, pkey)
        response["slug"] = final_slug
        response["slug_adjusted"] = (slug or "").strip() != "" and final_slug != self.slugify(slug)[0:80].strip("-")
        now = self.now_str()
        fields = {
            "title": title[0:200],
            "slug": final_slug,
            "content": content_html or "",
            "excerpt": self.excerpt(content_html),
            "cover_image": self.first_image(content_html),
            "read_minutes": self.read_minutes(content_html),
            "updated_str": now,
            "status": status
        }
        if pkey == "":
            rec = database.new(self.mgdDB, "db_tutorial")
            for key in fields:
                rec.put(key, fields[key])
            # end for
            rec.put("author_name", (admin or {}).get("name") or (admin or {}).get("email") or "")
            rec.put("fk_author_id", (admin or {}).get("pkey") or "")
            if status == "PUBLISHED":
                rec.put("published_str", now)
            # end if
            rec.insert()
            response["pkey"] = rec.get().get("pkey", "")
            response["status"] = "SUCCESS"
            return response
        # end if
        if status == "PUBLISHED" and (existing.get("published_str") or "") == "":
            fields["published_str"] = now
        # end if
        self.mgdDB.db_tutorial.update_one({"pkey": pkey}, {"$set": fields})
        response["status"] = "SUCCESS"
        return response
    # end def

    def list_published(self):
        recs = list(self.mgdDB.db_tutorial.find(
            {"is_deleted": False, "status": "PUBLISHED"},
            {"_id": 0, "content": 0}
        ).sort("published_str", -1))
        for rec in recs:
            rec["published_date"] = (rec.get("published_str") or rec.get("rec_timestamp_str") or "")[0:10]
        # end for
        return recs
    # end def

    def get_published(self, slug):
        rec = self.mgdDB.db_tutorial.find_one(
            {"slug": (slug or "").strip().lower(), "is_deleted": False, "status": "PUBLISHED"},
            {"_id": 0}
        )
        if rec == None:
            return None
        # end if
        rec["published_date"] = (rec.get("published_str") or rec.get("rec_timestamp_str") or "")[0:10]
        return rec
    # end def

    def delete_tutorial(self, pkey):
        self.mgdDB.db_tutorial.update_one(
            {"pkey": pkey},
            {"$set": {"is_deleted": True}}
        )
        return {"status": "SUCCESS"}
    # end def

    def save_image(self, file_obj):
        response = {"status": "FAILED", "desc": "", "url": ""}
        if file_obj == None or file_obj.filename == "":
            response["desc"] = "Choose an image to upload"
            return response
        # end if
        name = secure_filename(file_obj.filename)
        ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
        if ext not in self.IMAGE_EXT:
            response["desc"] = "Images must be jpg, png, webp, or gif"
            return response
        # end if
        dest_dir = os.path.join(config.G_UPLOAD_PATH, self.UPLOAD_FOLDER)
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        # end if
        stem = name.rsplit(".", 1)[0] or "image"
        stored = stem[0:60] + "-" + idgen._get_api_call_id() + "." + ext
        file_obj.save(os.path.join(dest_dir, stored))
        response["status"] = "SUCCESS"
        response["url"] = config.G_UPLOAD_URL_PATH + "/" + self.UPLOAD_FOLDER + "/" + stored
        return response
    # end def
# end class
