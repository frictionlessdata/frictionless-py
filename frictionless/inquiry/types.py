from __future__ import annotations

from typing import List

from typing_extensions import Required, TypedDict


class IInquiry(TypedDict, total=False):
    name: str
    type: str
    title: str
    description: str
    tasks: Required[List[IInquiryTask]]


class IInquiryTask(TypedDict, total=False):
    name: str
    type: str
    title: str
    description: str
