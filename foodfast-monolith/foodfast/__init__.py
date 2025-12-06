from flask import Flask, redirect, url_for
from .extensions import db, migrate, login_manager
from .routes_auth import auth_bp
from .routes_customer import customer_bp
from .routes_restaurant import restaurant_bp
from .routes_admin import admin_bp
from .models import User, Restaurant, MenuItem
import os


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(app.root_path, 'foodfast.db')}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(restaurant_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()
        # seed some demo data if no restaurants exist
        if Restaurant.query.count() == 0:
            # 1) Indian restaurant
            spicy_bites = Restaurant(
                name="Spicy Bites",
                cuisine_type="Indian",
                rating=4.5,
                delivery_time_mins=30,
            )
            db.session.add(spicy_bites)
            db.session.flush()

            # 2) Pizza place
            urban_pizza = Restaurant(
                name="Urban Pizza Co.",
                cuisine_type="Italian, Pizza",
                rating=4.3,
                delivery_time_mins=35,
            )
            db.session.add(urban_pizza)
            db.session.flush()

            # 3) Burger joint
            burger_station = Restaurant(
                name="Burger Station",
                cuisine_type="Burgers, Fast Food",
                rating=4.2,
                delivery_time_mins=25,
            )
            db.session.add(burger_station)
            db.session.flush()

            # 4) Desserts & beverages
            sweet_corner = Restaurant(
                name="Sweet Corner",
                cuisine_type="Desserts, Beverages",
                rating=4.6,
                delivery_time_mins=20,
            )
            db.session.add(sweet_corner)
            db.session.flush()

            db.session.add_all([
                # Spicy Bites menu
                MenuItem(
                    restaurant_id=spicy_bites.id,
                    name="Paneer Butter Masala",
                    description="Creamy tomato gravy with cottage cheese",
                    price=220.0,
                    category="Main Course",
                ),
                MenuItem(
                    restaurant_id=spicy_bites.id,
                    name="Butter Naan",
                    description="Soft tandoori naan with butter glaze",
                    price=55.0,
                    category="Bread",
                ),
                MenuItem(
                    restaurant_id=spicy_bites.id,
                    name="Veg Biryani",
                    description="Aromatic basmati rice with mixed vegetables",
                    price=200.0,
                    category="Rice",
                ),
                # Urban Pizza Co. menu
                MenuItem(
                    restaurant_id=urban_pizza.id,
                    name="Margherita Pizza",
                    description="Classic cheese & tomato pizza",
                    price=299.0,
                    category="Pizza",
                ),
                MenuItem(
                    restaurant_id=urban_pizza.id,
                    name="Farmhouse Pizza",
                    description="Loaded with veggies and mozzarella",
                    price=349.0,
                    category="Pizza",
                ),
                MenuItem(
                    restaurant_id=urban_pizza.id,
                    name="Garlic Breadsticks",
                    description="Oven-baked breadsticks with garlic and herbs",
                    price=149.0,
                    category="Sides",
                ),
                # Burger Station menu
                MenuItem(
                    restaurant_id=burger_station.id,
                    name="Classic Veg Burger",
                    description="Crispy veg patty with lettuce and cheese",
                    price=149.0,
                    category="Burger",
                ),
                MenuItem(
                    restaurant_id=burger_station.id,
                    name="Double Cheese Burger",
                    description="Double patty, double cheese, maximum flavor",
                    price=199.0,
                    category="Burger",
                ),
                MenuItem(
                    restaurant_id=burger_station.id,
                    name="French Fries",
                    description="Crispy golden fries with seasoning",
                    price=99.0,
                    category="Sides",
                ),
                # Sweet Corner menu
                MenuItem(
                    restaurant_id=sweet_corner.id,
                    name="Gulab Jamun",
                    description="Soft milk dumplings in sugar syrup",
                    price=120.0,
                    category="Dessert",
                ),
                MenuItem(
                    restaurant_id=sweet_corner.id,
                    name="Chocolate Brownie",
                    description="Warm brownie with chocolate sauce",
                    price=150.0,
                    category="Dessert",
                ),
                MenuItem(
                    restaurant_id=sweet_corner.id,
                    name="Cold Coffee",
                    description="Chilled coffee with ice cream",
                    price=130.0,
                    category="Beverage",
                ),
            ])
            db.session.commit()

        # ensure the first restaurant has at least 10 menu items (for existing DBs)
        first_restaurant = Restaurant.query.first()
        if first_restaurant:
            existing_items = MenuItem.query.filter_by(restaurant_id=first_restaurant.id).count()
            if existing_items < 10:
                extra_items = [
                    ("Cheese Garlic Naan", "Naan topped with cheese and garlic", 75.0, "Bread"),
                    ("Tandoori Roti", "Whole wheat roti from tandoor", 35.0, "Bread"),
                    ("Dal Tadka", "Yellow lentils tempered with ghee and spices", 180.0, "Main Course"),
                    ("Chicken Tikka Masala", "Grilled chicken in creamy tomato gravy", 260.0, "Main Course"),
                    ("Masala Papad", "Crispy papad topped with onions and tomatoes", 70.0, "Starter"),
                    ("Jeera Rice", "Steamed rice tempered with cumin seeds", 150.0, "Rice"),
                    ("Veg Manchurian", "Fried veg balls in Indo-Chinese gravy", 210.0, "Starter"),
                    ("Lassi (Sweet)", "Traditional sweet yogurt drink", 90.0, "Beverage"),
                    ("Lassi (Salted)", "Salted yogurt drink with cumin", 90.0, "Beverage"),
                    ("Rasmalai", "Soft paneer discs in saffron milk", 140.0, "Dessert"),
                ]
                # add until we reach 10 items for this restaurant
                to_add = 10 - existing_items
                for name, desc, price, cat in extra_items[:to_add]:
                    db.session.add(
                        MenuItem(
                            restaurant_id=first_restaurant.id,
                            name=name,
                            description=desc,
                            price=price,
                            category=cat,
                        )
                    )
                db.session.commit()

    @app.route("/")
    def index():
        return redirect(url_for("customer.list_restaurants"))

    return app
