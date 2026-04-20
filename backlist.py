"""
Token blacklist module.

This module defines the in-memory data structure used to store
revoked JWT token identifiers (JTI). Tokens added to this set
are considered invalid and cannot be used for authenticated requests.

Note
----
This implementation uses an in-memory set, which means all revoked
tokens will be lost if the application restarts. For production
environments, a persistent storage solution (e.g., database or Redis)
is recommended.
"""

BLACKLIST = set()
"""
Set containing revoked JWT token identifiers (JTI).

The JWTManager checks this set to determine whether a token
has been invalidated (e.g., after user logout).
"""