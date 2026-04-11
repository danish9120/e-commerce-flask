from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import json
import os

app = Flask(__name__)
app.secret_key = 'ecommerce-secret-key-2026'

# ── Sample product data ──────────────────────────────────────────────────────
PRODUCTS = [
    {"id": 1, "name": "Wireless Headphones", "price": 149.99, "category": "Electronics",
     "description": "Premium sound with active noise cancellation and 30-hour battery life.",
     "image": "🎧", "rating": 4.8, "reviews": 234, "badge": "Best Seller"},
    {"id": 2, "name": "Minimalist Watch", "price": 299.99, "category": "Accessories",
     "description": "Swiss-inspired design with sapphire crystal glass and leather strap.",
     "image": "⌚", "rating": 4.9, "reviews": 189, "badge": "New"},
    {"id": 3, "name": "Running Shoes", "price": 119.99, "category": "Sports",
     "description": "Lightweight carbon-fiber sole with breathable mesh upper.",
     "image": "👟", "rating": 4.7, "reviews": 412, "badge": "Popular"},
    {"id": 4, "name": "Leather Backpack", "price": 189.99, "category": "Accessories",
     "description": "Full-grain Italian leather with padded laptop compartment.",
     "image": "🎒", "rating": 4.6, "reviews": 97, "badge": ""},
    {"id": 5, "name": "Smart Speaker", "price": 89.99, "category": "Electronics",
     "description": "360° sound with built-in AI assistant and smart home control.",
     "image": "🔊", "rating": 4.5, "reviews": 301, "badge": "Sale"},
    {"id": 6, "name": "Yoga Mat", "price": 64.99, "category": "Sports",
     "description": "Extra-thick eco-friendly cork surface with alignment lines.",
     "image": "🧘", "rating": 4.8, "reviews": 156, "badge": ""},
    {"id": 7, "name": "Sunglasses", "price": 229.99, "category": "Accessories",
     "description": "Polarized UV400 lenses in titanium frame. Handcrafted in Italy.",
     "image": "🕶️", "rating": 4.9, "reviews": 78, "badge": "Premium"},
    {"id": 8, "name": "Mechanical Keyboard", "price": 174.99, "category": "Electronics",
     "description": "Hot-swappable switches, RGB per-key lighting, aluminum chassis.",
     "image": "⌨️", "rating": 4.7, "reviews": 543, "badge": ""},
]

CATEGORIES = ["All", "Electronics", "Accessories", "Sports"]

# ── Helpers ──────────────────────────────────────────────────────────────────
def get_cart():
    return session.get('cart', {})

def cart_count():
    return sum(get_cart().values())

def cart_total():
    cart = get_cart()
    total = 0
    for pid, qty in cart.items():
        product = next((p for p in PRODUCTS if p['id'] == int(pid)), None)
        if product:
            total += product['price'] * qty
    return round(total, 2)

# ── Routes ───────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    category = request.args.get('category', 'All')
    search = request.args.get('search', '').lower()
    sort = request.args.get('sort', 'default')

    products = PRODUCTS[:]
    if category != 'All':
        products = [p for p in products if p['category'] == category]
    if search:
        products = [p for p in products if search in p['name'].lower() or search in p['description'].lower()]
    if sort == 'price_asc':
        products.sort(key=lambda p: p['price'])
    elif sort == 'price_desc':
        products.sort(key=lambda p: p['price'], reverse=True)
    elif sort == 'rating':
        products.sort(key=lambda p: p['rating'], reverse=True)

    return render_template('index.html',
        products=products,
        categories=CATEGORIES,
        selected_category=category,
        search=search,
        sort=sort,
        cart_count=cart_count()
    )

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if not product:
        return redirect(url_for('index'))
    related = [p for p in PRODUCTS if p['category'] == product['category'] and p['id'] != product_id][:3]
    return render_template('product.html', product=product, related=related, cart_count=cart_count())

@app.route('/cart')
def cart():
    cart_data = get_cart()
    items = []
    for pid, qty in cart_data.items():
        product = next((p for p in PRODUCTS if p['id'] == int(pid)), None)
        if product:
            items.append({**product, 'qty': qty, 'subtotal': round(product['price'] * qty, 2)})
    return render_template('cart.html', items=items, total=cart_total(), cart_count=cart_count())

@app.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    cart = get_cart()
    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + 1
    session['cart'] = cart
    return jsonify({'success': True, 'cart_count': cart_count(), 'message': 'Added to cart!'})

@app.route('/cart/update', methods=['POST'])
def update_cart():
    data = request.get_json()
    pid = str(data.get('product_id'))
    qty = int(data.get('qty', 0))
    cart = get_cart()
    if qty <= 0:
        cart.pop(pid, None)
    else:
        cart[pid] = qty
    session['cart'] = cart
    return jsonify({'success': True, 'cart_count': cart_count(), 'total': cart_total()})

@app.route('/cart/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = get_cart()
    cart.pop(str(product_id), None)
    session['cart'] = cart
    return jsonify({'success': True, 'cart_count': cart_count(), 'total': cart_total()})

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        session['cart'] = {}
        return render_template('success.html', cart_count=0)
    cart_data = get_cart()
    items = []
    for pid, qty in cart_data.items():
        product = next((p for p in PRODUCTS if p['id'] == int(pid)), None)
        if product:
            items.append({**product, 'qty': qty, 'subtotal': round(product['price'] * qty, 2)})
    if not items:
        return redirect(url_for('cart'))
    return render_template('checkout.html', items=items, total=cart_total(), cart_count=cart_count())

if __name__ == '__main__':
    app.run(debug=True)