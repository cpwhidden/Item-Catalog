from server import flask, dbPath
from server.models import Base, Category, Product, ProductForm
from server.models import User, UserForm, Review, ReviewForm, ShoppingCart
from sqlalchemy import create_engine, desc, func
from sqlalchemy.orm import sessionmaker
from flask import url_for, render_template, session as login_session
from flask import redirect, request, make_response, jsonify, flash
from flask_wtf import Form
from werkzeug import secure_filename
from apiclient import discovery
from oauth2client import client
import os, datetime, json, random, string, requests, httplib2, re
import jinja2

# Initiate SQLAlchemy engine
engine = create_engine(dbPath)
Base.metadata.bind = engine
session = sessionmaker(engine)()


@flask.route('/')
@flask.route('/home')
def home():
	highestRated = session.query(Product.id, Product.name, Product.price, 
		Product.imageName, func.avg(Review.rating).label('averageRating')) \
		.join(Review, Product.id == Review.product_id).group_by(Product.id) \
		.order_by(desc(func.avg(Review.rating))).limit(5).all()
	newlyAdded = session.query(Product).order_by(desc(Product.dateAdded)) \
		.limit(5).all()
	currentUser = getCurrentUser()
	return render_template('home.html', highestRated = highestRated, 
		newlyAdded = newlyAdded)


#
#	Login, logout procedures
#

# Only needed to login as user from populator.py
# For testing purposes only
@flask.route('/login')
def login():
	user = session.query(User).filter(User.id == 0, User.oauth_id == 0).first()
	login_session['user_id'] = user.id
	return redirect(url_for('home'))


@flask.route('/logout')
def logout():
	if 'login_type' in login_session:
		if login_session['login_type'] == 'google':
			return googleLogout()
		elif login_session['login_type'] == 'facebook':
			return facebookLogout()
	# Make sure login_session variables are deleted just in case
	if 'user_id' in login_session:
		del login_session['user_id']
	if 'google_access_token' in login_session:
		del login_session['google_access_token']
	if 'facebook_access_token' in login_session:
		del login_session['facebook_access_token']
	if 'login_type' in login_session:
		del login_session['login_type']
	return redirect(url_for('home'))


@flask.route('/google-login', methods=['POST'])
def googleLogin():
	# Verify state token
	if request.args.get('google_state_token') != \
			login_session['google_state_token']:
		return makeJSONResponse('Invalid state token', 401)
	authorizationCode = request.data

	# Get credentials
	CLIENT_SECRET_FILE = getGoogleClientSecret()
	try:
		credentials = client.credentials_from_clientsecrets_and_code(
			CLIENT_SECRET_FILE,
				['https://www.googleapis.com/auth/drive.appdata', 
				'profile', 'email'],
    authorizationCode)
	except client.FlowExchangeError:
		return makeJSONResponse('Failed to exchange authorization code', 401)
	http_auth = credentials.authorize(httplib2.Http())
	drive_service = discovery.build('drive', 'v3', http=http_auth)
	appfolder = drive_service.files().get(fileId='appfolder').execute

	# Get user info
	oauth_id = credentials.id_token['sub']
	email = credentials.id_token['email']
	url = 'https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token=%s' \
		% credentials.access_token
	response = requests.get(url)
	data = json.loads(response.text)
	name = data['name']

	# Check if user already exists
	matchingUser = session.query(User).filter(User.oauth_id == oauth_id) \
		.first()
	if matchingUser is None:
		newUser = User(oauth_id = oauth_id, name = name, email = email)
		session.add(newUser)
		session.commit()
		login_session['user_id'] = newUser.id
	else:
		login_session['user_id'] = matchingUser.id
	login_session['login_type'] = 'google'
	login_session['google_access_token'] = credentials.access_token
	return makeJSONResponse('Logged in through Google', 200)


