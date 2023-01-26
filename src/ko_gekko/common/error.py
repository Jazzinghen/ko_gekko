# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
""" KoGekko's Errors

Module containing error proxies to handle exceptions properly outside of the library
"""


class KoGekkoError(Exception):
    """Base error that acts as root for all the other errors"""

    pass


class KoGekkoBackendError(KoGekkoError):
    """Internal libraries' error"""

    pass


class KoGekkoRemoteError(KoGekkoError):
    """Remote content retrieval error"""

    pass
