#!/usr/bin/env python

from asyncio import run as asyncio_run
from typing import Optional, Type
from json import dumps as json_dumps
from dataclasses import asdict
from sys import stderr

from httpx import AsyncClient as HTTPXAsyncClient, HTTPStatusError

from httpx_oauth.v1 import OAuthAuth
from twitter_api.calls import get_friend_ids, get_follower_ids, lookup_users, show_user

from pyutils.argparse.typed_argument_parser import TypedArgumentParser


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


async def main():

    args: Type[TwitterApiArgumentParser.Namespace] = TwitterApiArgumentParser().parse_args()

    auth = OAuthAuth(consumer_key=args.consumer_key, consumer_secret=args.consumer_secret)
    async with HTTPXAsyncClient(auth=auth) as http_client:
        if args.action == 'user':
            try:
                print(
                    json_dumps(
                        asdict(
                            await show_user(
                                http_client=http_client,
                                user_id=args.user_id,
                                screen_name=args.screen_name
                            )
                        ),
                        indent=4
                    )
                )
            except HTTPStatusError as e:
                print(e, file=stderr)
        elif args.action == 'followers':
            try:
                print(
                    '\n'.join(
                        user.screen_name
                        for user in await lookup_users(
                            http_client=http_client,
                            user_ids=await get_follower_ids(
                                http_client=http_client,
                                user_id=args.user_id,
                                screen_name=args.screen_name,
                                follow_cursor=True
                            )
                        )
                    )
                )
            except HTTPStatusError as e:
                print(e, file=stderr)
        elif args.action == 'following':
            try:
                print(
                    '\n'.join(
                        user.screen_name
                        for user in await lookup_users(
                            http_client=http_client,
                            user_ids=await get_friend_ids(
                                http_client=http_client,
                                user_id=args.user_id,
                                screen_name=args.screen_name,
                                follow_cursor=True
                            )
                        )
                    )
                )
            except HTTPStatusError as e:
                print(e, file=stderr)


if __name__ == '__main__':
    asyncio_run(main())