@flask.route('/google-logout', methods=['POST'])
def googleLogout():
	if 'google_access_token' in login_session and \
			login_session['google_access_token'] is not None:
		url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
			% login_session['google_access_token']
		h = httplib2.Http()
		result = h.request(url, 'GET')[0]
		if result['status'] == '200':
			del login_session['user_id']
			del login_session['google_access_token']
			del login_session['login_type']
			return redirect(url_for('home'))
		else:
			if 'user_id' in login_session:
				del login_session['user_id']
			if 'google_access_token' in login_session:
				del login_session['google_access_token']
			if 'login_type' in login_session:
				del login_session['login_type']
			return makeJSONResponse(
				'Failure to log out of Google. (Failure to revoke token)', 400)
	else:
		return makeJSONResponse('User was not connected', 401)


@flask.route('/facebook-login', methods=['POST'])
def facebookLogin():
	# Verify state token
	if request.args.get('facebook_state_token') != \
			login_session['facebook_state_token']:
		return makeJSONResponse('Invalid state token', 401)
	access_token = request.data

	clientSecretsJSON = json.loads(open(getFacebookClientSecrets(), 'r')
		.read())
	app_id = clientSecretsJSON['web']['app_id']
	app_secret = clientSecretsJSON['web']['app_secret']
	exchangeURL = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' \
		% (app_id, app_secret, access_token)
	exchangeResult = httplib2.Http().request(exchangeURL, 'GET')[1]
	token = exchangeResult.split('&')[0]
	infoURL = 'https://graph.facebook.com/v2.2/me?%s&fields=name,id,email' \
		 % token
	infoResult = httplib2.Http().request(infoURL, 'GET')[1]
	data = json.loads(infoResult)
	oauth_id = data['id']

	# Check if user already exists
	matchingUser = session.query(User).filter(User.oauth_id == oauth_id) \
		.first()
	if matchingUser is None:
		newUser = User(oauth_id = oauth_id, name = data['name'], 
			email = data['email'])
		session.add(newUser)
		session.commit()
		login_session['user_id'] = newUser.id
	else:
		login_session['user_id'] = matchingUser.id
	login_session['login_type'] = 'facebook'
	login_session['facebook_access_token'] = access_token
	return makeJSONResponse('Logged in through Facebook', 200)


@flask.route('/facebook-logout', methods=['POST'])
def facebookLogout():
	user = getCurrentUser()
	if user is not None:
		oauth_id = user.oauth_id
		url = 'https://graph.facebook.com/%s/permissions?access_token=%s' \
			% (oauth_id, login_session['facebook_access_token'])
		h = httplib2.Http()
		result = h.request(url, 'DELETE')[0]
		if result['status'] == '200':
			del login_session['user_id']
			del login_session['facebook_access_token']
			del login_session['login_type']
			return redirect(url_for('home'))
		else:
			if 'user_id' in login_session:
				del login_session['user_id']
			if 'facebook_access_token' in login_session:
				del login_session['facebook_access_token']
			if 'login_type' in login_session:
				del login_session['login_type']
			return makeJSONResponse(
				'Failure to log out of Facebook. (Failure to delete permission)'
					, 400)
	else:
		return makeJSONResponse('User was not connected to Facebook', 401)


#
#	Shopping cart
#


@flask.route('/shopping-cart')
def shoppingCart():
	user = getCurrentUser()
	# Only logged in users can access shopping cart
	if user is not None:
		shoppingCart = session.query(Product.id, Product.name, Product.imageName, 
			Product.price, ShoppingCart.quantity) \
			.join(ShoppingCart, Product.id == ShoppingCart.product_id) \
			.join(User, User.id == ShoppingCart.buyer_id) \
			.filter(ShoppingCart.buyer_id == user.id)
		products = shoppingCart.all()
		count = session.query(func.sum(ShoppingCart.quantity)) \
			.filter(ShoppingCart.buyer_id == user.id).one()[0]
		totalQuery = session.query(
			func.sum(Product.price * ShoppingCart.quantity)) \
			.join(ShoppingCart, Product.id == ShoppingCart.product_id) \
			.join(User, User.id == ShoppingCart.buyer_id) \
			.filter(ShoppingCart.buyer_id == user.id).one()[0]
		total = '0.00'
		if totalQuery is not None:
			total = '%0.2f' % totalQuery
		return render_template('shopping-cart.html', user = user, 
			products = products, count = count, total = total)
	else:
		return redirect(url_for('home'))


