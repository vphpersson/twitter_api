from typing import Optional, Union
from dataclasses import asdict
from json import loads as json_loads, dumps as json_dumps
from pathlib import Path

from httpx import AsyncClient as HTTPXAsyncClient

from twitter_api.calls import request_oauth_token, make_authorize_url, get_access_token
from twitter_api.structures import AccessTokenResponse


async def set_auth_tokens(
    http_client: HTTPXAsyncClient,
    consumer_key: Optional[str] = None,
    tokens_path: Optional[Union[Path, str]] = None
) -> None:
    """
    Obtain OAuth access tokens from a file or an HTTP endpoint and update the provided HTTP client auth handler.

    `http_client.auth` must be of type `OAuthV1Auth`.

    https://developer.twitter.com/en/docs/basics/authentication/oauth-1-0a/obtaining-user-access-tokens

    :param http_client: The HTTP client whose auth handler to update, and possibly retrieve OAuth tokens.
    :param consumer_key: The consumer key to be used in case OAuth tokens are to be retrieved from the HTTP endpoint.
    :param tokens_path: The path where the OAuth tokens are to be read from or stored.
    :return: None
    """

    if tokens_path is not None:
        tokens_path = Path(tokens_path)

    try:
        access_token_response = AccessTokenResponse.from_json(
            json_object=json_loads(s=tokens_path.read_text())
        )
    except (FileNotFoundError, AttributeError):
        request_token: str = (await request_oauth_token(http_client=http_client)).oauth_token

        print(f'Open {make_authorize_url(request_token=request_token)} in a browser.')
        access_token_response = await get_access_token(
            http_client=http_client,
            oauth_consumer_key=consumer_key,
            request_token=request_token,
            oauth_verifier=input('PIN code: ')
        )

        tokens_path.write_text(json_dumps(obj=asdict(access_token_response)))

    http_client.auth.oauth_access_token = access_token_response.oauth_token
    http_client.auth.oauth_access_token_secret = access_token_response.oauth_token_secret
