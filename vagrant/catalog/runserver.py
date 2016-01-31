from server import flask


flask.secret_key = 'qPHE[Cht}*kSCVango3i'
flask.config['WHOOSH_BASE'] = 'server/whoosh'
flask.config['PRODUCT_IMAGES_FOLDER'] = 'server/static/product_images/'
flask.debug = True
flask.run(host = '0.0.0.0', port = 8000)