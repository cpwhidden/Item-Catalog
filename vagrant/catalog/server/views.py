from server import flask, dbPath
from server.models import Base, Category, Product, ProductForm, User, UserForm, Review, ReviewForm, ShoppingCart
from sqlalchemy import create_engine, desc, func
from sqlalchemy.orm import sessionmaker
from flask import url_for, render_template, session as login_session, redirect, request, make_response
import datetime
from flask_wtf import Form
from werkzeug import secure_filename
import os
from apiclient import discovery
import httplib2
from oauth2client import client
import requests
import json
import random
import string

engine = create_engine(dbPath)
Base.metadata.bind = engine
session = sessionmaker(engine)()


@flask.route('/')
@flask.route('/home')
def home():
	highestRated = session.query(Product.id, Product.name, Product.price, Product.imageName, func.avg(Review.rating).label('averageRating')).join(Review, Product.id == Review.product_id).group_by(Product.id).order_by(desc(Review.rating)).limit(10).all()
	newlyAdded = session.query(Product).order_by(desc(Product.dateAdded)).limit(10).all()
	currentUser = getCurrentUser()
	return render_template('home.html', highestRated = highestRated, newlyAdded = newlyAdded)


@flask.route('/login')
def login():
	user = session.query(User).first()
	login_session['user_id'] = user.id
	return redirect(url_for('home'))

@flask.route('/logout')
def logout():
	if 'user_id' in login_session:
		del login_session['user_id']
	return redirect(url_for('home'))

@flask.route('/shopping-cart')
def shoppingCart():
	user = getCurrentUser()
	if user != None:
		shoppingCart = session.query(Product.id, Product.name, Product.imageName, Product.price, ShoppingCart.quantity).join(ShoppingCart, Product.id == ShoppingCart.product_id).join(User, User.id == ShoppingCart.buyer_id)
		products = shoppingCart.all()
		count = len(products)
		totalQuery = session.query(func.sum(Product.price * ShoppingCart.quantity)).join(ShoppingCart, Product.id == ShoppingCart.product_id).join(User, User.id == ShoppingCart.buyer_id).one()[0]
		total = '0.00'
		if totalQuery != None:
			total = '%0.2f' % totalQuery
		print total
		return render_template('shopping-cart.html', user = user, products = products, count = count, total = total)
	else:
		return redirect(url_for('home'))

@flask.route('/product/<int:product_id>/add-to-cart')
def addToCart(product_id):
	currentUser = getCurrentUser()
	if currentUser != None:
		existingRecord = session.query(ShoppingCart).join(User, User.id == ShoppingCart.buyer_id).filter(ShoppingCart.product_id == product_id, User.id == currentUser.id).first()
		if existingRecord != None:
			existingRecord.quantity += 1
			session.add(existingRecord)
		else:
			product = session.query(Product).filter(Product.id == product_id).one()
			shoppingRecord = ShoppingCart()
			shoppingRecord.buyer = currentUser
			shoppingRecord.product = product
			session.add(shoppingRecord)
		session.commit()
		return redirect(url_for('shoppingCart'))
	else:
		return redirect(url_for('home'))

@flask.route('/product/<int:product_id>/remove-from-cart')
def removeFromCart(product_id):
	currentUser = getCurrentUser()
	form = Form()
	if form.validate_on_submit():
		shoppingRecord = session.query(ShoppingCart).filter(product_id == product_id, buyer_id == currentUser.id)



@flask.route('/search')
def search():
	query = request.args.get('query')
	if query == '':
		return redirect(url_for('home'))
	else:
		currentPage = request.args.get('page')
		if currentPage == None:
			currentPage = 1
		return redirect(url_for('searchPage', query = query, currentPage = currentPage))


@flask.route('/search/<string:query>/page/<int:currentPage>')
def searchPage(query, currentPage):
	resultsPerPage = 10
	currentUser = getCurrentUser()
	offset = resultsPerPage * (currentPage - 1)
	totalPages = (session.query(Product).filter(Product.name.contains(query)).count() - 1) / resultsPerPage + 1
	if currentPage > totalPages:
		currentPage = 1
	products = session.query(Product).filter(Product.name.contains(query)).offset(offset).limit(resultsPerPage).all()
	pages = [(i+1) for i in range(totalPages)]
	return render_template('search.html', query = query, currentPage = currentPage, pages= pages, totalPages = totalPages, currentUser = currentUser, products = products)

@flask.route('/category/<string:category_name>')
def category(category_name):
	return redirect(url_for('categoryPage', category_name = category_name, currentPage = 1))

