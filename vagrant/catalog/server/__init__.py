from flask import Flask
flask = Flask(__name__)
dbPath = 'sqlite:///catalog.db'

import server.views
