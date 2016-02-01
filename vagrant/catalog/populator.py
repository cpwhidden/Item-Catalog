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

# Clothes

dress = Product(name='Black Dress', imageName = 'black-dress-clipart.jpg', 
	price=49.99, description='A beautiful dress', 
	category=clothes, seller=chris)
session.add(dress)

tshirt = Product(name='T-shirt', imageName = 't-shirt.jpg', 
	price = 29.99, description = 'A basic black t-shirt', 
	category = clothes, seller = chris)
session.add(tshirt)

socks = Product(name='Socks', imageName = 'socks.jpg', 
	price = 19.99, description = 'Nice athletic socks', 
	category = clothes, seller = chris)
session.add(socks)

jacket = Product(name='Jacket', imageName = 'jacket.png', 
	price = 39.99, description = 'Uniform-style jacket', 
	category = clothes, seller = chris)
session.add(jacket)

skirt = Product(name= 'Skirt', imageName = 'skirt.jpg', 
	price = 39.99, description = 'A very colorful skirt', 
	category = clothes, seller = chris)
session.add(skirt)

blouse = Product(name = 'Blouse', imageName = 'blouse.png', 
	price = 59.99, description = 'A pink blouse', 
	category = clothes, seller = chris)
session.add(blouse)

suit = Product(name = 'Suit', imageName = 'suit.jpg', 
	price = 199.99, description = 'A navy suit', 
	category = clothes, seller = chris)
session.add(suit)


# Shoes

boots = Product(name='Leather Boots', imageName = 'leather-boots.jpg', 
	price=79.99, description='Sturdy leather boots', 
	category=shoes, seller=chris)
session.add(boots)

sandals = Product(name='Sandals', imageName = 'sandals.jpg', 
	price = 69.99, description='Comfortable flip-flops', 
	category = shoes, seller = chris)
session.add(sandals)

sneakers = Product(name='Sneakers', imageName = 'sneakers.jpg', 
	price = 89.99, description='High quality running sneakers', 
	category = shoes, seller = chris)
session.add(sneakers)

slippers = Product(name='Slippers', imageName = 'slippers.jpg', 
	price = 79.99, description='Retro slippers', 
	category = shoes, seller = chris)
session.add(slippers)

dressShoes = Product(name='Dress shoes', imageName = 'dress-shoes.jpg', 
	price = 99.99, description='Premium material dress shoes', 
	category = shoes, seller = chris)
session.add(dressShoes)


# Tools

hammer = Product(name='Hammer', imageName = 'hammer.png', 
	price=5.99, description='It\'s a hammer', 
	category = tools, seller = chris)
session.add(hammer)

screwdriver = Product(name='Screwdriver', imageName = 'screwdriver.png', 
	price=5.99, description='Phillip\'s screwdriver', 
	category = tools, seller = chris)
session.add(screwdriver)

pliers = Product(name='Pliers', imageName = 'pliers.jpg', 
	price=6.99, description='Needle-nose pliers', 
	category = tools, seller = chris)
session.add(pliers)

ruler = Product(name='Ruler', imageName = 'ruler.png', 
	price=3.99, description='Metric ruler', 
	category = tools, seller = chris)
session.add(ruler)

thermometer = Product(name='Thermometer', imageName = 'thermometer.png', 
	price = 4.99, description='Tells the temperature', 
	category = tools, seller = chris)
session.add(thermometer)


# Toys

buildingBlocks = Product(name='Building blocks', 
	imageName = 'building-blocks.jpg', price = 14.99, 
	description='Hundreds of blocking blocks', category = toys, 
	seller = chris)
session.add(buildingBlocks)

toyTruck = Product(name='Toy Truck', imageName = 'toy-truck.jpg', 
	price = 2.99, description='Perfect gift for young kids', 
	category = toys, seller = chris)
session.add(toyTruck)

stuffedBear = Product(name='Stuffed Bear', imageName = 'stuffed-bear.jpg', 
	price = 8.99, description='A child\'s best friend', 
	category = toys, seller = chris)
session.add(stuffedBear)

dice = Product(name='Dice', imageName = 'dice.jpg', 
	price = 3.99, description='Dice that can be used for all kinds of games', 
	category = toys, seller = chris)
session.add(dice)

jigsawPuzzle = Product(name='Jigsaw puzzle', imageName = 'jigsaw-puzzle.jpg', 
	price=9.99, description='1000-piece jigsaw puzzle', 
	category = toys, seller = chris)
session.add(jigsawPuzzle)

# Reviews

socksReview = Review(rating=5, description='Very comfortable and last long', 
	product=socks, user=chris)
session.add(socksReview)

bootsReview = Review(rating=3, description='Very sturdy!', 
	product=boots, user=chris)
session.add(bootsReview)

hammerReview = Review(rating=4, 
	description='If you have nails, you *need* this hammer', 
	product=hammer, user=chris)
session.add(hammerReview)

stuffedBearReview = Review(rating=4, 
	description='Every child would love this stuff animal', 
	product=stuffedBear, user=chris)
session.add(stuffedBearReview)


session.commit()