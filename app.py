from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy 

from cloudipsp import Api, Checkout

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///eshop.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    isAvailable = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Product: {self.name}>"


@app.route("/")
def index():
    products = Product.query.order_by(Product.price).all()
    return render_template("index.html", data=products)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        description = request.form["description"]
        product = Product(name=name, price=price, description=description)
        try:
            db.session.add(product)
            db.session.commit()
            return redirect(url_for("index"))
        except ValueError as e:
            return f"There was an issue adding your product: {e}"
    return render_template("create.html")


@app.route("/products")
def products():
    products = Product.query.all()
    return render_template("products.html", products=products)

@app.route("/buy_product/<int:id>")
def buy_product(id):
    try:
        product = Product.query.get(id)
        api = Api(merchant_id=1396424,
                secret_key='test')
        checkout = Checkout(api=api)
        data = {
            "currency": "USD",
            "amount": product.price * 100
        }
        url = checkout.url(data).get('checkout_url')
    except Exception as e:
        print(e)
        return redirect(url_for("index"))
    return redirect(url)


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)

