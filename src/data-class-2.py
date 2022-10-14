#!/usr/bin/env python3
# coding: utf8
from dataclasses import dataclass, field, Field
@dataclass
class Record:
    item_ids: list[int]
if __name__ == '__main__':
    args = [1,2,3]
    Record(args)
    args = ['A','B']
    Record(args)
