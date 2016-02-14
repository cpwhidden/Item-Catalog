from server import flask
from flask_apscheduler import APScheduler
import sys
import logging
logging.basicConfig(stream=sys.stderr)

flask.secret_key = 'qPHE[Cht}*kSCVango3i'
flask.config['WHOOSH_BASE'] = 'server/whoosh'
flask.config['PRODUCT_IMAGES_FOLDER'] = 'server/static/product_images/'
flask.config['JOBS'] = [
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
flask.config['SCHEDULER_VIEWS_ENABLED'] = True
flask.debug = True

scheduler = APScheduler()
scheduler.init_app(flask)
scheduler.start()

if __name__ == '__main__':
    flask.run(host = '0.0.0.0', port = 8000)