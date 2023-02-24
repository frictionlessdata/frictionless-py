from __future__ import annotations
from typing import List
from typing_extensions import Required, TypedDict


class IInquiry(TypedDict, total=False):
    tasks: Required[List[IInquiryTask]]


class IInquiryTask(TypedDict, total=False):
    pass
