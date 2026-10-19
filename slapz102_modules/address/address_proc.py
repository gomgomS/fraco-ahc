import sys
import re

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

class address_proc:

    PART_KEYS = [
        "province_id",
        "province",
        "city_id",
        "city",
        "district_id",
        "district",
        "village_id",
        "village",
        "street",
        "address_detail",
        "postal_code"
    ]

    def __init__(self, app=None):
        self.webapp = app
    # end def

    def collect(self, params, prefix=""):
        fields = {}
        for key in self.PART_KEYS:
            fields[key] = (params.get(prefix + key) or "").strip()
        # end for
        fields["address"] = self.compose(fields)
        return fields
    # end def

    def from_record(self, rec, prefix=""):
        rec = rec or {}
        fields = {}
        for key in self.PART_KEYS:
            fields[key] = (rec.get(prefix + key) or "").strip()
        # end for
        fields["address"] = (rec.get(prefix + "address") or "").strip()
        if fields.get("address") == "":
            fields["address"] = self.compose(fields)
        # end if
        return fields
    # end def

    def prefixed(self, fields, prefix=""):
        out = {}
        for key in self.PART_KEYS + ["address"]:
            out[prefix + key] = fields.get(key) or ""
        # end for
        return out
    # end def

    def compose(self, fields):
        fields = fields or {}
        lines = []
        street = (fields.get("street") or "").strip()
        detail = (fields.get("address_detail") or "").strip()
        village = (fields.get("village") or "").strip()
        district = (fields.get("district") or "").strip()
        city = (fields.get("city") or "").strip()
        province = (fields.get("province") or "").strip()
        postal = (fields.get("postal_code") or "").strip()
        if street != "":
            lines.append(street)
        # end if
        if detail != "":
            lines.append(detail)
        # end if
        area = []
        if village != "":
            area.append(village)
        # end if
        if district != "":
            area.append(district)
        # end if
        if city != "":
            area.append(city)
        # end if
        if province != "":
            area.append(province)
        # end if
        area_text = ", ".join(area)
        if postal != "":
            if area_text != "":
                area_text = area_text + " " + postal
            else:
                area_text = postal
            # end if
        # end if
        if area_text != "":
            lines.append(area_text)
        # end if
        if lines == []:
            return (fields.get("address") or "").strip()
        # end if
        return "\n".join(lines)
    # end def

    def validate(self, fields):
        fields = fields or {}
        if (fields.get("street") or "").strip() == "":
            return {"status": "FAILED", "desc": "Nama jalan, gedung, dan nomor rumah wajib diisi", "field": "street"}
        # end if
        if (fields.get("province_id") or "").strip() == "" or (fields.get("province") or "").strip() == "":
            return {"status": "FAILED", "desc": "Pilih provinsi", "field": "province"}
        # end if
        if (fields.get("city_id") or "").strip() == "" or (fields.get("city") or "").strip() == "":
            return {"status": "FAILED", "desc": "Pilih kabupaten / kota", "field": "city"}
        # end if
        if (fields.get("district_id") or "").strip() == "" or (fields.get("district") or "").strip() == "":
            return {"status": "FAILED", "desc": "Pilih kecamatan", "field": "district"}
        # end if
        if (fields.get("village_id") or "").strip() == "" or (fields.get("village") or "").strip() == "":
            return {"status": "FAILED", "desc": "Pilih kelurahan / desa", "field": "village"}
        # end if
        return {"status": "SUCCESS", "desc": ""}
    # end def

    def display_rows(self, rec, prefix=""):
        fields = self.from_record(rec, prefix)
        rows = [
            ("Nama jalan / gedung / no.", fields.get("street") or ""),
            ("Detail lainnya", fields.get("address_detail") or ""),
            ("Kelurahan / desa", fields.get("village") or ""),
            ("Kecamatan", fields.get("district") or ""),
            ("Kabupaten / kota", fields.get("city") or ""),
            ("Provinsi", fields.get("province") or ""),
            ("Kode pos", fields.get("postal_code") or "")
        ]
        shown = []
        for label, value in rows:
            if (value or "").strip() != "":
                shown.append({"label": label, "value": value})
            # end if
        # end for
        if shown == [] and (fields.get("address") or "") != "":
            shown.append({"label": "Alamat", "value": fields.get("address")})
        # end if
        return shown
    # end def

    def lines(self, rec, prefix=""):
        fields = self.from_record(rec, prefix)
        text = fields.get("address") or self.compose(fields)
        if text == "":
            return []
        # end if
        return [line for line in re.split(r"[\r\n]+", text) if line.strip() != ""]
    # end def
# end class
