import os
import re
import sys

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from admin.admin_proc import admin_proc
from slapz102_core import config

proc = admin_proc()
print("migrate", proc.migrate_remote_images())
print("templates", proc.migrate_template_remote_images())

heroes_dir = os.path.join(config.G_UPLOAD_PATH, "heroes")
products_dir = os.path.join(config.G_UPLOAD_PATH, "products")
fallback = ""
if os.path.isdir(heroes_dir):
    names = [n for n in os.listdir(heroes_dir) if n.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
    if names:
        fallback = "/static/upload/heroes/" + names[0]
    # end if
# end if
if fallback == "" and os.path.isdir(products_dir):
    names = [n for n in os.listdir(products_dir) if n.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
    if names:
        fallback = "/static/upload/products/" + names[0]
    # end if
# end if
print("fallback", fallback)

if fallback != "":
    for table in ["db_product", "db_program", "db_update", "db_gallery", "db_event"]:
        for rec in proc.mgdDB[table].find({"is_deleted": False}, {"_id": 0}):
            changes = {}
            image = rec.get("image")
            if isinstance(image, str) and image.startswith("http"):
                changes["image"] = fallback
            # end if
            images = rec.get("images")
            if isinstance(images, list) and images != []:
                new_list = []
                changed = False
                for item in images:
                    if isinstance(item, str) and item.startswith("http"):
                        local = proc.download_remote_image(item, "products")
                        if local.get("status") == "SUCCESS":
                            new_list.append(local.get("url"))
                        else:
                            new_list.append(fallback)
                        # end if
                        changed = True
                    else:
                        new_list.append(item)
                    # end if
                # end for
                if changed:
                    changes["images"] = new_list
                    if (changes.get("image") or rec.get("image") or "") == "" or str(rec.get("image") or "").startswith("http"):
                        changes["image"] = new_list[0]
                    # end if
                # end if
            # end if
            if changes != {}:
                proc.mgdDB[table].update_one({"pkey": rec.get("pkey")}, {"$set": changes})
                print("updated", table, rec.get("name") or rec.get("title") or rec.get("pkey"), changes.keys())
            # end if
        # end for
    # end for

    broken_photo = "photo-1529156069898-49953e654ee0"
    broken_uni = "photo-1523050854058-8cb90180b9ae"
    for name in os.listdir("templates"):
        if not name.endswith(".html"):
            continue
        # end if
        path = os.path.join("templates", name)
        with open(path, "r", encoding="utf-8") as handle:
            text = handle.read()
        # end with
        new_text = text
        if broken_photo in new_text or broken_uni in new_text:
            new_text = re.sub(
                r"https://images\.unsplash\.com/photo-1529156069898-49953e654ee0[^\"']*",
                fallback,
                new_text
            )
            new_text = re.sub(
                r"https://images\.unsplash\.com/photo-1523050854058-8cb90180b9ae[^\"']*",
                fallback,
                new_text
            )
        # end if
        if new_text != text:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(new_text)
            # end with
            print("template fixed", name)
        # end if
    # end for
# end if

print("done")
