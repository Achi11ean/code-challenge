#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False
db.init_app(app)

migrate = Migrate(app, db)


api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"
@app.get('/restaurants')
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([{
        'id': restaurant.id,
        'name': restaurant.name,
        'address': restaurant.address
    } for restaurant in restaurants]), 200


@app.get('/restaurants/<int:id>')
def get_restaurant_by_id(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant:
        restaurant_data = {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "restaurant_pizzas": [{
                "id": rp.id,
                "pizza": {
                    "id": rp.pizza.id,
                    "name": rp.pizza.name,
                    "ingredients": rp.pizza.ingredients
                },
                "pizza_id": rp.pizza_id,
                "price": rp.price,
                "restaurant_id": rp.restaurant_id
            } for rp in restaurant.restaurant_pizzas]
        }
        return jsonify(restaurant_data), 200
    else:
        return jsonify({"error": "Restaurant not found"}), 404
    

@app.delete('/restaurants/<int:id>')
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    
    if restaurant:
        for rp in restaurant.restaurant_pizzas:
            db.session.delete(rp)
        
        db.session.delete(restaurant)
        db.session.commit()
        
        return '', 204
    
    else:
        return jsonify({"error": "Restaurant not found"}), 404
@app.get('/pizzas')
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict(only=("id", "ingredients", "name")) for pizza in pizzas]), 200

@app.post('/restaurant_pizzas')
def create_restaurant_pizza():
    data = request.get_json()

    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    if not (1 <= price <= 30):
        return jsonify({"errors": ["validation errors"]}), 400

    pizza = db.session.get(Pizza, pizza_id)
    restaurant = db.session.get(Restaurant, restaurant_id)

    if not pizza or not restaurant:
        return jsonify({"errors": ["Invalid pizza or restaurant ID"]}), 400

    try:
        restaurant_pizza = RestaurantPizza(
            price=price, pizza_id=pizza_id, restaurant_id=restaurant_id
        )

        db.session.add(restaurant_pizza)
        db.session.commit()

        return jsonify({
            "id": restaurant_pizza.id,
            "pizza": {
                "id": pizza.id,
                "ingredients": pizza.ingredients,
                "name": pizza.name
            },
            "pizza_id": pizza.id,
            "price": restaurant_pizza.price,
            "restaurant": {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address
            },
            "restaurant_id": restaurant.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": ["An error occurred while creating the restaurant pizza"]}), 500

if __name__ == "__main__":
    app.run(port=5555, debug=True)
