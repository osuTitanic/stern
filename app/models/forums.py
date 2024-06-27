
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from .user import UserModel

class IconModel(BaseModel):
    id: int
    name: str
    location: str

class PostModel(BaseModel):
    id: int
    topic_id: int
    forum_id: int
    user_id: int
    content: str
    created_at: datetime
    edit_time: datetime
    edit_count: int
    edit_locked: bool
    deleted: bool
    user: UserModel

class TopicModel(BaseModel):
    id: int
    forum_id: int
    creator_id: int
    icon_id: Optional[int]
    title: str
    status_text: Optional[str]
    views: int
    announcement: bool
    pinned: bool
    created_at: datetime
    last_post_at: datetime
    locked_at: Optional[datetime]
    creator: UserModel
    icon: Optional[IconModel]

class SubforumModel(BaseModel):
    id: int
    parent_id: Optional[int]
    created_at: datetime
    name: str
    description: str

class ForumModel(BaseModel):
    id: int
    parent_id: Optional[int]
    created_at: datetime
    name: str
    description: str
    subforums: List[SubforumModel]
    parent: Optional[SubforumModel]

class BookmarkModel(BaseModel):
    user: UserModel
    topic: TopicModel

class SubscriptionModel(BaseModel):
    user: UserModel
    topic: TopicModel
