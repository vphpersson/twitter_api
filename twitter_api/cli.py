from typing import Optional
from json import dumps as json_dumps
from dataclasses import asdict
from enum import Enum

from httpx import AsyncClient as HTTPXAsyncClient
from twitter_api.calls import get_friend_ids, get_follower_ids, lookup_users, show_user, create_friendship
from pyutils.argparse.typed_argument_parser import TypedArgumentParser


class TwitterApiAction(Enum):
    USER = 'user'
    FOLLOWERS = 'followers'
    FOLLOWING = 'following'
    FOLLOW = 'follow'


class TwitterApiArgumentParser(TypedArgumentParser):

    class Namespace:
        consumer_key: str
        consumer_secret: str
        action: str
        access_tokens_path: Optional[str]
        user_id: Optional[str]
        screen_name: Optional[str]

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **(
                dict(
                    description='Perform an action using the Twitter API.'
                )
                | kwargs
            )
        )

        self.add_argument(
            'consumer_key',
            help='A consumer key with which to authenticate to use the Twitter API.'
        )

        self.add_argument(
            'consumer_secret',
            help='A consumer secret with which to authenticate to use the Twitter API.'
        )

        self.add_argument(
            'action',
            help='The Twitter API action to perform.',
            choices=[member.value for member in TwitterApiAction]
        )

        user_group = self.add_mutually_exclusive_group(required=True)
        user_group.add_argument(
            '--user-id',
            help='An user ID of an user to examine.'
        )
        user_group.add_argument(
            '--screen-name',
            help='A screen name of a user to examine.'
        )

        self.add_argument(
            '--access-tokens-path',
            help='The path of a file storing access tokens.',
        )


async def twitter_api(
    http_client: HTTPXAsyncClient,
    action: str,
    user_id: Optional[str],
    screen_name: Optional[str]
) -> Optional[str]:
    if action == 'user':
        return json_dumps(
            asdict(
                await show_user(
                    http_client=http_client,
                    user_id=user_id,
                    screen_name=screen_name
                )
            ),
            indent=4
        )
    elif action == 'followers':
        return '\n'.join(
            user.screen_name
            for user in await lookup_users(
                http_client=http_client,
                user_ids=await get_follower_ids(
                    http_client=http_client,
                    user_id=user_id,
                    screen_name=screen_name,
                    follow_cursor=True
                )
            )
        )
    elif action == 'following':
        return '\n'.join(
            user.screen_name
            for user in await lookup_users(
                http_client=http_client,
                user_ids=await get_friend_ids(
                    http_client=http_client,
                    user_id=user_id,
                    screen_name=screen_name,
                    follow_cursor=True
                )
            )
        )
    elif action == 'follow':
        await create_friendship(
            http_client=http_client,
            user_id=user_id,
            screen_name=screen_name
        )
