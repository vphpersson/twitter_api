from typing import Optional
from json import dumps as json_dumps
from dataclasses import asdict

from httpx import AsyncClient as HTTPXAsyncClient
from twitter_api.calls import get_friend_ids, get_follower_ids, lookup_users, show_user
from pyutils.argparse.typed_argument_parser import TypedArgumentParser

# TODO: Add action enum?


class TwitterApiArgumentParser(TypedArgumentParser):

    class Namespace:
        consumer_key: str
        consumer_secret: str
        action: str
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
            choices=['user', 'followers', 'following']
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


async def twitter_api(
    http_client: HTTPXAsyncClient,
    action: str,
    user_id: Optional[str],
    screen_name: Optional[str]
) -> None:
    if action == 'user':
        print(
            json_dumps(
                asdict(
                    await show_user(
                        http_client=http_client,
                        user_id=user_id,
                        screen_name=screen_name
                    )
                ),
                indent=4
            )
        )
    elif action == 'followers':
        print(
            '\n'.join(
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
        )
    elif action == 'following':
        print(
            '\n'.join(
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
        )
