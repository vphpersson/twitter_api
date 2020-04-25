from typing import Optional, Set, Iterable, Tuple, Dict, List, Union
from urllib.parse import urljoin, quote, parse_qs, urlparse, urlencode

from httpx import AsyncClient as HTTPXAsyncClient
from httpx_oauth.v1 import RequestTokenResponse
from pyutils.my_http import HTTPStatusError

from twitter_api.structures import IdsResult, User, AccessTokenResponse

user_info_url = 'https://api.twitter.com/1.1/account/verify_credentials.json'

API_VERSION = '1.1'
TWITTER_BASE_URL = 'https://api.twitter.com/'
TWITTER_API_URL: str = f'{TWITTER_BASE_URL}{API_VERSION}/'


async def request_oauth_token(http_client: HTTPXAsyncClient) -> RequestTokenResponse:

    response = await http_client.post(url=urljoin(TWITTER_BASE_URL, 'oauth/request_token'))

    if response.is_error:
        raise HTTPStatusError.from_status_code(status_code=response.status_code, response=response)

    query_parameters_dict: Dict[str, List[str]] = parse_qs(response.text)

    return RequestTokenResponse(
        oauth_token=query_parameters_dict['oauth_token'][0],
        oauth_token_secret=query_parameters_dict['oauth_token_secret'][0],
        oauth_callback_confirmed=query_parameters_dict['oauth_callback_confirmed'][0] == 'true'
    )


def make_authorize_url(request_token: str) -> str:
    return urlparse(
        url=urljoin(TWITTER_BASE_URL, 'oauth/authorize')
    )._replace(query=urlencode(dict(oauth_token=request_token))).geturl()


async def get_access_token(
    http_client: HTTPXAsyncClient,
    oauth_consumer_key: str,
    request_token: str,
    oauth_verifier: str
):
    """

    :param http_client:
    :param oauth_consumer_key:
    :param request_token:
    :param oauth_verifier:
    :return:
    """

    response = await http_client.post(
        url=urljoin(TWITTER_BASE_URL, 'oauth/access_token'),
        params=dict(
            oauth_consumer_key=oauth_consumer_key,
            oauth_token=request_token,
            oauth_verifier=oauth_verifier
        )
    )

    if response.is_error:
        raise HTTPStatusError.from_status_code(status_code=response.status_code, response=response)

    query_parameters_dict: Dict[str, List[str]] = parse_qs(response.text)

    return AccessTokenResponse(
        oauth_token=query_parameters_dict['oauth_token'][0],
        oauth_token_secret=query_parameters_dict['oauth_token_secret'][0],
        user_id=int(query_parameters_dict['user_id'][0]),
        screen_name=query_parameters_dict['screen_name'][0]
    )


# TODO: Add additional parameters.
async def update_status(http_client: HTTPXAsyncClient, status: str):
    """
    Update a user's current status, i.e. tweet.

    https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/post-statuses-update

    :param http_client: The HTTP client with which to perform the HTTP request to update the status.
    :param status: The text of the status update.
    :return:
    """

    response = await http_client.post(
        url=urljoin(TWITTER_API_URL, 'statuses/update.json'),
        data={'status': status}
    )

    if response.is_error:
        raise HTTPStatusError.from_status_code(status_code=response.status_code, response=response)

    # TODO: Fix response.


async def search_users(
    http_client: HTTPXAsyncClient,
    search_query: str,
    page: Optional[int] = None,
    count: Optional[int] = None,
    include_entities: Optional[bool] = None,
) -> Tuple[User, ...]:
    """
    Retrieve user information of users matching a search query.

    Only the first 1000 matching results are available.

    https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-users-search

    :param http_client: The HTTP client with which to perform the HTTP request to retrieve the user information.
    :param search_query: The search query.
    :param page:
    :param count:
    :param include_entities:
    :return: A tuple of user information of the users matching the search query.
    """

    response = await http_client.get(
        url=urljoin(TWITTER_API_URL, 'users/search.json'),
        params={
            key: value
            for key, value in [
                ('q', quote(string=search_query)),
                ('page', page),
                ('count', count),
                ('include_entities', include_entities)
            ]
            if value is not None
        }
    )

    if response.is_error:
        raise HTTPStatusError.from_status_code(status_code=response.status_code, response=response)

    return tuple(User.from_json(json_object=user_object) for user_object in response.json())


async def show_user(
    http_client: HTTPXAsyncClient,
    user_id: Optional[int] = None,
    screen_name: Optional[str] = None,
    include_entities: Optional[bool] = None,
) -> User:
    """
    Retrieve user information about a specified user.

    https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-users-show

    :param http_client: The HTTP client with which to perform the HTTP request to retrieve the user information.
    :param user_id: The user ID of the user whose information to retrieve.
    :param screen_name: The screen name of the user whose information to retrieve.
    :param include_entities:
    :return: User information about the specified user.
    """

    response = await http_client.get(
        url=urljoin(TWITTER_API_URL, 'users/show.json'),
        params={
            key: value
            for key, value in [
                ('user_id', user_id),
                ('screen_name', screen_name),
                ('include_entities', include_entities)
            ]
            if value is not None
        }
    )

    if response.is_error:
        raise HTTPStatusError.from_status_code(status_code=response.status_code, response=response)

    return User.from_json(json_object=response.json())


