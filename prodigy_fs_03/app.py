from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # redirects if not logged in

# Import forms, models, routes AFTER app and db are defined
from models import User  # if you have a separate models.py

# In-memory "database" for demonstration
users = {}  # format: {'username': {'password': hashed_password}}

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password  # This calls the setter below

    # Make password write-only
    @property
    def password(self):
        raise AttributeError('Password is write-only!')

    @password.setter
    def password(self, password_plain):
        self.password_hash = generate_password_hash(password_plain)

    # Check password
    def check_password(self, password_plain):
        return check_password_hash(self.password_hash, password_plain)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 🏠 HOME
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/latest')
def latest():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password")

    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Check if username exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))

        # Create new user
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# 🛍️ PRODUCTS (match your HTML IDs exactly)
products = {
    1: {"name": "Checker Shorts", "price": 29.99, "image": "/static/webimages/images08.png"},
    2: {"name": "Too Cool Sweatshirt", "price": 49.99, "image": "/static/webimages/images09.png"},
    3: {"name": "Yellow Sweatshirt", "price": 19.99, "image": "/static/webimages/images10.png"},
    4: {"name": "Grey Sweatshirt", "price": 19.99, "image": "/static/webimages/images11.png"},
    5: {"name": "Joggers", "price": 19.99, "image": "/static/webimages/images12.png"},
    6: {"name": "Vintage Coat", "price": 19.99, "image": "/static/webimages/images13.png"},
}


# 🛒 ADD TO CART
@app.route('/add_to_cart/<int:id>')
def add_to_cart(id):
    if 'cart' not in session:
        session['cart'] = []

    cart = session['cart']

    product = products.get(id)

    if product:
        for item in cart:
            if item['id'] == id:
                item['quantity'] = item.get('quantity', 1) + 1
                break
        else:
            cart.append({
                "id": id,
                "name": product['name'],
                "price": product['price'],
                "image": product['image'],
                "quantity": 1
            })

    session['cart'] = cart
    return redirect(url_for('cart'))


# 🛒 CART PAGE
@app.route('/cart')
@login_required
def cart():
    cart = session.get('cart', [])

    # 🔥 FIX: ensure all items have quantity
    for item in cart:
        if 'quantity' not in item:
            item['quantity'] = 1

    subtotal = sum(item['price'] * item.get('quantity', 1) for item in cart)
    shipping = 10 if subtotal > 0 else 0
    total = subtotal + shipping

    session['cart'] = cart

    return render_template(
        'cart.html',
        cart=cart,
        subtotal=subtotal,
        shipping=shipping,
        total=total
    )

# 🔄 UPDATE QUANTITY
@app.route('/update_quantity/<int:id>', methods=['POST'])
def update_quantity(id):
    quantity = int(request.form.get('quantity', 1))

    cart = session.get('cart', [])

    for item in cart:
        if item['id'] == id:
            item['quantity'] = quantity
            break

    session['cart'] = cart
    return redirect(url_for('cart'))


# ❌ REMOVE ITEM
@app.route('/remove/<int:id>')
def remove(id):
    cart = session.get('cart', [])
    cart = [item for item in cart if item['id'] != id]

    session['cart'] = cart
    return redirect(url_for('cart'))


# 🧹 CLEAR CART (VERY IMPORTANT)
@app.route('/clear_cart')
def clear_cart():
    session.clear()
    return "Cart cleared!"


if __name__ == '__main__':
    with app.app_context():
      db.create_all()
    app.run(debug=True)