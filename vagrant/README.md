# StuffMart
You want stuff? Yeah, we got stuff.

This is a practice web application that provides functionality for an item catalog.

# Features
* Users can log in with Google or Facebook
* Users have a shopping cart to buy items in the catalog.
* Users can add products to the catalog to sell
* Users can upload images for their products.
* Front-end done with Bootstrap and includes pagination and carousels.
* Server side framework is Flask
* Google and Facebook logins are handled server-side
* DB-API is Flask-SQLAlchemy
* Offers RSS and Atom feeds
* RSS and Atom feeds are rebuilt as a scheduled task using Flask-APScheduler
* Server-side error handling
* Project built in a Vagrant virtual machine

# How to use
You will need [Vagrant](www.vagrantup.com) in order to use this project
1. Clone the repo
2. At the command line, navigate to the repo’s directory.
3. Fire up the virtual machine with `vagrant up`
4. Log into the virtual machine with `vagrant ssh`
5. Navigate to the server directory with `cd vagrant/catalog/`
6. Start the server with `python runserver.py`
7. Navigate in your browser to `http://localhost:8000`