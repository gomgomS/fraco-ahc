import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from flask import Flask
from slapz102_core import config

app = Flask(__name__)
app.secret_key = config.G_FLASK_SECRET

from home.home_blueprint import home_blueprint
from about.about_blueprint import about_blueprint
from programs.programs_blueprint import programs_blueprint
from merchandise.merchandise_blueprint import merchandise_blueprint
from partners.partners_blueprint import partners_blueprint
from participate.participate_blueprint import participate_blueprint
from dashboard.dashboard_blueprint import dashboard_blueprint
from admin.admin_blueprint import admin_blueprint
from updates.updates_blueprint import updates_blueprint
from cart.cart_blueprint import cart_blueprint
from support.support_blueprint import support_blueprint

app.register_blueprint(home_blueprint, url_prefix="/")
app.register_blueprint(about_blueprint, url_prefix="/")
app.register_blueprint(programs_blueprint, url_prefix="/")
app.register_blueprint(merchandise_blueprint, url_prefix="/")
app.register_blueprint(partners_blueprint, url_prefix="/")
app.register_blueprint(participate_blueprint, url_prefix="/")
app.register_blueprint(dashboard_blueprint, url_prefix="/")
app.register_blueprint(admin_blueprint, url_prefix="/")
app.register_blueprint(updates_blueprint, url_prefix="/")
app.register_blueprint(cart_blueprint, url_prefix="/")
app.register_blueprint(support_blueprint, url_prefix="/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)
# end if
