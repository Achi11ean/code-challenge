from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    restaurant_pizzas = relationship('RestaurantPizza', back_populates='restaurant', cascade="all, delete-orphan")

    pizzas = association_proxy('restaurant_pizzas', 'pizza')

    serialize_rules = ('-pizzas.restaurant_pizzas',)

    def to_dict(self, include_pizzas=False):
        """Override to_dict to optionally include restaurant_pizzas."""
        restaurant_data = super().to_dict()
        
        if include_pizzas:
            restaurant_data['restaurant_pizzas'] = [rp.to_dict() for rp in self.restaurant_pizzas]
        
        return restaurant_data
class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    restaurant_pizzas = relationship('RestaurantPizza', back_populates='pizza', cascade="all, delete-orphan")

    restaurants = association_proxy('restaurant_pizzas', 'restaurant')

    serialize_rules = ('-restaurant_pizzas.pizza', '-restaurants.restaurant_pizzas')

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    restaurant_id = db.Column(db.Integer, ForeignKey('restaurants.id'), nullable=False)
    pizza_id = db.Column(db.Integer, ForeignKey('pizzas.id'), nullable=False)

    restaurant = relationship('Restaurant', back_populates='restaurant_pizzas')
    pizza = relationship('Pizza', back_populates='restaurant_pizzas')

    serialize_rules = ('-restaurant.restaurant_pizzas', '-pizza.restaurant_pizzas')

    @validates('price')
    def validate_price(self, key, price):
        if not (1 <= price <= 30):
            raise ValueError("Price must be between $10 and $30")
        return price

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"