#!/usr/bin/env python

from asyncio import run as asyncio_run
from typing import Type
from sys import stderr

from httpx import AsyncClient as HTTPXAsyncClient, HTTPStatusError
from httpx_oauth.v1 import OAuthAuth

from twitter_api.cli import TwitterApiArgumentParser, twitter_api


async def main():
    args: Type[TwitterApiArgumentParser.Namespace] = TwitterApiArgumentParser().parse_args()

    try:
        auth = OAuthAuth(consumer_key=args.consumer_key, consumer_secret=args.consumer_secret)
        async with HTTPXAsyncClient(auth=auth) as http_client:
            await twitter_api(
                http_client=http_client,
                action=args.action,
                user_id=args.user_id,
                screen_name=args.screen_name
            )
    except HTTPStatusError as e:
        print(e, file=stderr)


if __name__ == '__main__':
    asyncio_run(main())
