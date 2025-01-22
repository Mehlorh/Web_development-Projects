import unittest
from app import app, db, Product, CartItem, FavoriteItem

class TestFlaskApp(unittest.TestCase):

    def setUp(self):
        """Set up a temporary test database."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            # Populate the database with initial data
            self.populate_database()

    def tearDown(self):
        """Tear down the test database."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def populate_database(self):
        initial_products = [
            Product(name="Test Product 1", price=100.0, image="test1.png"),
            Product(name="Test Product 2", price=200.0, image="test2.png"),
        ]
        db.session.bulk_save_objects(initial_products)
        db.session.commit()

    def test_home_page(self):
        """Test if the home page loads correctly."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_products_page(self):
        """Test if the products page shows the products."""
        response = self.app.get('/products')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Product 1', response.data)

    def test_add_to_cart(self):
        """Test adding a product to the cart."""
        response = self.app.post('/add_to_cart/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Product added to cart', response.data)

    def test_remove_from_cart(self):
        """Test removing a product from the cart."""
        self.app.post('/add_to_cart/1')
        response = self.app.post('/remove_from_cart/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Product removed from cart', response.data)

    def test_add_to_favorites(self):
        """Test adding a product to favorites."""
        response = self.app.post('/add_to_favorites/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Product added to favorites', response.data)

    def test_remove_from_favorites(self):
        """Test removing a product from favorites."""
        self.app.post('/add_to_favorites/1')
        response = self.app.post('/remove_from_favorites/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Product removed from favorites', response.data)

    def test_cart_page(self):
        """Test if the cart page shows the correct total."""
        self.app.post('/add_to_cart/1')
        self.app.post('/add_to_cart/2')
        response = self.app.get('/cart')
        self.assertIn(b'300.0', response.data)

    def test_favorites_page(self):
        """Test if the favorites page shows the correct products."""
        self.app.post('/add_to_favorites/1')
        response = self.app.get('/favorites')
        self.assertIn(b'Test Product 1', response.data)

if __name__ == '__main__':
    unittest.main()
