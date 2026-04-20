"""
User resource module.

This module defines RESTful resources responsible for user
management, authentication, registration, logout, and
account confirmation workflows.
"""

from flask import jsonify, make_response, render_template
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, jwt_required, get_jwt

from models.user import UserModel
from backlist import BLACKLIST

import traceback


# ---------------------------------------------------------------------
# Request Parser Configuration
# ---------------------------------------------------------------------

atributos = reqparse.RequestParser()
"""
Request parser used to validate and extract user-related fields
from incoming HTTP requests.
"""

atributos.add_argument(
    'login',
    type=str,
    required=True,
    help="The field 'login' cannot be left blank."
)

atributos.add_argument(
    'senha',
    type=str,
    required=True,
    help="The field 'senha' cannot be left blank."
)

atributos.add_argument('email', type=str)
atributos.add_argument('ativado', type=bool)


# ---------------------------------------------------------------------
# User Resource
# ---------------------------------------------------------------------

class User(Resource):
    """
    Resource representing a single user entity.

    Provides authenticated access to retrieve and delete users.
    """

    @jwt_required()
    def get(self, user_id):
        """
        Retrieve a user by identifier.

        Parameters
        ----------
        user_id : int
            Unique identifier of the user.

        Returns
        -------
        dict
            JSON representation of the user if found.
        tuple
            Error message and HTTP 404 if not found.
        """
        user = UserModel.find_user(user_id)
        if user:
            return user.json()
        return {'message': "User not found."}, 404

    @jwt_required()
    def delete(self, user_id):
        """
        Delete a user by identifier.

        Parameters
        ----------
        user_id : int
            Unique identifier of the user.

        Returns
        -------
        tuple
            Success or error message with appropriate HTTP status code.
        """
        user = UserModel.find_user(user_id)
        if user:
            try:
                user.delete_user()
            except:
                return {"message": "An error occurred while deleting the user."}, 500
            return {'message': 'User deleted.'}, 200
        return {'message': 'User not found.'}, 404


# ---------------------------------------------------------------------
# User Registration Resource
# ---------------------------------------------------------------------

class UserRegister(Resource):
    """
    Resource responsible for user registration.

    Handles input validation, uniqueness checks, persistence,
    and confirmation email dispatch.
    """

    def post(self):
        """
        Register a new user.

        Returns
        -------
        tuple
            Success or error message with appropriate HTTP status code.
        """
        dados = atributos.parse_args()

        if (
            not dados.get('email') or
            dados.get('email').strip() == '' or
            '@' not in dados.get('email') or
            '.' not in dados.get('email')
        ):
            return {
                "message": "The field 'email' is not a valid email address or is empty."
            }, 400

        if UserModel.find_by_email(dados['email']):
            return {
                "message": "The email '{}' already exists.".format(dados['email'])
            }, 400

        if UserModel.find_by_login(dados['login']):
            return {
                "message": "The login '{}' already exists.".format(dados['login'])
            }, 400

        user = UserModel(**dados)
        user.ativado = False

        try:
            user.save_user()
            user.send_confirmation_email()
        except:
            user.delete_user()
            traceback.print_exc()
            return {"message": "An error occurred while creating the user."}, 500

        return {"message": "User created successfully."}, 201


# ---------------------------------------------------------------------
# User Login Resource
# ---------------------------------------------------------------------

class UserLogin(Resource):
    """
    Resource responsible for user authentication.

    Validates credentials and generates a JWT access token
    for activated accounts.
    """

    def post(self):
        """
        Authenticate a user and generate a JWT token.

        Returns
        -------
        tuple
            Access token and HTTP 200 if successful.
            Appropriate error message otherwise.
        """
        dados = atributos.parse_args()
        user = UserModel.find_by_login(dados['login'])

        if user and user.senha == dados['senha']:
            if user.ativado:
                token_de_acesso = create_access_token(identity=str(user.user_id))
                return {'access_token': token_de_acesso}, 200
            else:
                return {'message': 'User is not activated.'}, 403

        return {'message': 'The username or password is incorrect'}, 401


# ---------------------------------------------------------------------
# User Logout Resource
# ---------------------------------------------------------------------

class UserLogout(Resource):
    """
    Resource responsible for user logout.

    Invalidates the current JWT token by adding its identifier
    to the blacklist.
    """

    @jwt_required()
    def post(self):
        """
        Invalidate the current JWT token.

        Returns
        -------
        tuple
            Confirmation message with HTTP 200 status code.
        """
        jwt_id = get_jwt()['jti']
        BLACKLIST.add(jwt_id)
        return {'message': 'Successfully logged out.'}, 200


# ---------------------------------------------------------------------
# User Confirmation Resource
# ---------------------------------------------------------------------

class UserConfirm(Resource):
    """
    Resource responsible for account activation.

    Activates a user account after email confirmation.
    """

    @classmethod
    def get(cls, user_id):
        """
        Activate a user account.

        Parameters
        ----------
        user_id : int
            Unique identifier of the user.

        Returns
        -------
        Response
            HTML confirmation page or error message.
        """
        user = UserModel.find_user(user_id)

        if not user:
            return {'message': 'User not found.'}, 404

        user.ativado = True
        user.save_user()

        headers = {'Content-Type': 'text/html'}

        return make_response(
            render_template(
                'user_confirm.html',
                email=user.email,
                usuario=user.login
            ),
            200,
            headers
        )