async def lookup_users(
    http_client: HTTPXAsyncClient,
    user_ids: Iterable[Union[int, str]] = None,
    screen_names: Iterable[str] = None,
    include_entities: Optional[bool] = None,
    tweet_mode: Optional[bool] = None
) -> Tuple[User, ...]:
    """
    Retrieve user information about specified users.

    https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-users-lookup

    :param http_client: The HTTP client with which to perform the HTTP request to look up the users.
    :param user_ids: The user IDs of the users whose information to retrieve.
    :param screen_names: The screen names of the users whose information to retrieve.
    :param include_entities:
    :param tweet_mode:
    :return: A tuple of user information about the specified users.
    """

    response = await http_client.get(
        url=urljoin(TWITTER_API_URL, 'users/lookup.json'),
        params={
            key: value
            for key, value in [
                ('user_id', ','.join(str(user_id) for user_id in (user_ids or []))),
                ('screen_name', ','.join(screen_names or [])),
                ('include_entities', include_entities),
                ('tweet_mode', tweet_mode)
            ]
            if value is not None
        }
    )

    if response.is_error:
        raise HTTPStatusError.from_status_code(status_code=response.status_code, response=response)

    return tuple(User.from_json(json_object=user_object) for user_object in response.json())


async def get_friend_ids(
    http_client: HTTPXAsyncClient,
    user_id: Optional[int] = None,
    screen_name: Optional[str] = None,
    cursor: Optional[int] = None,
    stringify_ids: Optional[bool] = None,
    count: Optional[int] = None,
    follow_cursor: bool = False
) -> Set[int]:
    """
    Retrieve the user IDs of the users a specified user is following.

    https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-friends-ids

    :param http_client: The HTTP client with which to perform the HTTP request to retrieve the user's friends' IDs.
    :param user_id: The user ID of the user whose friends' user IDs to retrieve.
    :param screen_name: The screen name of the user whose friends' user IDs to retrieve.
    :param cursor: A cursor indicating an offset from which to obtain the results.
    :param stringify_ids: Whether to have IDs returned as strings.
    :param count: the number of IDs attempt retrieval of, up to a maximum of 5,000 per distinct request.
    :param follow_cursor: Whether to follow the cursor, in order to obtain the complete result.
    :return: A set of user IDs of the friends of the specified user.
    """

    response = await http_client.get(
        url=urljoin(TWITTER_API_URL, 'friends/ids.json'),
        params={
            key: value
            for key, value in [
                ('user_id', user_id),
                ('screen_name', screen_name),
                ('cursor', cursor),
                ('stringify_ids', stringify_ids),
                ('count', count)
            ]
            if value is not None
        }
    )

    if response.is_error:
        raise HTTPStatusError.from_status_code(status_code=response.status_code, response=response)

    ids_result = IdsResult.from_json(json_object=response.json())

    if follow_cursor and ids_result.next_cursor != 0:
        return set(ids_result.ids).union(
            await get_friend_ids(
                http_client=http_client,
                user_id=user_id,
                screen_name=screen_name,
                cursor=ids_result.next_cursor,
                stringify_ids=stringify_ids,
                count=count,
                follow_cursor=follow_cursor
            )
        )

    return set(ids_result.ids)


async def get_follower_ids(
    http_client: HTTPXAsyncClient,
    user_id: Optional[int] = None,
    screen_name: Optional[str] = None,
    cursor: Optional[int] = None,
    stringify_ids: Optional[bool] = None,
    count: Optional[int] = None,
    follow_cursor: bool = False
) -> Set[int]:
    """
    Retrieve the user IDs of followers of a specified user.

    https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-followers-ids

    :param http_client: The HTTP client with which to perform the HTTP request to retrieve user's followers' IDs.
    :param user_id: The user ID of the user whose followers' IDs to retrieve.
    :param screen_name: The screen name of the user whose followers' IDs to retrieve.
    :param cursor:
    :param stringify_ids:
    :param count:
    :param follow_cursor: Whether to follow the cursor, in order to obtain the complete result.
    :return: A set of the IDs of the followers of the specified user.
    """

    response = await http_client.get(
        url=urljoin(TWITTER_API_URL, 'followers/ids.json'),
        params={
            key: value
            for key, value in [
                ('user_id', user_id),
                ('screen_name', screen_name),
                ('cursor', cursor),
                ('stringify_ids', stringify_ids),
                ('count', count)
            ]
            if value is not None
        }
    )

    if response.is_error:
        raise HTTPStatusError.from_status_code(status_code=response.status_code, response=response)

    ids_result = IdsResult.from_json(json_object=response.json())

    if follow_cursor and ids_result.next_cursor != 0:
        return set(ids_result.ids).union(
            await get_follower_ids(
                http_client=http_client,
                user_id=user_id,
                screen_name=screen_name,
                cursor=ids_result.next_cursor,
                stringify_ids=stringify_ids,
                count=count,
                follow_cursor=follow_cursor
            )
        )

    return set(ids_result.ids)
