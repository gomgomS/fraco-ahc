import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from admin.admin_proc import admin_proc

proc = admin_proc()
for rec in list(proc.mgdDB.db_product.find({"is_deleted": False}, {"_id": 0})):
    images = rec.get("images") or []
    if not isinstance(images, list):
        continue
    # end if
    new_list = []
    changed = False
    for item in images:
        if isinstance(item, str) and item.startswith("http"):
            result = proc.download_remote_image(item, "products")
            print(rec.get("name"), "->", result)
            if result.get("status") == "SUCCESS":
                new_list.append(result.get("url"))
                changed = True
            else:
                new_list.append(item)
            # end if
        else:
            new_list.append(item)
        # end if
    # end for
    if changed:
        update = {"images": new_list}
        image = rec.get("image") or ""
        if image == "" or str(image).startswith("http"):
            update["image"] = new_list[0]
        # end if
        proc.mgdDB.db_product.update_one({"pkey": rec.get("pkey")}, {"$set": update})
        print("saved", rec.get("name"), update)
    # end if
# end for

for rec in proc.mgdDB.db_product.find({"is_deleted": False}, {"_id": 0, "name": 1, "image": 1, "images": 1}):
    print("CHECK", rec.get("name"), rec.get("image"), rec.get("images"))
# end for
