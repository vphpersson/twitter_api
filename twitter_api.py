#!/usr/bin/env python

from asyncio import run as asyncio_run
from typing import Type, Optional
from sys import stderr

from httpx import AsyncClient as HTTPXAsyncClient, HTTPStatusError
from httpx_oauth.v1 import OAuthAuth

from twitter_api.cli import TwitterApiArgumentParser, twitter_api
from twitter_api.utils import set_auth_tokens


async def main():
    args: Type[TwitterApiArgumentParser.Namespace] = TwitterApiArgumentParser().parse_args()

    try:
        auth = OAuthAuth(consumer_key=args.consumer_key, consumer_secret=args.consumer_secret)
        async with HTTPXAsyncClient(auth=auth) as http_client:
            if args.access_tokens_path:
                await set_auth_tokens(
                    http_client=http_client,
                    consumer_key=args.consumer_key,
                    tokens_path=args.access_tokens_path
                )

            str_result: Optional[str] = await twitter_api(
                http_client=http_client,
                action=args.action,
                user_id=args.user_id,
                screen_name=args.screen_name
            )
            if str_result:
                print(str_result)
    except HTTPStatusError as e:
        print(
            '\n'.join(str(e).split('\n')[:-1]) + '\n' + e.response.text,
            file=stderr
        )


if __name__ == '__main__':
    asyncio_run(main())
