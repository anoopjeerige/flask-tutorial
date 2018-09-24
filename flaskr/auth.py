from flask import (
    Blueprint, request, url_for, redirect, flash, render_template, session, g
)
from flaskr.db import get_db
from werkzeug.security import generate_password_hash, check_password_hash

from functools import wraps


# Authentication blueprint for authentication view functions
bp = Blueprint('auth', __name__, url_prefix='/auth')


# Register view code - authentication function
@bp.route('/register', methods=('GET', 'POST'))
def register():
    # If post request then validate the input
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?',
            (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        # If no errors and not existing user, then add new user to db
        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                # Securely hash the password and store the hash
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        # Add any error messages
        flash(error)

    # return register template for a GET, or if validation error
    return render_template('auth/register.html')


# Login view code - authentication function
@bp.route('/login', methods=('GET', 'POST'))
def login():
    # If post request then validate the input
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute(
            'SELECT * FROM user WHERE username = ?',
            (username,)
        ).fetchone()
        error = None

        if not user:
            error = 'Username is incorrect.'
        elif not check_password_hash(user['password'], password):
            error = 'Password is incorrect.'

        if error is None:
            # Add the user to the session
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


# Register a logged user check from session, runs before the view function
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None

    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?',
            (user_id,)
        ).fetchone()

# Logout view code - authentication function


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# Creating, editing, and deleting a blog post will require a user to be logged in.
# A decorator can be used to check for each view this is applied to
def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        # Check is user is logged in
        if g.user is None:
            # User not logged in, redirect to login view
            return redirect(url_for('auth.login'))
        # User is logged in, return original view to which the decorator is
        # applied to
        return view(*args, **kwargs)

    return wrapped_view