@flask.route('/product/<int:product_id>/add-to-cart')
def addToCart(product_id):
	currentUser = getCurrentUser()
	# Only logged in users can add to cart
	if currentUser is not None:
		existingRecord = session.query(ShoppingCart) \
			.join(User, User.id == ShoppingCart.buyer_id) \
			.filter(ShoppingCart.product_id == product_id, \
				User.id == currentUser.id).first()
		if existingRecord is not None:
			existingRecord.quantity += 1
			session.add(existingRecord)
		else:
			product = session.query(Product) \
				.filter(Product.id == product_id).one()
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
	if currentUser is not None:
		shoppingRecord = session.query(ShoppingCart) \
			.filter(ShoppingCart.product_id == product_id, \
				ShoppingCart.buyer_id == currentUser.id).one()
		session.delete(shoppingRecord)
		session.commit()
		return redirect(url_for('shoppingCart'))
	else:
		return redirect(url_for('home'))


#
#	Search
#

@flask.route('/search')
def search():
	query = request.args.get('query')
	query = re.sub(r'[^\w]', '', query)
	if query == '':
		return redirect(url_for('home'))
	else:
		currentPage = request.args.get('page')
		if currentPage is None:
			currentPage = 1
		return redirect(url_for('searchPage', query = query, 
			currentPage = currentPage))


@flask.route('/search/<string:query>/page/<int:currentPage>')
def searchPage(query, currentPage):
	resultsPerPage = 10
	currentUser = getCurrentUser()
	offset = resultsPerPage * (currentPage - 1)
	totalPages = (session.query(Product)
		.filter(Product.name.contains(query))
		.count() - 1) / resultsPerPage + 1
	if totalPages > 0:
		if currentPage > totalPages:
			return redirect(url_for('searchPage', query = query, 
				currentPage = totalPages))
		if currentPage < 1:
			return redirect(url_for('searchPage', query = query, 
				currentPage = 1))
	products = session.query(Product) \
		.filter(Product.name.contains(query)) \
		.offset(offset).limit(resultsPerPage).all()
	pages = [(i+1) for i in range(totalPages)]
	return render_template('search.html', query = query, 
		currentPage = currentPage, pages= pages, totalPages = totalPages, 
		currentUser = currentUser, products = products)


#
#	Browsing by category
#

@flask.route('/category/<string:category_name>')
def category(category_name):
	return redirect(url_for('categoryPage', 
		category_name = category_name, currentPage = 1))


@flask.route('/category/<string:category_name>/<int:currentPage>')
def categoryPage(category_name, currentPage):
	# Display only a certain number of items per page
	resultsPerPage = 5
	offset = resultsPerPage * (currentPage - 1)
	currentUser = getCurrentUser()
	currentCategory = session.query(Category) \
		.filter(Category.name == category_name).one()
	totalPages = (session.query(Product) \
		.filter(Product.category == currentCategory) \
		.count() - 1) / resultsPerPage + 1
	pages = [(i+1) for i in range(totalPages)]
	if totalPages > 0:
		if currentPage > totalPages:
			return redirect(url_for('categoryPage', 
				category_name = category_name, currentPage = totalPages))
		if currentPage < 1:
			return redirect(url_for('categoryPage', 
				category_name = category_name, currentPage = 1))
	categories = session.query(Category).all()
	highestRated = session.query(Product.id, Product.name, 
		Product.imageName, Product.price, \
		func.avg(Review.rating).label('averageRating')) \
		.join(Review, Product.id == Review.product_id) \
		.filter(Product.category == currentCategory) \
		.group_by(Product.id).order_by(desc(func.avg(Review.rating))) \
		.limit(5).all()
	newlyAdded = session.query(Product) \
		.filter(Product.category == currentCategory) \
		.order_by(desc(Product.dateAdded)).limit(5).all()
	products = session.query(Product) \
		.filter(Product.category == currentCategory) \
		.offset(offset).limit(resultsPerPage).all()
	return render_template('category.html', categories = categories, 
		currentPage = currentPage, pages = pages, totalPages = totalPages, 
		currentCategory = currentCategory, products = products, 
		highestRated = highestRated, newlyAdded = newlyAdded, 
		currentUser = currentUser)


