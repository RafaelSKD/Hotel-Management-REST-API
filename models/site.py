"""
Site model module.

This module defines the SiteModel class responsible for handling
site persistence and its relationship with associated hotels
within the application.
"""

from sql_alchemy import banco


# ---------------------------------------------------------------------
# Site Model Definition
# ---------------------------------------------------------------------

class SiteModel(banco.Model):
    """
    Database model representing a booking site.

    A site aggregates multiple hotels and serves as a logical
    grouping entity within the system.
    """

    __tablename__ = 'site'
    """Name of the database table associated with this model."""

    site_id = banco.Column(banco.Integer, primary_key=True)
    url = banco.Column(banco.String(80))
    hoteis = banco.relationship('HotelModel')
    """
    Relationship linking the site to its associated hotels.

    This defines a one-to-many relationship between SiteModel
    and HotelModel.
    """

    def __init__(self, url):
        """
        Initialize a new SiteModel instance.

        Parameters
        ----------
        url : str
            The unique URL representing the site.
        """
        self.url = url

    def json(self):
        """
        Serialize the site object to a dictionary.

        Returns
        -------
        dict
            A dictionary representation of the site, including
            its associated hotels.
        """
        return {
            'site_id': self.site_id,
            'url': self.url,
            'hoteis': [hotel.json() for hotel in self.hoteis]
        }

    @classmethod
    def find_site(cls, url):
        """
        Retrieve a site by its URL.

        Parameters
        ----------
        url : str
            The site's URL.

        Returns
        -------
        SiteModel or None
            The matching site instance if found; otherwise, None.
        """
        site = cls.query.filter_by(url=url).first()
        if site:
            return site
        return None

    @classmethod
    def find_by_id(cls, site_id):
        """
        Retrieve a site by its unique identifier.

        Parameters
        ----------
        site_id : int
            The unique site identifier.

        Returns
        -------
        SiteModel or None
            The matching site instance if found; otherwise, None.
        """
        site = cls.query.filter_by(site_id=site_id).first()
        if site:
            return site
        return None

    def save_site(self):
        """
        Persist the current site instance to the database.

        Adds the instance to the session and commits the transaction.
        """
        banco.session.add(self)
        banco.session.commit()

    def delete_site(self):
        """
        Remove the site and its associated hotels from the database.

        All related hotels are deleted before removing the site
        itself to maintain referential integrity.
        """
        [hotel.delete_hotel() for hotel in self.hoteis]
        banco.session.delete(self)
        banco.session.commit()