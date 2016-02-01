# StuffMart
You want stuff? Yeah, we got stuff.

This is a practice web application that provides functionality for an item catalog.

# Features
* Users can log in with Google or Facebook
* Users have a shopping cart to buy items in the catalog.
* Users can add products to the catalog to sell
* Users can upload images for their products.
* Front-end done with Bootstrap and includes pagination and carousels.
* Forms are created with WTF-Forms, which do form validation and eliminate cross-site request forgery attacks.
* Server side framework is Flask
* Google and Facebook logins are handled server-side
* DB-API is Flask-SQLAlchemy
* Offers RESTful API in JSON format
* Offers RSS and Atom feeds
* RSS and Atom feeds are rebuilt as a scheduled task using Flask-APScheduler
* Server-side error handling
* Project built in a Vagrant virtual machine

# How to use
You will need [Vagrant](www.vagrantup.com) and [VirtualBox](www.virtualbox.org) in order to use this project
1. Clone the repo
2. At the command line, navigate to the repo’s directory.
3. Fire up the virtual machine with `vagrant up`
4. Log into the virtual machine with `vagrant ssh`
5. Navigate to the server directory with `cd /vagrant/catalog/`
6. Start the server with `python runserver.py`
7. Navigate in your browser to `http://localhost:8000`

# Populator
To populate the database with mock records:
1. Navigate to `cd /vagrant/catalog/` at the command line
2. Run `python populator.py`

# Access JSON endpoint
All JSON requests are HTTP GET requests. The base directory is the domain name. For example, `http://localhost:8000/categories/json` to request all categories
1. Get a list of all categories at `/categories/json`
2. Get a list of all products in a category at `/category/{category_id}/products/json`
3. Get detailed product information at `/product/{product_id}/json`
4. Get reviews for a specific product at `/product/{product_id}/reviews/json`

# RSS and Atom feeds
Get the “newly-added” RSS and Atom feeds at `/rss/newly-added.xml` and `/atom/newly-added.xml`

# Photo credits
A photos provided here are from [Pixabay](https://pixabay.com) and are under a Creative Commons license

# License
This project is provided under MIT License.