#
#	User profile
#

@flask.route('/user/<int:user_id>/profile')
def userProfile(user_id):
	user = session.query(User).filter(User.id == user_id).one()
	# Only display profile if user is current user
	if matchesLoginUser(user):
		products = session.query(Product).filter(Product.seller == user).all()
		reviews = session.query(Review).filter(Review.user == user).all()
		return render_template('user-profile.html', currentUser = user, 
			user = user, products = products, reviews = reviews)
	else:
		return redirect(url_for('home'))


@flask.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
def editUser(user_id):
	user = session.query(User).filter(User.id == user_id).one()
	# Only allow current user to edit own profile
	if matchesLoginUser(user):
		form = UserForm(request.form, user)
		if form.validate_on_submit():
			form.populate_obj(user)
			session.add(user)
			session.commit()
			return redirect(url_for('userProfile', user_id = user_id))
		else:
			return render_template('edit-user.html', currentUser = user, 
				form = form, user = user)
	else:
		return redirect(render_template('home'))


@flask.route('/user/<int:user_id>/profile/delete', methods=['GET', 'POST'])
def deleteUser(user_id):
	user = session.query(User).filter(User.id == user_id).one()
	# Only delete user if it matches the current user
	if matchesLoginUser(user):
		products = session.query(Product).filter(Product.seller == user).all()
		form = Form()
		if form.validate_on_submit():
			session.delete(user)
			if 'user_id' in login_session:
				del login_session['user_id']
			session.commit()
			return redirect(url_for('home'))
		else:
			return render_template('delete-user.html', currentUser = user, 
				form = form, user = user, products = products)
	else:
		return redirect(render_template('home'))


#
#	Product
#


@flask.route('/product/<int:product_id>/profile')
def product(product_id):
	product = session.query(Product).filter(Product.id == product_id).one()
	reviews = session.query(Review).filter(Review.product == product).all()
	ratingQuery = session.query(func.avg(Review.rating)) \
		.join(Product, Product.id == Review.product_id).one()[0]
	rating = ''
	if ratingQuery is not None:
		rating = '%0.1f' % ratingQuery
	currentUser = getCurrentUser()
	isOwner = matchesLoginUser(product.seller)
	return render_template('product.html', currentUser= currentUser, 
		isOwner = isOwner, product = product, reviews = reviews, 
		rating = rating)


@flask.route('/product/new', methods=['GET', 'POST'])
def newProduct():
	user = getCurrentUser()
	# Only logged in users can add a product
	if user is not None:
		categories = session.query(Category).order_by(Category.name).all()
		form = ProductForm(request.form)
		form.category_id.choices = \
			[(category.id, category.name) for category in categories]
		if form.validate_on_submit():
			product = Product()
			form.populate_obj(product)
			if 'image' in request.files and \
					request.files['image'].filename != '':
				image = request.files['image']
				product.imageName = secure_filename(image.filename)
				productImagesPath = flask.config['APP_DIR'] 
				path = os.path.join(productImagesPath, 'server/static/product_images/' + product.imageName)
				image.save(path)
			product.seller = user
			try:
				session.add(product)
				session.commit()
			except:
				session.rollback()
				return 'Failed to add record. Please make sure to pick a unique name.'
			return redirect(url_for('userProfile', user_id = user.id))
		else:
			return render_template('new-product.html', currentUser = user, 
				form = form)
	else:
		return redirect(url_for('home'))


