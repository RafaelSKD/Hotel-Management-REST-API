"""
Hotel resource module.

This module defines RESTful resources responsible for hotel
management, including advanced filtering, pagination,
creation, update, and deletion operations.
"""

from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required

from models.hotel import HotelModel
from models.site import SiteModel
from resources.filtros import (
    normalize_path_params,
    consulta_sem_cidade,
    consulta_com_cidade,
    non_empty_str,
    positive_float,
    estrelas_float
)

import sqlite3


# ---------------------------------------------------------------------
# Query Parameter Parser Configuration
# ---------------------------------------------------------------------

path_params = reqparse.RequestParser()
"""
Request parser used to extract and validate query string
parameters for hotel filtering and pagination.
"""

path_params.add_argument('nome', type=str, location='args')
path_params.add_argument('estrelas_min', type=float, location='args')
path_params.add_argument('estrelas_max', type=float, location='args')
path_params.add_argument('diaria_min', type=float, location='args')
path_params.add_argument('diaria_max', type=float, location='args')
path_params.add_argument('cidade', type=str, location='args')
path_params.add_argument('limit', type=int, location='args')
path_params.add_argument('offset', type=int, location='args')


# ---------------------------------------------------------------------
# Hotels Collection Resource
# ---------------------------------------------------------------------

class Hoteis(Resource):
    """
    Resource representing the collection of hotels.

    Provides advanced filtering capabilities using query parameters,
    including star range, daily rate range, city filtering,
    pagination, and normalization of parameters.
    """

    def get(self):
        """
        Retrieve filtered and paginated hotel records.

        Returns
        -------
        dict
            A dictionary containing a list of filtered hotel entries.
        """
        connection = sqlite3.connect('instance/banco.db')
        cursor = connection.cursor()

        dados = path_params.parse_args()
        dados_validos = {
            chave: dados[chave]
            for chave in dados
            if dados[chave] is not None
        }

        parametros = normalize_path_params(**dados_validos)

        if not parametros.get('cidade'):
            tupla = tuple([
                parametros['estrelas_min'],
                parametros['estrelas_max'],
                parametros['diaria_min'],
                parametros['diaria_max'],
                parametros['limit'],
                parametros['offset']
            ])
            resultado = cursor.execute(consulta_sem_cidade, tupla)
        else:
            tupla = tuple([
                parametros['estrelas_min'],
                parametros['estrelas_max'],
                parametros['diaria_min'],
                parametros['diaria_max'],
                parametros['cidade'],
                parametros['limit'],
                parametros['offset']
            ])
            resultado = cursor.execute(consulta_com_cidade, tupla)

        hoteis = []

        for linha in resultado:
            hoteis.append({
                'hotel_id': linha[0],
                'nome': linha[1],
                'estrelas': linha[2],
                'diaria': linha[3],
                'cidade': linha[4],
                'site_id': linha[5]
            })

        connection.close()

        return {'hoteis': hoteis}


# ---------------------------------------------------------------------
# Single Hotel Resource
# ---------------------------------------------------------------------

class Hotel(Resource):
    """
    Resource representing a single hotel entity.

    Provides operations to retrieve, create, update,
    and delete hotels.
    """

    atributos = reqparse.RequestParser()
    """
    Request parser used to validate and extract hotel
    creation and update payload fields.
    """

    atributos.add_argument(
        'nome',
        type=non_empty_str,
        required=True,
        help="The field 'nome' cannot be left blank."
    )

    atributos.add_argument(
        'estrelas',
        type=estrelas_float,
        required=True,
        help="The field 'estrelas' cannot be left blank and must be 0-5."
    )

    atributos.add_argument(
        'diaria',
        type=positive_float,
        required=True,
        help="The field 'diaria' cannot be left blank and must be > 0."
    )

    atributos.add_argument(
        'cidade',
        type=non_empty_str,
        required=True,
        help="The field 'cidade' cannot be left blank."
    )

    atributos.add_argument(
        'site_id',
        type=int,
        required=True,
        help="Every hotel needs to be linked to a site."
    )

    def get(self, hotel_id):
        """
        Retrieve a hotel by its identifier.

        Parameters
        ----------
        hotel_id : str
            Unique identifier of the hotel.

        Returns
        -------
        dict
            JSON representation of the hotel if found.
        tuple
            Error message and HTTP 404 if not found.
        """
        hotel = HotelModel.find_hotel(hotel_id)

        if hotel:
            return hotel.json()

        return {'message': "Hotel not found."}, 404

    @jwt_required()
    def post(self, hotel_id):
        """
        Create a new hotel.

        Requires JWT authentication.

        Parameters
        ----------
        hotel_id : str
            Unique identifier for the hotel.

        Returns
        -------
        tuple
            JSON representation and HTTP 201 if successful.
            Error message otherwise.
        """
        if HotelModel.find_hotel(hotel_id):
            return {
                "message": "Hotel id '{}' already exists.".format(hotel_id)
            }, 400

        dados = Hotel.atributos.parse_args()
        hotel = HotelModel(hotel_id, **dados)

        if not SiteModel.find_site(dados.get('site_id')):
            return {
                "message": "The site_id '{}' does not exist.".format(
                    dados.get('site_id')
                )
            }, 400

        try:
            hotel.save_hotel()
        except:
            return {
                "message": "An error occurred while inserting the hotel."
            }, 500

        return hotel.json(), 201

    @jwt_required()
    def put(self, hotel_id):
        """
        Update an existing hotel or create it if it does not exist.

        Requires JWT authentication.

        Parameters
        ----------
        hotel_id : str
            Unique identifier of the hotel.

        Returns
        -------
        tuple
            Updated or created hotel representation with
            appropriate HTTP status code.
        """
        dados = Hotel.atributos.parse_args()

        hotel_encontrado = HotelModel.find_hotel(hotel_id)

        if hotel_encontrado:
            hotel_encontrado.update_hotel(**dados)

            try:
                hotel_encontrado.save_hotel()
            except:
                return {
                    "message": "An error occurred while updating the hotel."
                }, 500

            return hotel_encontrado.json(), 200

        hotel = HotelModel(hotel_id, **dados)

        try:
            hotel.save_hotel()
        except:
            return {
                "message": "An error occurred while inserting the hotel."
            }, 500

        return hotel.json(), 201

    @jwt_required()
    def delete(self, hotel_id):
        """
        Delete a hotel by its identifier.

        Requires JWT authentication.

        Parameters
        ----------
        hotel_id : str
            Unique identifier of the hotel.

        Returns
        -------
        tuple
            Success message and HTTP 200 if deleted.
            Error message otherwise.
        """
        hotel = HotelModel.find_hotel(hotel_id)

        if hotel:
            try:
                hotel.delete_hotel()
            except:
                return {
                    "message": "An error occurred while deleting the hotel."
                }, 500

            return {'message': 'Hotel deleted.'}, 200

        return {'message': 'Hotel not found.'}, 404