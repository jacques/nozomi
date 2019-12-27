"""
Nozomi
Secure Resource Module
author: hugh@blinkybeach.com
"""
from typing import Any
from nozomi.errors.error import NozomiError
from nozomi.security.broadcastable import Broadcastable
from nozomi.security.session import Session
from nozomi.security.agent import Agent
from nozomi.resources.resource import Resource
from nozomi.http.query_string import QueryString
from nozomi.http.headers import Headers
from nozomi.http.status_code import HTTPStatusCode
from typing import Optional
from typing import Tuple


class SecureResource(Resource):
    """
    Abstract class defining an interface for API requests that
    require authentication. Authorisation should be performed
    in the implementing subclass. To authorise a request, call
    SecureResource.authorise() in the subclass compute_response() method.
    """

    def compute_response(
        self,
        request_data: Optional[Any],
        request_arguments: Optional[QueryString],
        requesting_agent: Agent
    ) -> Tuple[Broadcastable, Agent]:
        """
        Method returning an encodable response, and an Agent authorised to
        make the request
        """
        raise NotImplementedError

    def serve(
        self,
        request_data: Optional[Any],
        request_arguments: Optional[QueryString],
        headers: Headers
    ) -> str:
        session = Session.require_from_headers(
            headers=headers,
            datastore=self.datastore,
            configuration=self.configuration
        )
        assert isinstance(session, Session)
        response, authorised_agent = self.compute_response(
            request_data,
            request_arguments,
            session.human
        )
        if not isinstance(authorised_agent, Agent):
            raise RuntimeError('Request not authorised')
        if authorised_agent != session.agent:
            raise NozomiError('Not authorised', HTTPStatusCode.NOT_AUTHORISED)
        assert authorised_agent == session.agent
        return response.broadcast_to(authorised_agent).serialise()