@flask.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
def editProduct(product_id):
	currentUser = getCurrentUser()
	product = session.query(Product).filter(Product.id == product_id).one()
	# Only allow product edit if the seller is the current user
	if matchesLoginUser(product.seller):
		form = ProductForm(request.form, product)
		categories = session.query(Category).all()
		form.category_id.choices = [(category.id, category.name) for category in categories]
		if form.validate_on_submit():
			form.populate_obj(product)
			if 'image' in request.files and \
					request.files['image'].filename != '':
				image = request.files['image']
				product.imageName = secure_filename(image.filename)
				productImagesPath = flask.config['PRODUCT_IMAGES_FOLDER']
				path = os.path.join(productImagesPath, product.imageName)
				image.save(path)
			try:
				session.add(product)
				session.commit()
			except:
				session.rollback()
				return 'Failed to edit record. Please make sure to pick a unique name.'
			return redirect(url_for('userProfile', 
				user_id = product.seller.id))
		else:
			return render_template('edit-product.html', 
				currentUser = currentUser, form = form, product = product)
	else:
		return redirect(url_for('home'))


@flask.route('/product/<int:product_id>/remove', methods=['GET', 'POST'])
def deleteProduct(product_id):
	currentUser = getCurrentUser()
	product = session.query(Product).filter(Product.id == product_id).one()
	# Only all product deletion if the seller is the current user
	if matchesLoginUser(product.seller):
		form = Form()
		if form.validate_on_submit():
			session.delete(product)
			session.commit()
			return redirect(url_for('userProfile', 
				user_id = product.seller.id))
		else:
			return render_template('delete-product.html', 
				currentUser = currentUser, form = form, product = product)
	else:
		return redirect(url_for('home'))


#
#	Reviews
#

@flask.route('/product/<int:product_id>/review/add', methods=['GET', 'POST'])
def addReview(product_id):
	currentUser = getCurrentUser()
	product = session.query(Product).filter(Product.id == product_id).one()
	# Only allow logged in users to add a review
	if currentUser is not None:
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
			return render_template('add-review.html', 
				currentUser = currentUser, form = form, product = product)
	else:
		return redirect(url_for('product', product_id = product_id))


@flask.route('/product/<int:product_id>/review/<int:review_id>/edit', 
	methods=['GET', 'POST'])
def editReview(product_id, review_id):
	currentUser = getCurrentUser()
	product = session.query(Product).filter(Product.id == product_id).one()
	review = session.query(Review).filter(Review.id == review_id).one()
	# Only allow review edits if reviewer is the current user
	if matchesLoginUser(review.user):
		form = ReviewForm(request.form, review)
		if form.validate_on_submit():
			form.populate_obj(review)
			session.add(review)
			session.commit()
			return redirect(url_for('product', product_id = product_id))
		else:
			return render_template('edit-review.html', 
				currentUser = currentUser, form = form, product = product, review = review)
	else:
		return redirect(url_for('home'))


@flask.route('/product/<int:product_id>/review/<int:review_id>/remove', 
	methods=['GET', 'POST'])
def deleteReview(product_id, review_id):
	currentUser = getCurrentUser()
	product = session.query(Product).filter(Product.id == product_id).one()
	review = session.query(Review).filter(Review.id == review_id).one()
	# Only allow review deletion if reviers is the current user
	if matchesLoginUser(review.user):
		form = Form()
		if form.validate_on_submit():
			session.delete(review)
			session.commit()
			return redirect(url_for('product', product_id = product_id))
		else:
			return render_template('delete-review.html', 
				currentUser = currentUser, form = form, product = product, 
				review= review)
	else:
		return redirect(url_for('home'))


# 
#	JSON routes
#

@flask.route('/categories/json')
def categoriesJSON():
	categories = session.query(Category).all()
	return jsonify(Category=[c.serialize for c in categories])