@flask.route('/category/<string:category_name>/<int:currentPage>')
def categoryPage(category_name, currentPage):
	resultsPerPage = 10
	offset = resultsPerPage * (currentPage - 1)
	currentUser = getCurrentUser()
	currentCategory = session.query(Category).filter(Category.name == category_name).one()
	totalPages = (session.query(Product).filter(Product.category == currentCategory).count() - 1) / resultsPerPage + 1
	pages = [(i+1) for i in range(totalPages)]
	if currentPage > totalPages:
		currentPage = 1
	categories = session.query(Category).all()
	highestRated = session.query(Product.id, Product.name, Product.imageName, Product.price, func.avg(Review.rating).label('averageRating')).join(Review, Product.id == Review.product_id).filter(Product.category == currentCategory).group_by(Product.id).order_by(desc(Review.rating)).limit(10).all()
	newlyAdded = session.query(Product).filter(Product.category == currentCategory).order_by(desc(Product.dateAdded)).limit(10).all()
	products = session.query(Product).filter(Product.category == currentCategory).offset(offset).limit(resultsPerPage).all()
	return render_template('category.html', categories = categories, currentPage = currentPage, pages = pages, totalPages = totalPages, currentCategory = currentCategory, products = products, highestRated = highestRated, newlyAdded = newlyAdded, currentUser = currentUser)

@flask.route('/user/<int:user_id>/profile')
def userProfile(user_id):
	user = session.query(User).filter(User.id == user_id).one()
	if matchesLoginUser(user):
		products = session.query(Product).filter(Product.seller == user).all()
		reviews = session.query(Review).filter(Review.user == user).all()
		return render_template('user-profile.html', currentUser = user, user = user, products = products, reviews = reviews)
	else:
		return redirect(url_for('home'))

@flask.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
def editUser(user_id):
	user = session.query(User).filter(User.id == user_id).one()
	if matchesLoginUser(user):
		form = UserForm(request.form, user)
		if form.validate_on_submit():
			form.populate_obj(user)
			session.add(user)
			session.commit()
			return redirect(url_for('userProfile', user_id = user_id))
		else:
			return render_template('edit-user.html', currentUser = user, form = form, user = user)
	else:
		return redirect(render_template('home'))

@flask.route('/user/<int:user_id>/profile/delete', methods=['GET', 'POST'])
def deleteUser(user_id):
	user = session.query(User).filter(User.id == user_id).one()
	if matchesLoginUser(user):
		products = session.query(Product).filter(Product.seller == user).all()
		form = Form()
		if form.validate_on_submit():
			session.delete(user)
			if 'user_id' in login_session:
				del login_session['user']
			session.commit()
			return redirect(url_for('home'))
		else:
			return render_template('delete-user.html', currentUser = user, form = form, user = user, products = products)
	else:
		return redirect(render_template('home'))

@flask.route('/product/<int:product_id>/profile')
def product(product_id):
	product = session.query(Product).filter(Product.id == product_id).one()
	reviews = session.query(Review).filter(Review.product == product).all()
	ratingQuery = session.query(func.avg(Review.rating)).join(Product, Product.id == Review.product_id).one()[0]
	rating = ''
	if ratingQuery != None:
		rating = '%0.1f' % ratingQuery
	currentUser = getCurrentUser()
	isOwner = matchesLoginUser(product.seller)
	return render_template('product.html', currentUser= currentUser, isOwner = isOwner, product = product, reviews = reviews, rating = rating)

@flask.route('/product/new', methods=['GET', 'POST'])
def newProduct():
	user = getCurrentUser()
	if user != None:
		categories = session.query(Category).order_by(Category.name).all()
		form = ProductForm(request.form)
		form.category_id.choices = [(index, cat.name) for (index, cat) in enumerate(categories)]
		if form.validate_on_submit():
			product = Product()
			form.populate_obj(product)
			image = request.files['image']
			if image != None:
				product.imageName = secure_filename(image.filename)
				productImagesPath = flask.config['PRODUCT_IMAGES_FOLDER'] 
				path = os.path.join(productImagesPath, product.imageName)
				image.save(path)
			product.seller = user
			session.add(product)
			session.commit()
			return redirect(url_for('userProfile', user_id = user.id))
		else:
			print form.errors
			return render_template('new-product.html', currentUser = user, form = form)
	else:
		return redirect(url_for('home'))


@flask.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
def editProduct(product_id):
	currentUser = getCurrentUser()
	product = session.query(Product).filter(Product.id == product_id).one()
	if matchesLoginUser(product.seller):
		form = ProductForm(request.form, product)
		categories = session.query(Category).all()
		form.category_id.choices = [(cat.id, cat.name) for cat in categories]
		if form.validate_on_submit():
			form.populate_obj(product)
			print request.files
			if 'image' in request.files and request.files['image'].filename != '':
				image = request.files['image']
				product.imageName = secure_filename(image.filename)
				productImagesPath = flask.config['PRODUCT_IMAGES_FOLDER']
				path = os.path.join(productImagesPath, product.imageName)
				image.save(path)
			session.add(product)
			session.commit()
			return redirect(url_for('userProfile', user_id = product.seller.id))
		else:
			return render_template('edit-product.html', currentUser = currentUser, form = form, product = product)
	else:
		return redirect(url_for('home'))

