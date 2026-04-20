"""
Site resource module.

This module defines RESTful resources responsible for managing
site entities within the application. It provides endpoints
for listing, retrieving, creating, and deleting sites.
"""

from flask_restful import Resource
from models.site import SiteModel


# ---------------------------------------------------------------------
# Sites Collection Resource
# ---------------------------------------------------------------------

class Sites(Resource):
    """
    Resource representing the collection of sites.

    Provides access to retrieve all registered sites.
    """

    def get(self):
        """
        Retrieve all sites.

        Returns
        -------
        dict
            A dictionary containing a list of all site representations.
        """
        return {'sites': [site.json() for site in SiteModel.query.all()]}


# ---------------------------------------------------------------------
# Single Site Resource
# ---------------------------------------------------------------------

class Site(Resource):
    """
    Resource representing a single site entity.

    Provides operations to retrieve, create, and delete
    a specific site identified by its URL.
    """

    def get(self, url):
        """
        Retrieve a site by its URL.

        Parameters
        ----------
        url : str
            The unique URL identifying the site.

        Returns
        -------
        dict
            JSON representation of the site if found.
        tuple
            Error message and HTTP 404 status code if not found.
        """
        site = SiteModel.find_site(url)
        if site:
            return site.json()
        return {'message': 'Site not found.'}, 404

    def post(self, url):
        """
        Create a new site.

        Parameters
        ----------
        url : str
            The unique URL identifying the site.

        Returns
        -------
        tuple
            JSON representation of the created site and HTTP 201
            if successful.
            Error message and appropriate HTTP status code otherwise.
        """
        if SiteModel.find_site(url):
            return {'message': "The site '{}' already exists.".format(url)}, 400

        site = SiteModel(url)

        try:
            site.save_site()
        except:
            return {'message': 'An error occurred while creating the site.'}, 500

        return site.json(), 201

    def delete(self, url):
        """
        Delete a site by its URL.

        Parameters
        ----------
        url : str
            The unique URL identifying the site.

        Returns
        -------
        dict
            Success message if deletion is successful.
        tuple
            Error message and appropriate HTTP status code if the
            site does not exist or deletion fails.
        """
        site = SiteModel.find_site(url)

        if site:
            try:
                site.delete_site()
            except:
                return {'message': 'An error occurred while deleting the site.'}, 500

            return {'message': 'Site deleted.'}

        return {'message': 'Site not found.'}, 404