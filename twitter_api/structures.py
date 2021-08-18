from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any

from pyutils.my_dataclasses import JsonDataclass


@dataclass
class AccessTokenResponse(JsonDataclass):
    oauth_token: str
    oauth_token_secret: str
    user_id: int
    screen_name: str


@dataclass
class IdsResult(JsonDataclass):
    ids: list[int]
    next_cursor: int
    next_cursor_str: str
    previous_cursor: int
    previous_cursor_str: str
    total_count: Optional[int] = None


@dataclass
class Url(JsonDataclass):
    url: str
    expanded_url: str
    display_url: str
    indices: list[int]


@dataclass
class UserUrl(JsonDataclass):
    urls: list[Url]


@dataclass
class Description(JsonDataclass):
    urls: list[Url]


@dataclass
class UserEntities(JsonDataclass):
    description: Description
    url: Optional[UserUrl] = None


@dataclass
class StatusEntities(JsonDataclass):
    hashtags: list[Any]
    symbols: list[Any]
    user_mentions: list[UserMention]
    urls: list[Any]
    media: Optional[list[Media]] = None


@dataclass
class Status(JsonDataclass):
    created_at: str
    id: int
    id_str: str
    truncated: bool
    entities: StatusEntities
    source: str
    in_reply_to_status_id: Any
    in_reply_to_status_id_str: Any
    in_reply_to_user_id: Any
    in_reply_to_user_id_str: Any
    in_reply_to_screen_name: Any
    geo: Any
    coordinates: Any
    place: Any
    contributors: Any
    is_quote_status: bool
    retweet_count: int
    favorite_count: int
    favorited: bool
    retweeted: bool
    lang: str
    user: Optional[User]
    possibly_sensitive: Optional[bool] = None
    retweeted_status: Optional[Status] = None
    quoted_status_id: Optional[int] = None
    quoted_status_id_str: Optional[str] = None
    quoted_status: Optional[Status] = None
    extended_entities: Optional[ExtendedEntities] = None
    text: Optional[str] = None
    full_text: Optional[str] = None
    display_text_range: Optional[list[int]] = None
    quoted_status_permalink: Optional[str] = None


@dataclass
class User(JsonDataclass):
    id: int
    id_str: str
    name: str
    screen_name: str
    location: str
    description: str
    url: str
    entities: UserEntities
    protected: bool
    followers_count: int
    friends_count: int
    listed_count: int
    created_at: str
    favourites_count: int
    utc_offset: Any
    time_zone: Any
    geo_enabled: bool
    verified: bool
    statuses_count: int
    lang: Any
    contributors_enabled: bool
    is_translator: bool
    is_translation_enabled: bool
    profile_background_color: str
    profile_background_image_url: str
    profile_background_image_url_https: str
    profile_background_tile: bool
    profile_image_url: str
    profile_image_url_https: str
    profile_link_color: str
    profile_sidebar_border_color: str
    profile_sidebar_fill_color: str
    profile_text_color: str
    profile_use_background_image: bool
    has_extended_profile: bool
    default_profile: bool
    default_profile_image: bool
    following: bool
    follow_request_sent: bool
    notifications: bool
    translator_type: str
    status: Optional[Status] = None
    profile_banner_url: Optional[str] = None
    profile_location: Optional[str] = None
    suspended: Optional[bool] = None
    needs_phone_verification: Optional[bool] = None
    muting: Optional[bool] = None
    withheld_in_countries: Optional[list[Any]] = None


@dataclass
class SearchMetadata(JsonDataclass):
    completed_in: float
    max_id: int
    mad_id_str: str
    next_results: str
    query: str
    count: int
    since_id: int
    since_id_str: str


@dataclass
class SearchTweetsResponse(JsonDataclass):
    statuses: list[Status]
    search_metadata: SearchMetadata


@dataclass
class MediaSizeSpecifier(JsonDataclass):
    w: str
    h: str
    resize: str


@dataclass
class MediaSize(JsonDataclass):
    thumb: MediaSizeSpecifier
    media: MediaSizeSpecifier
    large: MediaSizeSpecifier
    small: MediaSizeSpecifier


@dataclass
class Media(JsonDataclass):
    id: int
    id_str: str
    indices: list[int]
    media_url: str
    media_url_https: str
    url: str
    display_url: str
    expanded_url: str
    type: str
    sizes: MediaSize


@dataclass
class ExtendedEntities:
    media: list[Media]


@dataclass
class UserMention(JsonDataclass):
    screen_name: str
    name: str
    id: int
    id_str: str
    indices: list[int]
