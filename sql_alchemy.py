"""
Database configuration module.

This module defines the global SQLAlchemy instance used across
the application. The instance is initialized without an app
context and later bound to the Flask application within the
main configuration module.
"""

from flask_sqlalchemy import SQLAlchemy


# ---------------------------------------------------------------------
# Global Database Instance
# ---------------------------------------------------------------------

banco = SQLAlchemy()
"""
Global SQLAlchemy instance.

This object is shared across the entire application and is
initialized with the Flask application using the `init_app`
method during application setup.
"""