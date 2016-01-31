from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from server import flask
from server.models import Base, Category, User, Product, Review

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

clothes = Category(name='Clothes')
session.add(clothes)

shoes = Category(name='Shoes')
session.add(shoes)

tools = Category(name='Tools')
session.add(tools)

toys = Category(name='Toys')
session.add(toys)

chris = User(oauth_id='0', name='Chris')
session.add(chris)

dress = Product(name='Dress', price=49.99, description='A beautiful dress', category=clothes, seller=chris)
session.add(dress)

boots = Product(name='Boots', price=79.99, description='Sturdy leather boots', category=shoes, seller=chris)
session.add(boots)

bootsReview = Review(rating=3, description='Very sturdy!', product=boots, user=chris)
session.add(bootsReview)

session.commit()