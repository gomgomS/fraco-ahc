import sys
import traceback
from flask import Blueprint, redirect

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from view.admin import view_admin

admin_blueprint = Blueprint("admin_blueprint", __name__)

def _wrap(fn):
    try:
        return fn()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def

@admin_blueprint.route("/admin/login", methods=["GET", "POST"])
def login():
    return _wrap(view_admin.html_login)
# end def

@admin_blueprint.route("/admin/logout", methods=["GET"])
def logout():
    return _wrap(view_admin.html_logout)
# end def

@admin_blueprint.route("/admin", methods=["GET"])
def overview():
    return _wrap(view_admin.html_overview)
# end def

@admin_blueprint.route("/admin/participants", methods=["GET", "POST"])
def participants():
    return _wrap(view_admin.html_participants)
# end def

@admin_blueprint.route("/admin/participants/<pkey>", methods=["GET", "POST"])
def participant(pkey):
    try:
        return view_admin.html_participant(pkey)
    except Exception:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def

@admin_blueprint.route("/admin/orders", methods=["GET", "POST"])
def orders():
    return _wrap(view_admin.html_orders)
# end def

@admin_blueprint.route("/admin/orders/print/officer", methods=["GET"])
def officer_shipping_print():
    return _wrap(view_admin.html_officer_shipping_print)
# end def

@admin_blueprint.route("/admin/orders/<pkey>", methods=["GET", "POST"])
def order(pkey):
    try:
        return view_admin.html_order(pkey)
    except Exception:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def

@admin_blueprint.route("/admin/orders/<pkey>/shipping-document", methods=["GET"])
def order_shipping_document(pkey):
    try:
        return view_admin.html_order_shipping_document(pkey)
    except Exception:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def

@admin_blueprint.route("/admin/orders/<pkey>/shipping-document.pdf", methods=["GET"])
def order_shipping_document_pdf(pkey):
    try:
        return view_admin.pdf_order_shipping_document(pkey)
    except Exception:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def

@admin_blueprint.route("/admin/products", methods=["GET", "POST"])
def products():
    return _wrap(view_admin.html_products)
# end def

@admin_blueprint.route("/admin/products/new", methods=["GET", "POST"])
def product_new():
    return _wrap(lambda: view_admin.html_product_form(""))
# end def

@admin_blueprint.route("/admin/products/<pkey>", methods=["GET", "POST"])
def product_edit(pkey):
    try:
        return view_admin.html_product_form(pkey)
    except Exception:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def

@admin_blueprint.route("/admin/programs", methods=["GET"])
def programs():
    return _wrap(view_admin.html_programs)
# end def

@admin_blueprint.route("/admin/programs/new", methods=["GET", "POST"])
def program_new():
    return _wrap(lambda: view_admin.html_program_form(""))
# end def

@admin_blueprint.route("/admin/programs/<pkey>", methods=["GET", "POST"])
def program_edit(pkey):
    try:
        return view_admin.html_program_form(pkey)
    except Exception:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def

@admin_blueprint.route("/admin/programs/<pkey>/schedule", methods=["POST"])
def program_schedule(pkey):
    try:
        return view_admin.html_program_schedule(pkey)
    except Exception:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def

@admin_blueprint.route("/admin/programs/<pkey>/faq", methods=["POST"])
def program_faq(pkey):
    try:
        return view_admin.html_program_faq_action(pkey)
    except Exception:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def

@admin_blueprint.route("/admin/programs/<pkey>/updates", methods=["POST"])
def program_updates(pkey):
    try:
        return view_admin.html_program_update_action(pkey)
    except Exception:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def

@admin_blueprint.route("/admin/events", methods=["GET"])
def events():
    return _wrap(view_admin.html_events)
# end def

@admin_blueprint.route("/admin/events/new", methods=["GET", "POST"])
def event_new():
    return _wrap(lambda: view_admin.html_event_form(""))
# end def

