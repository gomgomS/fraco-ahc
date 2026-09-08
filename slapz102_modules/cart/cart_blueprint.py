import sys
import traceback
from flask import Blueprint

sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from view.cart import view_cart

cart_blueprint = Blueprint("cart_blueprint", __name__)

@cart_blueprint.route("/cart", methods=["GET"])
def cart():
    try:
        return view_cart.html_cart()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@cart_blueprint.route("/cart/add", methods=["POST"])
def cart_add():
    try:
        return view_cart.html_add()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@cart_blueprint.route("/cart/update", methods=["POST"])
def cart_update():
    try:
        return view_cart.html_update()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@cart_blueprint.route("/cart/remove", methods=["POST"])
def cart_remove():
    try:
        return view_cart.html_remove()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@cart_blueprint.route("/checkout", methods=["GET", "POST"])
def checkout():
    try:
        return view_cart.html_checkout()
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def

@cart_blueprint.route("/order/<order_id>", methods=["GET"])
def order_detail(order_id):
    try:
        return view_cart.html_order(order_id)
    except Exception as e:
        print(traceback.format_exc())
        return "An error occurred", 500
# end def
