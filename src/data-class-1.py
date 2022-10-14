#!/usr/bin/env python3
# coding: utf8
import unittest
import dataclasses
from dataclasses import dataclass, field, Field
from decimal import Decimal
from datetime import datetime, date, time
import types
@dataclass
class Record:
    id: int
    name: str
    birth: datetime 
    value: Decimal


if __name__ == '__main__':
    def test_init_args_0(self):
        id = 1
        name = 'A'
        birth = datetime.now()
        value = Decimal('0.1')
        r = Record(id, name, birth, value)
    def test_init_args_1(self):
        args = [1, 'A', datetime.now(), Decimal('0.1')]
        r = Record(*args)
    def test_init_kwargs_0(self):
        kwargs = {'id': 1, 'name': 'A', 'birth': datetime.now(), 'value': Decimal('0.1')}
        r = Record(**kwargs)
    def test_init_args_error_0(self):
        r = Record(*[1, 'A'])
    print(dir(Record))
    print(Record.__annotations__)
    print(Record.__dataclass_fields__)
    test_init_args_error_0()
