import sys
import re

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from slapz102_core import database
from slapz102_core import config
from ahc_site.ahc_site_proc import ahc_site_proc
from urllib.parse import urlparse

class merchandise_proc:

    mgdDB = database.get_db_conn(config.mainDB)

    # Default size measurement table (cm). Admin can override per product.
    SIZE_TABLE = {
        "DEWASA": {
            "XS": [41, 62],
            "S": [44, 65],
            "M": [47, 68],
            "L": [50, 71],
            "XL": [53, 73],
            "2XL": [56, 76],
            "3XL": [59, 79],
            "4XL": [67, 79],
            "5XL": [72, 82]
        },
        "ANAK": {
            "0": [28, 37],
            "1": [32, 43],
            "2": [35, 49],
            "3": [38, 55]
        }
    }
    SIZE_ALIASES = {
        "XXL": "2XL",
        "XXXL": "3XL",
        "XXXXL": "4XL",
        "XXXXXL": "5XL",
        "2X": "2XL",
        "3X": "3XL",
        "4X": "4XL",
        "5X": "5XL"
    }
    DEFAULT_CATEGORIES = ["Apparel", "Accessories", "Member Kit", "Other"]

    def __init__(self, app=None):
        self.webapp = app
        self.site = ahc_site_proc(app)
    # end def

    def get_products(self, category="", query=""):
        filt = {"is_deleted": False, "status": {"$nin": ["DRAFT", "ARCHIVED", "Draft", "Archived"]}}
        if category != "" and category != "All Products":
            filt["category"] = category
        # end if
        recs = list(self.mgdDB.db_product.find(filt, {"_id": 0}))
        if query != "":
            q = query.lower()
            filtered = []
            for item in recs:
                blob = (item.get("name", "") + " " + item.get("category", "")).lower()
                if q in blob:
                    filtered.append(item)
                # end if
            # end for
            recs = filtered
        # end if
        for item in recs:
            self.decorate_product(item)
        # end for
        return recs
    # end def

    def get_categories(self):
        recs = list(self.mgdDB.db_merchandise_category.find(
            {"is_deleted": False, "status": "ENABLE"},
            {"_id": 0, "name": 1}
        ).sort("order", 1))
        names = []
        for rec in recs:
            name = (rec.get("name") or "").strip()
            if name != "" and name not in names:
                names.append(name)
            # end if
        # end for
        if names == []:
            names = list(self.DEFAULT_CATEGORIES)
        # end if
        return ["All Products"] + names
    # end def

    def get_product(self, slug):
        rec = self.mgdDB.db_product.find_one(
            {"slug": slug, "is_deleted": False},
            {"_id": 0}
        )
        return rec
    # end def

    def _truthy(self, value):
        return value == True or value in ["YES", "1", "true", "on", "True"]
    # end def

    def stock_by_size_map(self, product):
        if product == None:
            return {}
        # end if
        raw = product.get("stock_by_size") or {}
        if not isinstance(raw, dict):
            return {}
        # end if
        out = {}
        for key in raw:
            try:
                n = int(raw.get(key) or 0)
            except Exception:
                n = 0
            # end try
            if n < 0:
                n = 0
            # end if
            out[str(key)] = n
        # end for
        return out
    # end def

    def price_by_size_map(self, product):
        if product == None:
            return {}
        # end if
        raw = product.get("price_by_size") or {}
        if not isinstance(raw, dict):
            return {}
        # end if
        out = {}
        for key in raw:
            try:
                n = int(raw.get(key) or 0)
            except Exception:
                n = 0
            # end try
            if n > 0:
                out[str(key)] = n
            # end if
        # end for
        return out
    # end def

    def price_num_for_size(self, product, size=""):
        # Size price override falls back to the standard price when not set or 0.
        if product == None:
            return 0
        # end if
        base = int(product.get("price_num") or 0)
        size_key = (size or "").strip()
        if size_key == "":
            return base
        # end if
        by_size = self.price_by_size_map(product)
        if by_size == {}:
            return base
        # end if
        if size_key in by_size:
            return by_size.get(size_key)
        # end if
        for key in by_size:
            if str(key).strip().lower() == size_key.lower():
                return by_size.get(key)
            # end if
        # end for
        return base
    # end def

    def _normalize_size_key(self, size):
        key = re.sub(r"\s+", "", str(size or "")).upper()
        return self.SIZE_ALIASES.get(key, key)
    # end def

    def size_spec_default(self, size):
        # Lookup in the default measurement table; returns None when unknown
        key = self._normalize_size_key(size)
        for cat in ["DEWASA", "ANAK"]:
            for tbl_key, dims in self.SIZE_TABLE.get(cat, {}).items():
                if self._normalize_size_key(tbl_key) == key:
                    return {"cat": cat, "lebar": int(dims[0]), "panjang": int(dims[1])}
                # end if
            # end for
        # end for
        return None
    # end def

    def size_specs_stored(self, product):
        raw = (product or {}).get("size_specs") or {}
        if not isinstance(raw, dict):
            return {}
        # end if
        out = {}
        for key, val in raw.items():
            if not isinstance(val, dict):
                continue
            # end if
            cat = str(val.get("cat") or "").strip().upper()
            if cat not in ["DEWASA", "ANAK"]:
                cat = ""
            # end if
            try:
                lebar = int(val.get("lebar") or 0)
            except Exception:
                lebar = 0
            # end try
            try:
                panjang = int(val.get("panjang") or 0)
            except Exception:
                panjang = 0
            # end try
            if lebar < 0:
                lebar = 0
            # end if
            if panjang < 0:
                panjang = 0
            # end if
            out[str(key)] = {"cat": cat, "lebar": lebar, "panjang": panjang}
        # end for
        return out
    # end def

    def size_specs_resolved(self, product):
        # Stored specs win; sizes without stored specs fall back to the default
        # table so old products get measurements without being re-saved.
        if product == None:
            return {}
        # end if
        stored = self.size_specs_stored(product)
        out = {}
        for sz in product.get("sizes") or []:
            spec = dict(stored.get(sz) or {})
            fallback = self.size_spec_default(sz)
            if fallback != None:
                if spec.get("cat", "") == "":
                    spec["cat"] = fallback["cat"]
                # end if
                if int(spec.get("lebar") or 0) <= 0:
                    spec["lebar"] = fallback["lebar"]
                # end if
                if int(spec.get("panjang") or 0) <= 0:
                    spec["panjang"] = fallback["panjang"]
                # end if
            # end if
            if spec.get("cat", "") != "" or int(spec.get("lebar") or 0) > 0 or int(spec.get("panjang") or 0) > 0:
                out[sz] = spec
            # end if
        # end for
        return out
    # end def

    def stock_num(self, product, size=""):
        if product == None:
            return 0
        # end if
        size_key = (size or "").strip()
        by_size = self.stock_by_size_map(product)
        if size_key != "" and by_size != {}:
            if size_key in by_size:
                return int(by_size.get(size_key) or 0)
            # end if
            for key in by_size:
                if str(key).strip().lower() == size_key.lower():
                    return int(by_size.get(key) or 0)
                # end if
            # end for
            return 0
        # end if
        if by_size != {}:
            total = 0
            for key in by_size:
                total = total + int(by_size.get(key) or 0)
            # end for
            return total
        # end if
        n = int(product.get("stock") or 0)
        if n < 0:
            return 0
        # end if
        return n
    # end def

    def allows_preorder(self, product):
        if product == None:
            return False
        # end if
        if self._truthy(product.get("allow_preorder")):
            return True
        # end if
        # Legacy: older products used is_preorder as the allow flag
        if self._truthy(product.get("is_preorder")):
            return True
        # end if
        avail = (product.get("availability") or "").strip().lower()
        if avail in ["preorder", "pre-order"]:
            return True
        # end if
        return False
    # end def

    def is_in_stock(self, product, size=""):
        return self.stock_num(product, size) > 0
    # end def

    def is_preorder(self, product, size=""):
        # True when THIS SALE is a preorder: out of stock but preorder allowed
        if product == None:
            return False
        # end if
        if self.is_in_stock(product, size):
            return False
        # end if
        return self.allows_preorder(product)
    # end def

    def stock_label(self, product, size=""):
        if self.is_in_stock(product, size):
            return "In stock"
        # end if
        if self.allows_preorder(product):
            return "Out of stock · Preorder open"
        # end if
        return "Out of stock"
    # end def

    def can_buy(self, product, size=""):
        if product == None:
            return False
        # end if
        if product.get("category") == "Member Kit":
            return False
        # end if
        if int(product.get("price_num", 0)) <= 0:
            return False
        # end if
        size_key = (size or "").strip()
        sizes = product.get("sizes") or []
        if size_key == "" and sizes != []:
            for sz in sizes:
                if self.is_in_stock(product, sz) or self.allows_preorder(product):
                    return True
                # end if
            # end for
            return False
        # end if
        if self.is_in_stock(product, size_key):
            return True
        # end if
        if self.allows_preorder(product):
            return True
        # end if
        return False
    # end def

    def buy_limit(self, product, size=""):
        if product == None:
            return 0
        # end if
        stock = self.stock_num(product, size)
        if stock > 0:
            return stock
        # end if
        if self.allows_preorder(product):
            return 99
        # end if
        return 0
    # end def

    def size_stock_rows(self, product):
        rows = []
        sizes = product.get("sizes") or []
        by_size = self.stock_by_size_map(product)
        prices_by_size = self.price_by_size_map(product)
        specs_by_size = self.size_specs_resolved(product)
        base_price = int(product.get("price_num") or 0)
        shared = False
        if by_size == {} and sizes != []:
            shared = True
        # end if
        for sz in sizes:
            if shared:
                qty = int(product.get("stock") or 0)
                if qty < 0:
                    qty = 0
                # end if
            else:
                qty = 0
                if sz in by_size:
                    qty = int(by_size.get(sz) or 0)
                else:
                    for key in by_size:
                        if str(key).strip().lower() == str(sz).strip().lower():
                            qty = int(by_size.get(key) or 0)
                            break
                        # end if
                    # end for
                # end if
            # end if
            price_num = base_price
            if sz in prices_by_size:
                price_num = prices_by_size.get(sz)
            else:
                for key in prices_by_size:
                    if str(key).strip().lower() == str(sz).strip().lower():
                        price_num = prices_by_size.get(key)
                        break
                    # end if
                # end for
            # end if
            spec = specs_by_size.get(sz) or {}
            rows.append({
                "size": sz,
                "stock": qty,
                "shared": shared,
                "available": qty > 0 or self.allows_preorder(product),
                "is_preorder": qty <= 0 and self.allows_preorder(product),
                "buy_limit": self.buy_limit(product, "" if shared else sz),
                "price_num": price_num,
                "price_label": self.format_rp(price_num),
                "has_price_override": price_num != base_price,
                "lebar": int(spec.get("lebar") or 0),
                "panjang": int(spec.get("panjang") or 0),
                "cat": spec.get("cat") or "",
                "is_kids": (spec.get("cat") or "").upper() == "ANAK"
            })
        # end for
        return rows
    # end def

    def decorate_product(self, product):
        if product == None:
            return None
        # end if
        by_size = self.stock_by_size_map(product)
        product["stock_by_size"] = by_size
        product["size_stock_rows"] = self.size_stock_rows(product)
        product["size_specs"] = self.size_specs_resolved(product)
        product["size_guide_rows"] = [
            row for row in product["size_stock_rows"]
            if int(row.get("lebar") or 0) > 0 or int(row.get("panjang") or 0) > 0
        ]
        product["allows_preorder"] = self.allows_preorder(product)
        product["is_preorder"] = self.is_preorder(product)
        product["is_in_stock"] = self.is_in_stock(product)
        product["stock_label"] = self.stock_label(product)
        product["can_buy"] = self.can_buy(product)
        product["buy_limit"] = self.buy_limit(product)
        # Availability is admin free text; translate the known seeded values for display
        ui = self.site.UI.get(self.site.get_lang()) or self.site.UI["en"]
        avail_map = {
            "In Stock": ui.get("badge_in_stock_cap"),
            "Out of Stock": ui.get("badge_out_stock_cap"),
            "Preorder": ui.get("badge_preorder")
        }
        raw_avail = (product.get("availability") or "").strip()
        product["availability_label"] = avail_map.get(raw_avail) or raw_avail
        # Keep total stock in sync for display when map exists
        if by_size != {}:
            product["stock"] = self.stock_num(product)
        # end if
        return product
    # end def

    def format_rp(self, amount):
        n = int(amount or 0)
        if n <= 0:
            return "Rp 0"
        # end if
        return "Rp " + "{:,}".format(n).replace(",", ".")
    # end def

    def social_buyer_name(self, full_name):
        parts = [part for part in (full_name or "").strip().split(" ") if part != ""]
        if parts == []:
            return "FRACO supporter"
        # end if
        return " ".join(parts)
    # end def

    def get_merchandise_social_proof(self):
        orders = list(self.mgdDB.db_order.find(
            {
                "is_deleted": False,
                "payment_status": "Paid",
                "order_status": {"$ne": "Cancelled"}
            },
            {
                "_id": 0,
                "full_name": 1,
                "total": 1,
                "total_num": 1,
                "items": 1,
                "rec_timestamp": 1
            }
        ).sort("rec_timestamp", -1))
        total_num = 0
        buyers = set()
        ticker = []
        for order in orders:
            total_num = total_num + int(order.get("total_num") or 0)
            buyer_key = (order.get("full_name") or "").strip().lower()
            if buyer_key != "":
                buyers.add(buyer_key)
            # end if
            if len(ticker) < 16:
                product_labels = []
                for item in order.get("items") or []:
                    product_name = item.get("name") or item.get("product_name") or "Merchandise"
                    qty = int(item.get("qty") or 0)
                    product_label = product_name
                    if qty > 1:
                        product_label = product_label + " ×" + str(qty)
                    # end if
                    product_labels.append(product_label)
                # end for
                ticker.append({
                    "name": self.social_buyer_name(order.get("full_name")),
                    "products": ", ".join(product_labels) if product_labels != [] else "Merchandise",
                    "amount": order.get("total") or self.format_rp(order.get("total_num"))
                })
            # end if
        # end for
        return {
            "buyer_count": len(buyers),
            "order_count": len(orders),
            "total": self.format_rp(total_num),
            "ticker": ticker
        }
    # end def

    def get_order_tracking(self, transaction_code):
        code = (transaction_code or "").strip().upper()[0:80]
        if code == "":
            return None
        # end if
        order = self.mgdDB.db_order.find_one(
            {"order_id": code, "is_deleted": False},
            {"_id": 0}
        )
        if order == None:
            return None
        # end if
        ui = self.site.UI.get(self.site.get_lang()) or self.site.UI["en"]
        status_map = {
            "Pending Payment": ui.get("status_pending_payment"),
            "Pending": ui.get("status_pending"),
            "Paid": ui.get("status_paid"),
            "Ready": ui.get("status_ready"),
            "Processing": ui.get("status_processing"),
            "Shipped": ui.get("status_shipped"),
            "Completed": ui.get("status_completed"),
            "Cancelled": ui.get("status_cancelled"),
            "Preorder": ui.get("status_preorder")
        }
        item_rows = []
        for item in order.get("items") or []:
            label = item.get("name") or item.get("product_name") or "Merchandise"
            variant = []
            if (item.get("size") or "").strip() != "":
                variant.append(item.get("size"))
            # end if
            if (item.get("color") or "").strip() != "":
                variant.append(item.get("color"))
            # end if
            item_rows.append({
                "name": label,
                "qty": int(item.get("qty") or 0),
                "variant": " · ".join(variant),
                "status": status_map.get(item.get("line_status")) or status_map.get(order.get("order_status")) or item.get("line_status") or order.get("order_status") or "Pending"
            })
        # end for
        order_status = (order.get("order_status") or "Pending Payment").strip()
        payment_status = (order.get("payment_status") or "Pending").strip()
        rank = 1
        if payment_status == "Paid":
            rank = 2
        # end if
        rank_by_status = {
            "Paid": 2,
            "Ready": 3,
            "Processing": 3,
            "Shipped": 4,
            "Completed": 5
        }
        if rank_by_status.get(order_status, 0) > rank:
            rank = rank_by_status.get(order_status)
        # end if
        step_labels = [
            ui.get("track_step_placed") or "Order placed",
            ui.get("track_step_payment") or "Payment confirmed",
            ui.get("track_step_preparing") or "Preparing merchandise",
            ui.get("track_step_shipped") or "Shipped",
            ui.get("track_step_completed") or "Completed"
        ]
        steps = []
        for index, label in enumerate(step_labels):
            step_no = index + 1
            steps.append({
                "label": label,
                "done": order_status != "Cancelled" and step_no <= rank,
                "active": order_status != "Cancelled" and step_no == rank and rank < 5
            })
        # end for
        shipping_status = ui.get("track_not_shipped") or "Not shipped yet"
        if order_status == "Shipped":
            shipping_status = status_map.get("Shipped")
        elif order_status == "Completed":
            shipping_status = status_map.get("Completed")
        elif order_status == "Cancelled":
            shipping_status = status_map.get("Cancelled")
        # end if
        tracking_url = (order.get("shipping_tracking_url") or "").strip()
        if tracking_url != "":
            parsed_url = urlparse(tracking_url)
            if parsed_url.scheme not in ["http", "https"] or parsed_url.netloc == "":
                tracking_url = ""
            # end if
        # end if
        return {
            "transaction_code": order.get("order_id") or code,
            "date": order.get("rec_timestamp_str") or "",
            "payment_status": status_map.get(payment_status) or payment_status,
            "is_paid": payment_status == "Paid",
            "order_status": status_map.get(order_status) or order_status,
            "shipping_status": shipping_status,
            "shipping_info": order.get("shipping") or (ui.get("track_confirmed_after") or "Confirmed after order"),
            "shipping_expedition": order.get("shipping_expedition") or "",
            "shipping_tracking_code": order.get("shipping_tracking_code") or "",
            "shipping_tracking_url": tracking_url,
            "total": order.get("total") or "Rp 0",
            "has_preorder": order.get("has_preorder") == True,
            "preorder_eta": order.get("preorder_eta") or "",
            "items": item_rows,
            "steps": steps,
            "is_cancelled": order_status == "Cancelled"
        }
    # end def

    def get_merchandise_page(self, category="", query="", track_code=""):
        products = self.get_products(category, query)
        for item in products:
            self.decorate_product(item)
        # end for
        tracking_code = (track_code or "").strip().upper()[0:80]
        return self.site.with_site({
            "products": products,
            "categories": self.get_categories(),
            "active_category": category if category != "" else "All Products",
            "query": query,
            "tracking_code": tracking_code,
            "tracking_checked": tracking_code != "",
            "tracking": self.get_order_tracking(tracking_code),
            "social_proof": self.get_merchandise_social_proof()
        })
    # end def

    def get_product_page(self, slug):
        product = self.get_product(slug)
        if product == None:
            return None
        # end if
        self.decorate_product(product)
        gallery = product.get("images") or []
        if gallery == []:
            gallery = [product.get("image", "")]
        # end if
        related = []
        for item in self.get_products(product.get("category", "")):
            if item.get("slug") != slug:
                self.decorate_product(item)
                related.append(item)
            # end if
        # end for
        return self.site.with_site({
            "product": product,
            "gallery": gallery,
            "can_buy": product.get("can_buy"),
            "is_preorder": product.get("is_preorder"),
            "is_in_stock": product.get("is_in_stock"),
            "allows_preorder": product.get("allows_preorder"),
            "buy_limit": product.get("buy_limit"),
            "related": related[:4]
        })
    # end def
# end class
