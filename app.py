"""
Main application module.

This module configures and initializes the Flask application,
database connection, JWT authentication system, and API resources
for the hotel and site simulation project.
"""

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from backlist import BLACKLIST
from sql_alchemy import banco


# ---------------------------------------------------------------------
# Application Setup
# ---------------------------------------------------------------------

app = Flask(__name__)
"""Flask application instance."""

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
"""Database connection string (SQLite local database)."""

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
"""Disable SQLAlchemy modification tracking for performance optimization."""

app.config['JWT_SECRET_KEY'] = 'panados'
"""Secret key used to sign and validate JWT tokens."""


# ---------------------------------------------------------------------
# Extensions Initialization
# ---------------------------------------------------------------------

banco.init_app(app)
"""Bind SQLAlchemy instance to the Flask application."""

api = Api(app)
"""Flask-RESTful API instance."""

jwt = JWTManager(app)
"""JWT manager responsible for authentication and token handling."""


# ---------------------------------------------------------------------
# Database Initialization
# ---------------------------------------------------------------------

def cria_banco():
    """
    Create all database tables.

    This function initializes the database schema based on
    the defined SQLAlchemy models. It must be executed within
    the Flask application context.
    """
    banco.create_all()


# ---------------------------------------------------------------------
# JWT Configuration
# ---------------------------------------------------------------------

@jwt.token_in_blocklist_loader
def verifica_blacklist(jwt_header, jwt_payload):
    """
    Determine whether a JWT token has been revoked.

    Parameters
    ----------
    jwt_header : dict
        The decoded header of the JWT.
    jwt_payload : dict
        The decoded payload of the JWT.

    Returns
    -------
    bool
        True if the token identifier (jti) exists in the blacklist;
        otherwise, False.
    """
    return jwt_payload['jti'] in BLACKLIST


@jwt.revoked_token_loader
def token_de_acesso_invalidado(jwt_header, jwt_payload):
    """
    Handle requests made with a revoked JWT token.

    Parameters
    ----------
    jwt_header : dict
        The decoded header of the JWT.
    jwt_payload : dict
        The decoded payload of the JWT.

    Returns
    -------
    tuple
        A JSON response with HTTP status code 401 indicating
        that the user has been logged out.
    """
    return jsonify({'message': 'You have been logged out.'}), 401


# ---------------------------------------------------------------------
# Resource Imports
# ---------------------------------------------------------------------
# Imported after API initialization to prevent circular dependencies.

from resources.hotel import Hoteis, Hotel
from resources.user import User, UserRegister, UserLogin, UserLogout, UserConfirm
from resources.site import Site, Sites


# ---------------------------------------------------------------------
# API Resource Registration
# ---------------------------------------------------------------------

api.add_resource(Hoteis, "/hoteis")
api.add_resource(Hotel, "/hoteis/<string:hotel_id>")

api.add_resource(User, "/users/<string:user_id>")
api.add_resource(UserRegister, "/cadastro")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(Sites, "/sites")
api.add_resource(Site, "/sites/<string:url>")
api.add_resource(UserConfirm, "/confirmacao/<int:user_id>")


# ---------------------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------------------

if __name__ == "__main__":
    """
    Application execution entry point.

    Ensures the database schema is created before starting
    the development server.
    """
    with app.app_context():
        cria_banco()

    app.run(debug=True)