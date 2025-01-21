# Flask E-commerce Application

This repository contains a Flask-based e-commerce application with features such as product listing, cart management, favorite items, and Stripe-powered checkout.

## Features

- **Product Management**: View, add, and manage products.
- **Cart Functionality**: Add or remove products from the cart.
- **Favorites**: Add or remove products from your favorites.
- **Stripe Integration**: Checkout and payments handled via Stripe.
- **Database**: SQLAlchemy used for database interactions with SQLite.
- **Templating**: HTML templates rendered using Flask's Jinja2.
- **API Endpoints**: JSON endpoints for cart and favorite data.

## Prerequisites

- Python 3.x
- Virtual environment tool (optional but recommended)

## Installation

1. **Clone the repository**:

   git clone https://github.com/Mehlorh/Web_development-Projects/main/web%20projects/E-commerce%20page.git
   cd E-commerce page
   

3. **Create and activate a virtual environment** (optional but recommended):

   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`

4. **Install the required packages**:

   pip install -r requirements.txt

5. **Run the application**:

   python app.py   

   The app will be accessible at `http://127.0.0.1:5000/`.

## Database Setup

The database is automatically initialized with some sample products when the app runs for the first time.

## Usage

- Visit the home page to view products.
- Use the "Add to Cart" or "Add to Favorites" buttons to manage your selections.
- Navigate to the cart or favorites page to review your selections.
- Proceed to checkout to complete your purchase using Stripe.

## API Endpoints

- `GET /favorites_data`: Retrieve favorite items data as JSON.
- `GET /cart_data`: Retrieve cart items data as JSON.


## Contributing

Contributions are welcome! Please open an issue or submit a pull request to discuss changes.

## Author

- [Sboniso Mnncwango](https://github.com/Mehlorh)

