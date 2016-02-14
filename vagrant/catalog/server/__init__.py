from flask import Flask
flask = Flask(__name__)
dbPath = 'postgresql://catalog:catalog@localhost:5432/catalog'

import server.views
