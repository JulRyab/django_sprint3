from typing import TypeVar, Union

from blogicum.tests.adapters.post import PostModelAdapter
from blogicum.tests.adapters.user import UserModelAdapter

CommentModelAdapterT = TypeVar("CommentModelAdapterT", bound=type)
ModelAdapterT = Union[CommentModelAdapterT, PostModelAdapter, UserModelAdapter]