@flask.route('/category/<int:category_id>/products/json')
def productsInCategory(category_id):
	products = session.query(Product) \
		.filter(Product.category_id == category_id).all()
	return jsonify(Product=[p.serialize for p in products])


@flask.route('/product/<int:product_id>/json')
def productJSON(product_id):
	product = session.query(Product) \
		.filter(Product.id == product_id).one()
	return jsonify(Product=product.serialize)


@flask.route('/product/<int:product_id>/reviews/json')
def reviewsForProduct(product_id):
	reviews = session.query(Review) \
		.filter(Review.product_id == product_id).all()
	return jsonify(Review=[r.serialize for r in reviews])


#
#	RSS rebuild task and endpoint
#

def render_without_request(template_name, **template_vars):
    """
    Usage is the same as flask.render_template:

    render_without_request('my_template.html', var1='foo', var2='bar')
    """
    env = jinja2.Environment(
        loader=jinja2.PackageLoader('server','templates')
    )
    template = env.get_template(template_name)
    return template.render(**template_vars)


def buildNewlyAddedRSSFeed():
	engine = create_engine(dbPath)
	Base.metadata.bind = engine
	session = sessionmaker(engine)()
	buildDateTime = datetime.datetime.now()
	products = session.query(Product).order_by(desc(Product.dateAdded)) \
		.limit(20).all()
	xml = render_without_request('newly-added-rss-template.xml', 
		buildDateTime = buildDateTime, products = products)
	with open('server/static/rss/newly-added.xml', 'w') as rss_file:
	    rss_file.write(xml)


@flask.route('/rss/newly-added.xml')
def newlyAddedRSSFeed():
	with open('server/static/rss/newly-added.xml', 'r') as rss_file:
		content = rss_file.read()
	response = make_response(content)
	response.headers['Content-Type'] = 'text/xml'
	return response


def buildNewlyAddedAtomFeed():
	engine = create_engine(dbPath)
	Base.metadata.bind = engine
	session = sessionmaker(engine)()
	buildDateTime = datetime.datetime.now()
	products = session.query(Product).order_by(desc(Product.dateAdded)) \
		.limit(20).all()
	xml = render_without_request('newly-added-atom-template.xml', 
		buildDateTime = buildDateTime, products = products)
	with open('server/static/atom/newly-added.xml', 'w') as atom_file:
	    atom_file.write(xml)


@flask.route('/atom/newly-added.xml')
def newlyAddedAtomFeed():
	with open('server/static/atom/newly-added.xml', 'r') as atom_file:
	    content = atom_file.read()
	response = make_response(content)
	response.headers['Content-Type'] = 'text/xml'
	return response


#
#	Utility functions for templates
#

@flask.context_processor
def utility_processor():
	def getCategories():
		return session.query(Category).order_by(Category.name).all()
	def queryCurrentUser():
		return getCurrentUser()
	def indices(array):
		return [i for i in range(len(array))]
	def generateStateToken(type):
		state_token = ''.join(random.choice(
			string.ascii_uppercase + string.digits) for x in xrange(32))
		login_session[type + '_state_token'] = state_token
		return state_token
	return dict(getCategories = getCategories, 
		queryCurrentUser = queryCurrentUser, indices = indices, 
		generateStateToken = generateStateToken)


# Utility functions

def makeJSONResponse(message, status):
	response = make_response(json.dumps(message), status)
	response.headers['Content-Type'] = 'application/json'
	return response


def getGoogleClientSecret():
	return os.path.join(flask.config['APP_DIR'], 'server/static/google_client_secrets.json')


def getFacebookClientSecrets():
	return os.path.join(flask.config['APP_DIR'], 'server/static/facebook_client_secrets.json')


def getCurrentUser():
	if 'user_id' in login_session and login_session['user_id'] is not None:
		return session.query(User) \
			.filter(User.id == login_session['user_id']).first()
	else:
		return None


def matchesLoginUser(user):
	if 'user_id' in login_session and login_session['user_id'] == user.id:
		return True
	else:
		return False