from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import stripe

app = Flask(__name__)

# Configure the SQLAlchemy part of the app instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)

# Configure your Stripe API keys
stripe.api_key = 'sk_test_51QixOJD6xYpPHRNxL8VwrPnUKTzW1ve3RsHZMrfnHjOouFZd60pGeDS2OzBYcWiZ5yx0KPWk9ZFrKQBppjfaUJid00eT98FuYf'
STRIPE_PUBLIC_KEY = 'pk_test_51QixOJD6xYpPHRNx03HL6LIPSP3oBcg3lpB9KM1pUlWr9IZjrx8qGiEzfFLlZFECegCPkLpEErLIRDrLzTmrrYmA00xrzaMnmO'

# Models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(120), nullable=False)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

class FavoriteItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

# Initialize the database
with app.app_context():
    db.create_all()

def populate_database():
    if Product.query.count() == 0:
        initial_products = [
            Product(name="Air Jordan 1 Low Make", price=2599.95, image="/static/images/Air Jordan 1 Low Make.png"),
            Product(name="Lebron XXII Sneakers", price=3699.95, image="/static/images/Lebron XXII.png"),
            Product(name="Nike Heritage Eugene Backpack", price=999.95, image="/static/images/Heritage Bag.png"),
            Product(name="LA Lakers T-Shirt", price=699.95, image="/static/images/Air Jordan 1 Low Make.png"),
            Product(name="Nike Air Max Portal", price=2199.95, image="/static/images/latest1.png"),
            Product(name="Nike Air Backpack 20L", price=649.95, image="/static/images/latest2.png"),
            Product(name="Nike Metcon 9 AMP", price=2999.95, image="/static/images/latest3.png"),
            Product(name="Nike MC Trainer 3", price=1599.95, image="/static/images/latest4.png"),
            Product(name="Nike Heritage Bag 4L", price=429.95, image="/static/images/latest5.png"),
            Product(name="Nike Max90 T-Shirt", price=699.95, image="/static/images/latest6.png"),
            Product(name="Nike Therma Sweatshirt", price=1399.95, image="/static/images/latest7.png"),
            Product(name="Nike Tennis Hoodie", price=1599.95, image="/static/images/latest8.png"),
            Product(name="Nike Jacquard Golf Polo", price=1399.95, image="/static/images/latest9.png"),
            Product(name="Nike Sportswear Cross-Body Bag", price=549.95, image="/static/images/latest10.png"),
            Product(name="Jordan Flight Suit", price=1899.95, image="/static/images/latest12.png"),
            Product(name="Nike Air Max 97 SE", price=2299.95, image="/static/images/latest11.png")
        ]
        db.session.bulk_save_objects(initial_products)
        db.session.commit()

@app.before_request
def before_request():
    populate_database()

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/products')
def products_page():
    all_products = Product.query.all()
    return render_template('products.html', products=all_products)

@app.route('/favorites')
def favorites_page():
    favorite_items = FavoriteItem.query.all()
    favorites = [Product.query.get(item.product_id) for item in favorite_items]
    return render_template('favorites.html', favorites=favorites)

@app.route('/cart')
def cart_page():
    cart_items = CartItem.query.all()
    cart = [Product.query.get(item.product_id) for item in cart_items]
    total = sum(item.price for item in cart)
    return render_template('cart.html', cart=cart, total=total, stripe_public_key=STRIPE_PUBLIC_KEY)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    if CartItem.query.filter_by(product_id=product_id).first():
        return jsonify({'error': 'Product already in cart'}), 400

    cart_item = CartItem(product_id=product_id)
    db.session.add(cart_item)
    db.session.commit()
    return jsonify({'message': 'Product added to cart', 'product': {'name': product.name, 'price': product.price, 'image': product.image}}), 200

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart_item = CartItem.query.filter_by(product_id=product_id).first()
    if not cart_item:
        return jsonify({'error': 'Product not found in cart'}), 404

    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'Product removed from cart'}), 200

@app.route('/add_to_favorites/<int:product_id>', methods=['POST'])
def add_to_favorites(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    if FavoriteItem.query.filter_by(product_id=product_id).first():
        return jsonify({'error': 'Product already in favorites'}), 400

    favorite_item = FavoriteItem(product_id=product_id)
    db.session.add(favorite_item)
    db.session.commit()
    return jsonify({'message': 'Product added to favorites', 'product': {'name': product.name, 'price': product.price, 'image': product.image}}), 200

@app.route('/remove_from_favorites/<int:product_id>', methods=['POST'])
def remove_from_favorites(product_id):
    favorite_item = FavoriteItem.query.filter_by(product_id=product_id).first()
    if not favorite_item:
        return jsonify({'error': 'Product not found in favorites'}), 404

    db.session.delete(favorite_item)
    db.session.commit()
    return jsonify({'message': 'Product removed from favorites'}), 200

@app.route('/checkout', methods=['POST'])
def checkout():
    # Prepare the cart items for Stripe checkout session
    cart_items = CartItem.query.all()
    cart_products = [Product.query.get(item.product_id) for item in cart_items]
    total_amount = int(sum(item.price for item in cart_products) * 100)  # Amount in cents

    # Create a new Stripe Checkout session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'zar',
                    'product_data': {
                        'name': item.name,
                    },
                    'unit_amount': int(item.price * 100),  # Amount in cents
                },
                'quantity': 1,
            }
            for item in cart_products
        ],
        mode='payment',
        success_url=url_for('payment_success', _external=True),
        cancel_url=url_for('cart_page', _external=True),
    )

    # Return the session ID as JSON
    return jsonify({'id': session.id})

@app.route('/payment_success')
def payment_success():
    # After successful payment, clear the cart
    CartItem.query.delete()
    db.session.commit()
    return render_template('payment_success.html')

@app.route('/favorites_data')
def favorites_data():
    favorite_items = FavoriteItem.query.all()
    favorites = [{'id': item.product_id, 'name': Product.query.get(item.product_id).name, 'price': Product.query.get(item.product_id).price, 'image': Product.query.get(item.product_id).image} for item in favorite_items]
    return jsonify(favorites=favorites)

@app.route('/cart_data')
def cart_data():
    cart_items = CartItem.query.all()
    cart = [{'id': item.product_id, 'name': Product.query.get(item.product_id).name, 'price': Product.query.get(item.product_id).price, 'image': Product.query.get(item.product_id).image} for item in cart_items]
    return jsonify(cart=cart)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)
