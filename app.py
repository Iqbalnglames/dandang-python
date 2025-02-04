from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from flask_bcrypt import Bcrypt
import random

app = Flask(__name__)
app.secret_key = "secret123"
bcrypt = Bcrypt(app)


# Fungsi untuk membuat database
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Buat tabel produk
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        slug TEXT NOT NULL,
        price REAL NOT NULL
    )
    """)

    # Buat tabel pesanan
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kd_order TEXT NOT NULL,
        product_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        customer_name TEXT NOT NULL,
        address TEXT NOT NULL,
        contact TEXT NOT NULL
    )
    """)

    # Tambahkan produk contoh jika belum ada
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO products (name, slug, price) VALUES (?, ?, ?)", [
            ("Dandang 6kg", "dandang-6kg", 200000),
            ("Dandang 8kg", "dandang-8kg", 300000),
            ("Dandang 10kg", "dandang-10kg", 500000)
        ])
        conn.commit()

    conn.close()

# Panggil fungsi untuk inisialisasi database
init_db()

# Route untuk halaman utama
@app.route("/")
def index():
    
    return render_template("index.html")

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/product')
def product():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, slug, price FROM products")
    products = cursor.fetchall()
    conn.close()
    return render_template("products.html", products=products)

@app.route('/cart/<string:produk>')
def cart(produk):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, slug, price FROM products WHERE slug = ?', (produk,))
    product = cursor.fetchone()
    conn.close()
    return render_template('checkout.html', product=product)


# Route untuk menangani pemesanan
@app.route("/place_order", methods=["POST"])
def place_order():
    kd_order = random.randint(10000, 99999)
    product_name = request.form["product_name"]
    quantity = request.form["quantity"]
    customer_name = request.form["customer_name"]
    address = request.form["address"]
    contact = request.form["contact"]

    if not product_name or not quantity or not customer_name or not address or not contact:
        flash("Semua kolom harus diisi!", "danger")
        return redirect(url_for("index"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO orders (kd_order, product_name, quantity, customer_name, address, contact)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (kd_order, product_name, int(quantity), customer_name, address, contact))
    conn.commit()
    conn.close()

    flash("Pesanan berhasil dibuat!", "success")
    return redirect(url_for("index"))


# Route untuk melihat daftar pesanan user side
@app.route("/orders-search", methods=['GET', 'POST'])
def orders():
    orders = []  
    kd_order = ""
    if request.method == 'POST':
        kd_order = request.form['kd_order']
        if kd_order:  # Jika kd_order tidak kosong
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders WHERE kd_order = ?", (kd_order,))
            orders = cursor.fetchall()
            conn.close()
    return render_template("orders_users.html", orders=orders, kd_order=kd_order)

# Route untuk melihat daftar pesanan admin side
@app.route("/orders-admin")
def orders_admin():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    conn.close()
    return render_template("orders_admin.html", orders=orders)

if __name__ == "__main__":
    app.run(debug=True)
