from sqlalchemy import create_engine, Column, Integer, String,Boolean, ForeignKey, Float
from sqlalchemy.orm import declarative_base

db = create_engine('sqlite:///database.db')

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    email = Column(String, nullable=False) 
    password = Column(String)
    active = Column(Boolean)
    admin = Column(Boolean,default=False)

    def __init__(self, name, email, password, active=True, admin=False):
        self.name = name
        self.email = email
        self.password = password
        self.active = active
        self.admin = admin


class Order(Base):
    __tablename__ = 'orders'

    # ORDER_STATUS = (
    #     ('PENDING', 'PENDING'),
    #     ('CANCELLED', 'CANCELLED'),
    #     ('FINISHED', 'FINISHED'),
    # )

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String)
    user = Column(Integer, ForeignKey('users.id'))
    price = Column(Float)

    def __init__(self, user, status='PENDING', price=0):
        self.user = user
        self.status = status
        self.price = price


class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    quantity = Column(Integer)
    flavor = Column(String)
    size = Column(String)
    price = Column(Float)
    order = Column(Integer, ForeignKey('orders.id'))

    def __init__(self,  quantity, flavor, size, price,order_id):
        self.quantity = quantity
        self.flavor = flavor
        self.size = size
        self.price = price
        self.order_id = order_id