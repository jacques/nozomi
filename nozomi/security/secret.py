"""
Nozomi
Secret Module
author: hugh@blinkybeach.com
"""
import hmac
from nozomi.ancillary.immutable import Immutable
from nozomi.errors.error import NozomiError
from nozomi.security.salt import Salt
from nozomi.data.datastore import Datastore
import argon2
from typing import TypeVar, Type, Optional
from nozomi.data.query import Query

T = TypeVar('T', bound='Secret')


class Secret:
    """
    A user's secret passphrase
    """
    Q_RETRIEVE_BY_EMAIL = Query.from_file('queries/secret/retrieve.sql')

    def __init__(
        self,
        salt: Salt,
        hashed_passphrase: str
    ) -> None:

        assert isinstance(hashed_passphrase, str)
        assert isinstance(salt, Salt)
        self._hashed_passphrase = hashed_passphrase
        self._salt = salt

        return

    hashed_passphrase = Immutable(lambda s: s._hashed_passphrase)
    salt = Immutable(lambda s: s._salt.string)

    @classmethod
    def _compute_hash(cls: Type[T], raw_secret: str, salt: Salt) -> str:
        """Compute the Argon2 hash of the provided secret"""
        assert isinstance(raw_secret, str)
        assert isinstance(salt, Salt)
        computed_hash = argon2.low_level.hash_secret(
            raw_secret.encode('utf-8'),
            salt=salt.utf8_bytes,
            time_cost=10,
            memory_cost=64,
            parallelism=2,
            hash_len=48,
            type=argon2.Type.I
        ).decode('utf-8')
        return computed_hash

    def matches(self, plaintext_passphrase: str) -> bool:
        """Return True if the supplied passphrase matches this one"""
        supplied_secret_hash = self._compute_hash(
            plaintext_passphrase,
            self._salt
        )
        comparison = hmac.compare_digest(
            supplied_secret_hash,
            self._hashed_passphrase
        )
        assert isinstance(comparison, bool)
        if comparison is True:
            return True
        return False

    @classmethod
    def create_from_plaintext(cls: Type[T], plaintext_passphrase: str) -> T:
        """Return a Secret created based on the supplied plaintext passphrase"""
        if not isinstance(plaintext_passphrase, str):
            raise NozomiError('Passphrases must be strings', 400)
        salt = Salt.create()
        hashed_passphrase = cls._compute_hash(plaintext_passphrase, salt)
        return cls(salt, hashed_passphrase)

    @classmethod
    def retrieve_for_user_id(cls: Type[T], user_id: int) -> T:
        """Return the active Secret for a given User ID"""
        raise NotImplementedError

    @classmethod
    def retrieve_for_email(
        cls: Type[T],
        email: str,
        datastore: Datastore
    ) -> Optional[T]:
        """
        Return the active Secret for a given email, or None if no secret exists
        for said email
        """
        assert isinstance(datastore, Datastore)
        assert isinstance(email, str)

        arguments = {'email_address': email}
        result = cls.Q_RETRIEVE_BY_EMAIL.execute(datastore, arguments)
        if result is None:
            return None

        return cls(
            salt=Salt(salt_b64_string=result['salt']),
            hashed_passphrase=result['secret_hash']
        )

    def __str__(self) -> str:
        return self.hashed_passphrase
