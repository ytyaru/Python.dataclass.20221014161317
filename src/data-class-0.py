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
    id: int = 0
    name: str = ''
    birth: datetime = datetime.now()
    value: Decimal = Decimal('0.0')


if __name__ == '__main__':
    print(Record())
    print(Record(1, 'A'))
    print(Record(name='B', value=Decimal('9.9')))

