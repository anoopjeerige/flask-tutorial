import os

from flask import Flask


def create_app(test_config=None):
    """
    A application factory function to create, set and return a flask instance.
    """

    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'))

    print(app.config["DATABASE"])
    if test_config is None:
        # Load the instance config, if it exits, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page
    @app.route('/hello')
    def hello():
        return "Hello, Hang in there."

    # Import and Register db functions with app
    from . import db
    db.init_app(app)

    # Import and register blueprints with app
    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)

    # Associated endpoint 'index' with '/',
    # so url_for('index') and url_for('blog.index') both generate '/' url
    app.add_url_rule('/', endpoint='index')

    return app
