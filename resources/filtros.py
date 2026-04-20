"""
Filtering and validation utilities module.

This module provides helper functions and SQL query templates
used for hotel filtering, pagination, and input validation
within the application.
"""


# ---------------------------------------------------------------------
# Query Parameter Normalization
# ---------------------------------------------------------------------

def normalize_path_params(
    cidade=None,
    estrelas_min=0,
    estrelas_max=5,
    diaria_min=0,
    diaria_max=10000,
    limit=50,
    offset=0,
    **dados
):
    """
    Normalize and structure query string parameters.

    Applies default values to missing filtering parameters
    and returns a dictionary formatted for SQL query execution.

    Parameters
    ----------
    cidade : str, optional
        City filter.
    estrelas_min : float, optional
        Minimum star rating.
    estrelas_max : float, optional
        Maximum star rating.
    diaria_min : float, optional
        Minimum daily rate.
    diaria_max : float, optional
        Maximum daily rate.
    limit : int, optional
        Maximum number of records to return.
    offset : int, optional
        Number of records to skip for pagination.
    **dados : dict
        Additional unused parameters.

    Returns
    -------
    dict
        Dictionary containing normalized filtering parameters.
    """
    if cidade:
        return {
            'cidade': cidade,
            'estrelas_min': estrelas_min,
            'estrelas_max': estrelas_max,
            'diaria_min': diaria_min,
            'diaria_max': diaria_max,
            'limit': limit,
            'offset': offset
        }

    return {
        'estrelas_min': estrelas_min,
        'estrelas_max': estrelas_max,
        'diaria_min': diaria_min,
        'diaria_max': diaria_max,
        'limit': limit,
        'offset': offset
    }


# ---------------------------------------------------------------------
# SQL Query Templates
# ---------------------------------------------------------------------

consulta_sem_cidade = (
    "SELECT * FROM hoteis "
    "WHERE (estrelas >= ? and estrelas <= ?) "
    "and (diaria >= ? and diaria <= ?) "
    "LIMIT ? OFFSET ?"
)
"""
SQL query template used when no city filter is applied.
"""


consulta_com_cidade = (
    "SELECT * FROM hoteis "
    "WHERE (estrelas >= ? and estrelas <= ?) "
    "and (diaria >= ? and diaria <= ?) "
    "and cidade = ? "
    "LIMIT ? OFFSET ?"
)
"""
SQL query template used when filtering by city.
"""


# ---------------------------------------------------------------------
# Validation Utilities
# ---------------------------------------------------------------------

def non_empty_str(value):
    """
    Validate that a string is not empty.

    Parameters
    ----------
    value : Any
        Input value to validate.

    Returns
    -------
    str
        Stripped string value if valid.

    Raises
    ------
    ValueError
        If the value is empty after stripping.
    """
    s = str(value).strip()
    if not s:
        raise ValueError("must not be empty")
    return s


def positive_float(value):
    """
    Validate that a value is a positive float.

    Parameters
    ----------
    value : Any
        Input value to validate.

    Returns
    -------
    float
        Converted float value if valid.

    Raises
    ------
    ValueError
        If the value is not numeric or is less than or equal to zero.
    """
    try:
        v = float(value)
    except Exception:
        raise ValueError("must be a number")

    if v <= 0:
        raise ValueError("must be greater than 0")

    return v


def estrelas_float(value):
    """
    Validate that a value is a float between 0 and 5.

    Parameters
    ----------
    value : Any
        Input value to validate.

    Returns
    -------
    float
        Converted float value if within the valid range.

    Raises
    ------
    ValueError
        If the value is not numeric or outside the range 0 to 5.
    """
    try:
        v = float(value)
    except Exception:
        raise ValueError("must be a number")

    if v < 0 or v > 5:
        raise ValueError("must be between 0 and 5")

    return v