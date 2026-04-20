"""
Hotel model module.

This module defines the HotelModel class responsible for handling
hotel persistence and its association with booking sites within
the application.
"""

from sql_alchemy import banco


# ---------------------------------------------------------------------
# Hotel Model Definition
# ---------------------------------------------------------------------

class HotelModel(banco.Model):
    """
    Database model representing a hotel entity.

    Each hotel belongs to a specific site and contains
    descriptive and pricing information.
    """

    __tablename__ = 'hoteis'
    """Name of the database table associated with this model."""

    hotel_id = banco.Column(banco.String(80), primary_key=True)
    nome = banco.Column(banco.String(80))
    estrelas = banco.Column(banco.Float(precision=1))
    diaria = banco.Column(banco.Float(precision=2))
    cidade = banco.Column(banco.String(40))
    site_id = banco.Column(banco.Integer, banco.ForeignKey('site.site_id'))
    """
    Foreign key linking the hotel to a SiteModel instance.
    """

    def __init__(self, hotel_id, nome, estrelas, diaria, cidade, site_id):
        """
        Initialize a new HotelModel instance.

        Parameters
        ----------
        hotel_id : str
            Unique identifier for the hotel.
        nome : str
            Name of the hotel.
        estrelas : float
            Star rating of the hotel.
        diaria : float
            Daily rate of the hotel.
        cidade : str
            City where the hotel is located.
        site_id : int
            Identifier of the associated site.
        """
        self.hotel_id = hotel_id
        self.nome = nome
        self.estrelas = estrelas
        self.diaria = diaria
        self.cidade = cidade
        self.site_id = site_id

    def json(self):
        """
        Serialize the hotel object to a dictionary.

        Returns
        -------
        dict
            A dictionary representation of the hotel instance.
        """
        return {
            'hotel_id': self.hotel_id,
            'nome': self.nome,
            'estrelas': self.estrelas,
            'diaria': self.diaria,
            'cidade': self.cidade,
            'site_id': self.site_id
        }

    @classmethod
    def find_hotel(cls, hotel_id):
        """
        Retrieve a hotel by its unique identifier.

        Parameters
        ----------
        hotel_id : str
            The unique hotel identifier.

        Returns
        -------
        HotelModel or None
            The matching hotel instance if found; otherwise, None.
        """
        hotel = cls.query.filter_by(hotel_id=hotel_id).first()
        if hotel:
            return hotel
        return None

    def save_hotel(self):
        """
        Persist the current hotel instance to the database.

        Adds the instance to the session and commits the transaction.
        """
        banco.session.add(self)
        banco.session.commit()

    def update_hotel(self, nome, estrelas, diaria, cidade):
        """
        Update hotel attributes.

        Parameters
        ----------
        nome : str
            Updated hotel name.
        estrelas : float
            Updated star rating.
        diaria : float
            Updated daily rate.
        cidade : str
            Updated city location.
        """
        self.nome = nome
        self.estrelas = estrelas
        self.diaria = diaria
        self.cidade = cidade

    def delete_hotel(self):
        """
        Remove the hotel instance from the database.

        Deletes the instance from the session and commits
        the transaction.
        """
        banco.session.delete(self)
        banco.session.commit()