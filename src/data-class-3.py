#!/usr/bin/env python3
# coding: utf8
from dataclasses import dataclass, field, Field
from typing import Generic, TypeVar, Tuple, List
# Python 3.9からはtypingを使った表現は非推奨。代わりにlistなどの組み込み型を使う。
@dataclass
class Record:
    item_ids: List[int]
if __name__ == '__main__':
    args = [1,2,3]
    Record(args)
    args = ['A','B']
    Record(args)