@admin_blueprint.route("/admin/events/<pkey>", methods=["GET", "POST"])
def event_edit(pkey):
    try:
        return view_admin.html_event_form(pkey)
    except Exception:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def

@admin_blueprint.route("/admin/sponsors", methods=["GET"])
def sponsors():
    return _wrap(view_admin.html_sponsors)
# end def

@admin_blueprint.route("/admin/sponsors/packages", methods=["GET", "POST"])
def sponsor_packages():
    return _wrap(view_admin.html_sponsor_packages)
# end def

@admin_blueprint.route("/admin/sponsors/packages/new", methods=["GET", "POST"])
def sponsor_package_new():
    try:
        return view_admin.html_sponsor_package_form("")
    except Exception:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def

@admin_blueprint.route("/admin/sponsors/packages/<pkey>", methods=["GET", "POST"])
def sponsor_package(pkey):
    try:
        return view_admin.html_sponsor_package_form(pkey)
    except Exception:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def

@admin_blueprint.route("/admin/sponsors/<pkey>", methods=["GET", "POST"])
def sponsor(pkey):
    try:
        return view_admin.html_sponsor(pkey)
    except Exception:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def

@admin_blueprint.route("/admin/vendors", methods=["GET", "POST"])
def vendors():
    return _wrap(view_admin.html_vendors)
# end def

@admin_blueprint.route("/admin/vendors/<pkey>", methods=["GET", "POST"])
def vendor(pkey):
    try:
        return view_admin.html_vendor(pkey)
    except Exception:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def

@admin_blueprint.route("/admin/universities", methods=["GET"])
def universities():
    return _wrap(view_admin.html_universities)
# end def

@admin_blueprint.route("/admin/universities/applications", methods=["GET"])
def university_applications():
    return redirect("/admin/universities")
# end def

@admin_blueprint.route("/admin/universities/applications/<pkey>", methods=["GET", "POST"])
def university_application_legacy(pkey):
    return redirect("/admin/universities/" + pkey)
# end def

@admin_blueprint.route("/admin/universities/new", methods=["GET", "POST"])
def university_new():
    return redirect("/admin/universities")
# end def

@admin_blueprint.route("/admin/universities/<pkey>", methods=["GET", "POST"])
def university_edit(pkey):
    try:
        return view_admin.html_university_application(pkey)
    except Exception:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def

@admin_blueprint.route("/admin/payments", methods=["GET", "POST"])
def payments():
    return _wrap(view_admin.html_payments)
# end def

@admin_blueprint.route("/admin/content", methods=["GET"])
def content():
    return _wrap(view_admin.html_content)
# end def

@admin_blueprint.route("/admin/content/new", methods=["GET", "POST"])
def content_new():
    return _wrap(lambda: view_admin.html_content_form(""))
# end def

@admin_blueprint.route("/admin/content/<pkey>", methods=["GET", "POST"])
def content_edit(pkey):
    try:
        return view_admin.html_content_form(pkey)
    except Exception:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def

@admin_blueprint.route("/admin/gallery", methods=["GET", "POST"])
def gallery():
    return _wrap(view_admin.html_gallery)
# end def

@admin_blueprint.route("/admin/team", methods=["GET", "POST"])
def team():
    return _wrap(view_admin.html_team)
# end def

@admin_blueprint.route("/admin/donations", methods=["GET", "POST"])
def donations():
    return _wrap(view_admin.html_donations)
# end def

@admin_blueprint.route("/admin/users", methods=["GET"])
def users():
    return _wrap(view_admin.html_users)
# end def

@admin_blueprint.route("/admin/users/new", methods=["GET", "POST"])
def user_new():
    return _wrap(lambda: view_admin.html_user_form(""))
# end def

@admin_blueprint.route("/admin/users/<pkey>", methods=["GET", "POST"])
def user_edit(pkey):
    try:
        return view_admin.html_user_form(pkey)
    except Exception:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def

@admin_blueprint.route("/admin/settings", methods=["GET", "POST"])
def settings():
    return _wrap(view_admin.html_settings)
# end def
