"""
Nozomi
IP Address Module
author: hugh@blinkybeach.com
"""
from nozomi.data.encodable import Encodable
from nozomi.http.headers import Headers
from nozomi.ancillary.immutable import Immutable
from nozomi.data.sql_conforming import SQLConforming
from nozomi.errors.error import NozomiError
from typing import TypeVar, Type

T = TypeVar('T', bound='IpAddress')


class IpAddress(SQLConforming, Encodable):
    """
    A client IP address, discerned from examining headers written by a
    network boundary, presumed to be HAProxy
    """
    IP_HEADER = 'X-Ip-At-Boundary'

    def __init__(self, raw_address: str) -> None:

        assert isinstance(raw_address, str)
        self._raw_address = raw_address
        return

    sql_representation = Immutable(lambda s: s.quote_string(s._raw_address))

    @classmethod
    def load_from_headers(
        cls: Type[T],
        request_headers: Headers,
        debug: bool = False,
        debug_address: str = None
    ) -> T:

        assert isinstance(debug, bool)

        if debug is True:
            assert isinstance(debug_address, str)
            return cls(debug_address)

        addresses = request_headers.getlist(cls.IP_HEADER)

        # We presume that headers are being set by HAProxy. If these checks
        # fail, HAProxy is not configured properly.

        if len(addresses) != 1:
            raise NozomiError('Internal error', 500)

        if len(addresses[0].split(',')) != 1:
            raise NozomiError('Internal error', 500)

        return cls(addresses[0])

    def encode(self) -> str:
        return self._raw_address

    def __str__(self) -> str:
        return self._raw_address
