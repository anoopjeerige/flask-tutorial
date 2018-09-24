import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    """
    Function returns a new or existing db connection
    """
    # Check if db connection exists
    if 'db' not in g:
        # New db connection
        g.db = sqlite3.connect(
            # Get DATABASE configuration key
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Set returned rows to behave as dicts
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """
    Checks if an connection was created and closes it
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    """
    Initialize the database
    Clear existing data and create new tables.
    """
    # Get the db connection
    db = get_db()

    # Read the schema queries and execute them
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """
    Command line comand to invoke the init_db method,
    and show user the success message.
    """
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    """
    Register functions with application.
    """
    # Inform flask application to call close_db()
    # function when cleaning up after returning response
    app.teardown_appcontext(close_db)

    # Add the db initialization command to be called with flask
    app.cli.add_command(init_db_command)