@flask.route('/product/<int:product_id>/remove', methods=['GET', 'POST'])
def deleteProduct(product_id):
	currentUser = getCurrentUser()
	product = session.query(Product).filter(Product.id == product_id).one()
	if matchesLoginUser(product.seller):
		form = Form()
		if form.validate_on_submit():
			session.delete(product)
			session.commit()
			return redirect(url_for('userProfile', user_id = product.seller.id))
		else:
			return render_template('delete-product.html', currentUser = currentUser, form = form, product = product)
	else:
		return redirect(url_for('home'))

@flask.route('/product/<int:product_id>/review/add', methods=['GET', 'POST'])
def addReview(product_id):
	currentUser = getCurrentUser()
	product = session.query(Product).filter(Product.id == product_id).one()
	if currentUser != None:
		form = ReviewForm(request.form)
		if form.validate_on_submit():
			review = Review()
			form.populate_obj(review)
			review.user = currentUser
			review.product = product
			session.add(review)
			session.commit()
			return redirect(url_for('product', product_id = product_id))
		else:
			return render_template('add-review.html', currentUser = currentUser, form = form, product = product)
	else:
		return redirect(url_for('product', product_id = product_id))

@flask.route('/product/<int:product_id>/review/<int:review_id>/edit', methods=['GET', 'POST'])
def editReview(product_id, review_id):
	currentUser = getCurrentUser()
	product = session.query(Product).filter(Product.id == product_id).one()
	review = session.query(Review).filter(Review.id == review_id).one()
	if matchesLoginUser(review.user):
		form = ReviewForm(request.form, review)
		if form.validate_on_submit():
			form.populate_obj(review)
			session.add(review)
			session.commit()
			return redirect(url_for('product', product_id = product_id))
		else:
			return render_template('edit-review.html', currentUser = currentUser, form = form, product = product)
	else:
		return redirect(url_for('home'))

@flask.route('/product/<int:product_id>/review/<int:review_id>/remove', methods=['GET', 'POST'])
def deleteReview(product_id, review_id):
	currentUser = getCurrentUser()
	product = session.query(Product).filter(Product.id == product_id).one()
	review = session.query(Review).filter(Review.id == review_id).one()
	if matchesLoginUser(review.user):
		form = Form()
		if form.validate_on_submit():
			session.delete(review)
			session.commit()
			return redirect(url_for('product', product_id = product_id))
		else:
			return render_template('delete-review.html', currentUser = currentUser, form = form, product = product, review= review)
	else:
		return redirect(url_for('home'))

@flask.route('/google-login', methods=['POST'])
def googleLogin():
	if request.args.get('state_token') != login_session['state_token']:
		return makeJSONResponse('Invalid state token', 401)
	authorizationCode = request.data
	CLIENT_SECRET_FILE = getClientSecret()
	try:
		credentials = client.credentials_from_clientsecrets_and_code(CLIENT_SECRET_FILE,  ['https://www.googleapis.com/auth/drive.appdata', 'profile', 'email'],
    authorizationCode)
	except client.FlowExchangeError:
		return makeJSONResponse('Failed to exchange authorization code', 401)
	http_auth = credentials.authorize(httplib2.Http())
	drive_service = discovery.build('drive', 'v3', http=http_auth)
	appfolder = drive_service.files().get(fileId='appfolder').execute

	oauth_id = credentials.id_token['sub']
	email = credentials.id_token['email']
	url = 'https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token=%s' % credentials.access_token
	response = requests.get(url)
	data = json.loads(response.text)
	name = data['name']
	matchingUser = session.query(User).filter(User.oauth_id == oauth_id).first()
	if matchingUser == None:
		newUser = User(oauth_id = oauth_id, name = name, email = email)
		session.add(newUser)
		session.commit()
		login_session['user_id'] = newUser.id
	else:
		login_session['user_id'] = matchingUser.id
	return makeJSONResponse('Logged in to Google', 200)

@flask.route('/google-logout')
def googleLogout():
	return 'Logging out of Google'

@flask.route('/facebook-login')
def facebookLogin():
	return 'Logging in with Facebook account'

@flask.route('/facebook-logout')
def facebookLogout():
	return 'Logging out of Facebook'

@flask.context_processor
def utility_processor():
	def getCategories():
		return session.query(Category).order_by(Category.name).all()
	def queryCurrentUser():
		return getCurrentUser()
	def indices(array):
		return [i for i in range(len(array))]
	def generateStateToken():
		state_token = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
		login_session['state_token'] = state_token
		return state_token
	return dict(getCategories = getCategories, queryCurrentUser = queryCurrentUser, indices = indices, generateStateToken = generateStateToken)


# Utility functions
def makeJSONResponse(message, status):
	response = make_response(json.dumps(message), status)
	response.headers['Content-Type'] = 'application/json'
	return response

def getClientSecret():
	#return url_for('static', filename='client_secret.json')
	return 'server/static/client_secret.json'


def getCurrentUser():
	if 'user_id' in login_session and login_session['user_id'] != None:
		return session.query(User).filter(User.id == login_session['user_id']).one()
	else:
		return None

def matchesLoginUser(user):
	if 'user_id' in login_session and login_session['user_id'] == user.id:
		return True
	else:
		return False