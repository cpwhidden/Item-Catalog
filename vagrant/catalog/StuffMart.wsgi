activate_this = '/var/www/html/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys, os, logging
from flask_apscheduler import APScheduler
sys.path.insert(0, 'var/www/html/StuffMart/vagrant/catalog')
logging.basicConfig(stream=sys.stderr)

from server import flask as application
application.secret_key = 'qPHE[Cht}*kSCVango3i'
application.config['APP_DIR'] = os.path.abspath(os.path.dirname(__file__))
application.config['WHOOSH_BASE'] = 'server/whoosh'
application.config['PRODUCT_IMAGES_FOLDER'] = 'vagrant/catalog/server/static/product_images/'
application.config['JOBS'] = [
        {
            'id': 'buildNewlyAddedRSSFeed',
            'func': 'server.views:buildNewlyAddedRSSFeed',
            'trigger': 'interval',
            'seconds': (60*60)
        },
        {
            'id': 'buildNewlyAddedAtomFeed',
            'func': 'server.views:buildNewlyAddedAtomFeed',
            'trigger': 'interval',
            'seconds': (60*60)
        },
        {
            'id': 'buildNewlyAddedRSSFeedAtStartup',
            'func': 'server.views:buildNewlyAddedRSSFeed'
        },
        {
            'id': 'buildNewlyAddedAtomFeedAtStartup',
            'func': 'server.views:buildNewlyAddedAtomFeed'
        }
    ]
application.config['SCHEDULER_VIEWS_ENABLED'] = True
application.debug = True

scheduler = APScheduler()
scheduler.init_app(application)
scheduler.start()