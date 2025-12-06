from datetime import datetime
from flask_login import UserMixin
from .extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    role = db.Column(db.String(20), nullable=False, default="customer")

    restaurants = db.relationship("Restaurant", backref="owner", lazy=True)
    orders = db.relationship("Order", backref="customer", lazy=True)


class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    cuisine_type = db.Column(db.String(80))
    rating = db.Column(db.Float, default=0.0)
    delivery_time_mins = db.Column(db.Integer, default=30)

    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    menu_items = db.relationship("MenuItem", backref="restaurant", lazy=True)
    orders = db.relationship("Order", backref="restaurant", lazy=True)


class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurant.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(80))
    is_available = db.Column(db.Boolean, default=True)

    order_items = db.relationship("OrderItem", backref="menu_item", lazy=True)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurant.id"), nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    delivery_address = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(30), default="received")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("OrderItem", backref="order", lazy=True)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_item.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False)
