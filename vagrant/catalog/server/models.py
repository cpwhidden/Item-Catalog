from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine, Table, Column, ForeignKey, Integer, String, Numeric, Date
from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask.ext.uploads import UploadSet, IMAGES
from wtforms import DateField, DecimalField, IntegerField, RadioField, SelectField, StringField, TextAreaField
from wtforms.validators import InputRequired, Length, NumberRange, Regexp
import datetime

Base = declarative_base()

class ShoppingCart(Base):
	__tablename__ = 'shopping_cart'

	buyer_id = Column(Integer, ForeignKey('user.id'), primary_key = True)
	product_id = Column(Integer, ForeignKey('product.id'), primary_key = True)
	quantity = Column(Integer, server_default='1')
	buyer = relationship('User', back_populates='shoppingCartProducts')
	product = relationship('Product', back_populates='buyers')


class Category(Base):
	__tablename__ = 'category'

	id = Column(Integer, primary_key = True)
	name = Column(String(100), nullable = False, unique = True)

	@property
	def serialize(self):
		return {
			'id' : self.id,
			'name' : self.name
		}


class User(Base):
	__tablename__ = 'user'

	id = Column(Integer, primary_key = True)
	oauth_id = Column(Integer, unique = True)
	name = Column(String(60))
	email = Column(String(100))
	shoppingCartProducts = relationship(ShoppingCart)
	reviews = relationship('Review', cascade='all, delete-orphan')
	productsSold = relationship('Product', cascade='all, delete-orphan')
	productsBuying = relationship('ShoppingCart', cascade='all, delete-orphan')


class UserForm(Form):
	name = StringField('Name', [InputRequired(), Length(min=1,max=60)])


class Product(Base):
	__tablename__ = 'product'

	id = Column(Integer, primary_key = True)
	name = Column(String(100), nullable = False, unique = True)
	price = Column(Numeric(10,2))
	description = Column(String(500))
	imageName = Column(String(100), server_default = 'default_product.png')
	dateAdded = Column(Date, nullable = False, server_default = datetime.date.today().strftime('%Y-%m-%d %H-%M-%S'))
	category_id = Column(Integer, ForeignKey('category.id'))
	category = relationship(Category)
	seller_id = Column(Integer, ForeignKey('user.id'))
	seller = relationship(User)
	buyers = relationship(ShoppingCart)
	reviews = relationship('Review', cascade='all, delete-orphan')
	productsBeingBought = relationship('ShoppingCart', cascade='all, delete-orphan')

	@property
	def serialize(self):
		# Returns object data in easily serializeable format
		return {
			'id' : self.id,
			'name' : self.name,
			'description' : self.description,
			'price' : self.price,
			'dateAdded' : self.dateAdded.strftime('%Y-%m-%d'),
			'category' : self.category.name
		}


images = UploadSet('images', IMAGES)

class ProductForm(Form):
	name = StringField('Name', [InputRequired(), Length(min=1,max=100)])
	price = DecimalField('Price', [InputRequired(), NumberRange(min=0,max=99999999.99)])
	description = TextAreaField('Description', [InputRequired(), Length(min=1,max=500)])
	image = FileField('Image', [FileAllowed(images, 'Upload image files only')])
	category_id = SelectField('Category', coerce=int)


class Review(Base):
	__tablename__ = 'review'

	id = Column(Integer, primary_key = True)
	rating = Column(Integer)
	description = Column(String(500))
	dateAdded = Column(Date, nullable = False, server_default = datetime.date.today().strftime('%Y-%m-%d'))
	product_id = Column(Integer, ForeignKey('product.id'))
	product = relationship(Product)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	@property
	def serialize(self):
		return {
			'id' : self.id,
			'rating' : self.rating,
			'description' : self.description,
			'dateAdded' : self.dateAdded.strftime('%Y-%m-%d'),
			'product' : self.product.name,
			'user' : self.user.name
		}


class ReviewForm(Form):
	rating = SelectField('Rating', [InputRequired()], choices=[(1,'1'),(2,'2'),(3,'3'),(4,'4'),(5,'5')], coerce=int)
	description = TextAreaField('Review', [InputRequired(), Length(min=1,max=500)])


engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)