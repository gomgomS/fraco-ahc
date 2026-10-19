import sys
import traceback
import re
import requests
from flask import Blueprint, jsonify

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

address_blueprint = Blueprint("address_blueprint", __name__)
WILAYAH_BASE = "https://www.emsifa.com/api-wilayah-indonesia/v2"

def _safe_region_id(value):
    text = str(value or "").strip()
    if re.match(r"^[0-9]{2}(\.[0-9]{2}){0,3}(\.[0-9]{4})?$", text) == None:
        return ""
    # end if
    return text
# end def

def _proxy(path):
    url = WILAYAH_BASE + "/" + path
    try:
        resp = requests.get(url, timeout=8)
        if resp.status_code != 200:
            return jsonify({"data": [], "meta": {"error": "upstream"}}), 502
        # end if
        return jsonify(resp.json()), 200
    except Exception:
        print(traceback.format_exc())
        return jsonify({"data": [], "meta": {"error": "unavailable"}}), 502
    # end try
# end def

@address_blueprint.route("/api/wilayah/provinces.json", methods=["GET"])
def wilayah_provinces():
    return _proxy("provinces.json")
# end def

@address_blueprint.route("/api/wilayah/regencies/<province_id>.json", methods=["GET"])
def wilayah_regencies(province_id):
    clean = _safe_region_id(province_id)
    if clean == "":
        return jsonify({"data": []}), 400
    # end if
    return _proxy("regencies/" + clean + ".json")
# end def

@address_blueprint.route("/api/wilayah/districts/<regency_id>.json", methods=["GET"])
def wilayah_districts(regency_id):
    clean = _safe_region_id(regency_id)
    if clean == "":
        return jsonify({"data": []}), 400
    # end if
    return _proxy("districts/" + clean + ".json")
# end def

@address_blueprint.route("/api/wilayah/villages/<district_id>.json", methods=["GET"])
def wilayah_villages(district_id):
    clean = _safe_region_id(district_id)
    if clean == "":
        return jsonify({"data": []}), 400
    # end if
    return _proxy("villages/" + clean + ".json")
# end def
