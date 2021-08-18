from typing import Optional, Iterable, Union, Any
from urllib.parse import urljoin, quote, parse_qs, urlparse, urlencode

from httpx import AsyncClient as HTTPXAsyncClient
from httpx_oauth.v1 import RequestTokenResponse

from twitter_api.structures import IdsResult, User, AccessTokenResponse, Status, SearchTweetsResponse

user_info_url = 'https://api.twitter.com/1.1/account/verify_credentials.json'

API_VERSION = '1.1'
TWITTER_BASE_URL = 'https://api.twitter.com/'
TWITTER_API_URL: str = f'{TWITTER_BASE_URL}{API_VERSION}/'


async def request_oauth_token(http_client: HTTPXAsyncClient) -> RequestTokenResponse:

    response = await http_client.post(url=urljoin(TWITTER_BASE_URL, 'oauth/request_token'))

    response.raise_for_status()

    query_parameters_dict: dict[str, list[str]] = parse_qs(response.text)

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
) -> AccessTokenResponse:
    """
    Obtain an OAuth access token from an OAuth request token.

    https://developer.twitter.com/en/docs/authentication/api-reference/access_token

    :param http_client: An HTTP client with which to retrieve the access token.
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
    response.raise_for_status()

    query_parameters_dict: dict[str, list[str]] = parse_qs(response.text)

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
    response.raise_for_status()

    # TODO: Fix response.


async def search_users(
    http_client: HTTPXAsyncClient,
    search_query: str,
    page: Optional[int] = None,
    count: Optional[int] = None,
    include_entities: Optional[bool] = None,
) -> tuple[User, ...]:
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
    response.raise_for_status()

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
    response.raise_for_status()

    return User.from_json(json_object=response.json())


async def lookup_users(
    http_client: HTTPXAsyncClient,
    user_ids: Iterable[Union[int, str]] = None,
    screen_names: Iterable[str] = None,
    include_entities: Optional[bool] = None,
    # NOTE: Undocumented (!) - When set to "extended", the full text a of a tweet is returned.
    tweet_mode: Optional[bool] = None
) -> tuple[User, ...]:
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

    json_user_objects: list[dict[str, Any]] = []

    user_ids = [str(user_id) for user_id in user_ids] if user_ids is not None else []
    screen_names = list(screen_names) if screen_names else []

    user_ids_index = 0
    screen_names_index = 0

    # TODO: It would be cool to use `asyncio.gather` here...

    while True:
        iter_user_ids = user_ids[user_ids_index:user_ids_index+100]
        user_ids_index += 100

        num_slots_remaining = 100 - len(iter_user_ids)

        iter_screen_names = screen_names[screen_names_index:screen_names_index+num_slots_remaining]
        screen_names_index += num_slots_remaining

        if not iter_user_ids and not iter_screen_names:
            break

        response = await http_client.get(
            url=urljoin(TWITTER_API_URL, 'users/lookup.json'),
            params={
                key: value
                for key, value in [
                    ('user_id', ','.join(iter_user_ids) if iter_user_ids else None),
                    ('screen_name', ','.join(iter_screen_names) if iter_screen_names else None),
                    ('include_entities', include_entities),
                    ('tweet_mode', tweet_mode)
                ]
                if value is not None
            }
        )
        response.raise_for_status()

        json_user_objects.extend(response.json())

    return tuple(User.from_json(json_object=user_object) for user_object in json_user_objects)


async def get_friend_ids(
    http_client: HTTPXAsyncClient,
    user_id: Optional[int] = None,
    screen_name: Optional[str] = None,
    cursor: Optional[int] = None,
    stringify_ids: Optional[bool] = None,
    count: Optional[int] = None,
    follow_cursor: bool = False
) -> list[int]:
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
    response.raise_for_status()

    ids_result = IdsResult.from_json(json_object=response.json())

    if follow_cursor and ids_result.next_cursor != 0:
        ids_result.ids.extend(
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

    return ids_result.ids


async def get_follower_ids(
    http_client: HTTPXAsyncClient,
    user_id: Optional[int] = None,
    screen_name: Optional[str] = None,
    cursor: Optional[int] = None,
    stringify_ids: Optional[bool] = None,
    count: Optional[int] = None,
    follow_cursor: bool = False
) -> list[int]:
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
    response.raise_for_status()

    ids_result = IdsResult.from_json(json_object=response.json())

    if follow_cursor and ids_result.next_cursor != 0:
        ids_result.ids.extend(
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

    return ids_result.ids


async def create_friendship(
    http_client: HTTPXAsyncClient,
    user_id: Optional[int] = None,
    screen_name: Optional[str] = None,
    follow: bool = False
) -> User:
    """
    Create a friendship with a user (i.e. follow a user).

    https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/post-friendships-create

    :param http_client: The HTTP client with which to perform the request.
    :param user_id: The user id of the user to follow.
    :param screen_name: The screen name of the user to follow.
    :param follow: Whether to enable notifications for the target user.
    :return: The followed user.
    """

    response = await http_client.post(
        url=urljoin(TWITTER_API_URL, 'friendships/create.json'),
        params={
            key: value
            for key, value in [
                ('user_id', user_id),
                ('screen_name', screen_name),
                ('follow', 'true' if follow else None)
            ]
            if value is not None
        }
    )
    response.raise_for_status()

    return User.from_json(json_object=response.json())


async def user_timeline_statuses(
    http_client: HTTPXAsyncClient,
    user_id: Optional[int] = None,
    screen_name: Optional[str] = None,
    since_id: Optional[int] = None,
    count: Optional[int] = None,
    max_id: Optional[int] = None,
    trim_user: Optional[bool] = None,
    exclude_replies: Optional[bool] = None,
    include_rts: Optional[bool] = None,
    tweet_mode: Optional[str] = None
) -> tuple[Status, ...]:
    """
    Retrieve statuses (i.e. tweets) of a user.

    https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/api-reference/get-statuses-user_timeline

    :param http_client: The HTTP client with which to perform the request.
    :param user_id: The user id of the user whose statuses to retrieve.
    :param screen_name: The screen name of the user whose statuses to retrieve.
    :param since_id: The minimum non-inclusive id of the statuses to return.
    :param count: The maximum number of statuses to retrieve.
    :param max_id: The maximum id of the statuses to return.
    :param trim_user: Whether to trim the user object included in the statuses.
    :param exclude_replies: Whether to exclude replies.
    :param include_rts: Whether to include retweets.
    :return: Statuses matching the criteria.
    """

    response = await http_client.get(
        url=urljoin(TWITTER_API_URL, 'statuses/user_timeline.json'),
        params={
            key: value
            for key, value in [
                ('user_id', user_id),
                ('screen_name', screen_name),
                ('since_id', since_id),
                ('count', count),
                ('max_id', max_id),
                ('trim_user', 'true' if trim_user else None),
                ('exclude_replies', 'true' if exclude_replies else None),
                ('include_rts', 'true' if include_rts else None),
                ('tweet_mode', tweet_mode)
            ]
            if value is not None
        }
    )
    response.raise_for_status()

    return tuple(Status.from_json(json_object=status_dict) for status_dict in response.json())


async def search_tweets(
    http_client: HTTPXAsyncClient,
    q: str,
    geocode: Optional[str] = None,
    lang: Optional[str] = None,
    locale: Optional[str] = None,
    result_type: ... = None,
    count: Optional[int] = None,
    until: Optional[str] = None,
    since_id: Optional[str] = None,
    max_id: Optional[str] = None,
    include_entities: Optional[bool] = None
) -> SearchTweetsResponse:
    """
    Search Tweets.

    https://developer.twitter.com/en/docs/twitter-api/v1/tweets/search/api-reference/get-search-tweets

    :param http_client: The HTTP client with which to perform the request.
    :param q:
    :param geocode:
    :param lang:
    :param locale:
    :param result_type:
    :param count:
    :param until:
    :param since_id:
    :param max_id:
    :param include_entities:
    :return:
    """

    response = await http_client.get(
        url=urljoin(TWITTER_API_URL, 'search/tweets.json'),
        params={
            key: value
            for key, value in [
                ('q', q),
                ('geocode', geocode),
                ('lang', lang),
                ('locale', locale),
                ('result_type', result_type),
                ('count', count),
                ('until', until),
                ('since_id', since_id),
                ('max_id', max_id),
                ('include_entities', 'true' if include_entities else None)
            ]
            if value is not None
        }
    )
    response.raise_for_status()

    return SearchTweetsResponse.from_json(json_object=response.json())
