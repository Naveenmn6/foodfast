from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_required, current_user

from .models import Restaurant, MenuItem, Order, OrderItem
from .extensions import db


customer_bp = Blueprint("customer", __name__)


@customer_bp.route("/restaurants")
def list_restaurants():
    q = request.args.get("q", "").strip()
    query = Restaurant.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            (Restaurant.name.ilike(like)) | (Restaurant.cuisine_type.ilike(like))
        )
    restaurants = query.all()
    return render_template("customer/restaurants.html", restaurants=restaurants, q=q)


@customer_bp.route("/restaurants/<int:restaurant_id>")
def restaurant_detail(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    items = MenuItem.query.filter_by(restaurant_id=restaurant.id, is_available=True).all()
    return render_template("customer/restaurant_detail.html", restaurant=restaurant, items=items)


@customer_bp.route("/cart/add", methods=["POST"])
def add_to_cart():
    restaurant_id = int(request.form.get("restaurant_id"))
    item_id = int(request.form.get("item_id"))
    quantity = int(request.form.get("quantity", 1))

    cart = session.get("cart", {})

    # enforce single-restaurant cart
    cart_restaurant = cart.get("restaurant_id")
    if cart_restaurant and cart_restaurant != restaurant_id:
        flash("Cart cleared because you switched restaurants", "info")
        cart = {}

    items = cart.get("items", {})
    items[str(item_id)] = items.get(str(item_id), 0) + quantity

    cart["restaurant_id"] = restaurant_id
    cart["items"] = items
    session["cart"] = cart

    flash("Item added to cart", "success")
    return redirect(url_for("customer.restaurant_detail", restaurant_id=restaurant_id))


@customer_bp.route("/cart")
def view_cart():
    cart = session.get("cart", {})
    if not cart:
        return render_template("customer/cart.html", cart_items=[], restaurant=None, total=0)

    restaurant = Restaurant.query.get(cart.get("restaurant_id"))
    items_map = cart.get("items", {})

    cart_items = []
    total = 0
    for item_id_str, qty in items_map.items():
        item = MenuItem.query.get(int(item_id_str))
        if not item:
            continue
        subtotal = item.price * qty
        total += subtotal
        cart_items.append({"item": item, "quantity": qty, "subtotal": subtotal})

    return render_template("customer/cart.html", cart_items=cart_items, restaurant=restaurant, total=total)


@customer_bp.route("/checkout", methods=["POST"])
@login_required
def checkout():
    cart = session.get("cart", {})
    if not cart:
        flash("Cart is empty", "danger")
        return redirect(url_for("customer.list_restaurants"))

    restaurant = Restaurant.query.get(cart.get("restaurant_id"))
    if not restaurant:
        flash("Restaurant not found", "danger")
        return redirect(url_for("customer.list_restaurants"))

    items_map = cart.get("items", {})

    total = 0
    order = Order(
        customer_id=current_user.id,
        restaurant_id=restaurant.id,
        delivery_address=current_user.address,
        total_cost=0,
    )
    db.session.add(order)

    for item_id_str, qty in items_map.items():
        item = MenuItem.query.get(int(item_id_str))
        if not item:
            continue
        subtotal = item.price * qty
        total += subtotal
        order_item = OrderItem(
            order=order,
            menu_item=item,
            quantity=qty,
            unit_price=item.price,
        )
        db.session.add(order_item)

    order.total_cost = total
    db.session.commit()

    session.pop("cart", None)
    return render_template("customer/order_confirmation.html", order=order)
