
Work in progress.

## Example applications

### List all followers of a user that the user follows

```python
from asyncio import run as asyncio_run, gather as asyncio_gather

from httpx import AsyncClient as HTTPXAsyncClient
from httpx_oauth.v1 import OAuthAuth
from twitter_api.calls import get_friend_ids, get_follower_ids, lookup_users


async def main():
    consumer_key = 'CONSUMER_KEY'
    consumer_secret = 'CONSUMER_SECRET'
    target_username = 'sandboxbear'

    auth = OAuthAuth(consumer_key=consumer_key, consumer_secret=consumer_secret)

    async with HTTPXAsyncClient(auth=auth) as http_client:
        friend_ids, follower_ids = await asyncio_gather(
            get_friend_ids(http_client=http_client, screen_name=target_username, follow_cursor=True),
            get_follower_ids(http_client=http_client, screen_name=target_username, follow_cursor=True)
        )

        print(
            '\n'.join(
                user.screen_name
                for user in await lookup_users(http_client=http_client, user_ids=friend_ids.intersection(follower_ids))
            )
        )

if __name__ == '__main__':
    asyncio_run(main())
```

**Output:**
```
0x1day
VV_X_7
KateLibc
foxwithpaws
fiendishandroid
smurfhell
0xGlitch
malltos92
UK_Daniel_Card
adhsec
B1naryG
dcuthbert
Kym_Possible
Andreiztm
nixbyte
malwrpost
tiraniddo
_sh286
velvetsemtex
SwiftOnSecurity
bsdaemon
NGC_3572
donhey
reybango
manoj_jindal
KvinKISOKA
LargeCardinal
jonasLyk
LiveOverflow
hackerfantastic
TheLumberJhack
GlitchWitch
FalconDarkstar
TheChrisAM
CristinGoodwin
```

:thumbsup: