#!/usr/bin/env python3
# coding: utf8
import unittest
import dataclasses
from dataclasses import dataclass, field, Field
from decimal import Decimal
from datetime import datetime, date, time
import types
from typing import Generic, TypeVar, Tuple, List
@dataclass
class Record:
    item_ids: List[int] # list でなく List にしてみたが同じ。中の型をチェックしてくれない。
class TestDataClass(unittest.TestCase):
    def setUp(self): pass
    def tearDown(self): pass
    def test_print_dict(self):
        print(Record.__dict__)
    def test_annotations(self):
        self.assertEqual(['item_ids'], list(Record.__annotations__.keys()))
        self.assertEqual([List[int]], list(Record.__annotations__.values()))
    def test_dataclass_fields(self):
        self.assertEqual(['item_ids'], list(Record.__dataclass_fields__.keys()))
        self.assertEqual('item_ids', Record.__dataclass_fields__['item_ids'].name)
        self.assertEqual(List[int], Record.__dataclass_fields__['item_ids'].type)
        self.assertEqual(dataclasses._MISSING_TYPE, type(Record.__dataclass_fields__['item_ids'].default))
        self.assertEqual(dataclasses._MISSING_TYPE, type(Record.__dataclass_fields__['item_ids'].default_factory))
        self.assertEqual(types.MappingProxyType, type(Record.__dataclass_fields__['item_ids'].metadata))
    def test_init_missing_required_args(self):
        msg = "Record.__init__() missing 1 required positional argument: 'item_ids'"
        with self.assertRaises(TypeError) as cm:
            Record()
        self.assertEqual(msg, cm.exception.args[0])
    def test_init_args_0(self):
        item_ids = [1, 2, 3]
        r = Record(item_ids)
        self.assertEqual(item_ids, r.item_ids)
    def test_init_args_1(self):
        args = [[1, 2, 3]]
        r = Record(*args)
        self.assertEqual(args[0], r.item_ids)
    def test_init_kwargs_0(self):
        kwargs = {'item_ids': [1, 2, 3]}
        r = Record(**kwargs)
        self.assertEqual(kwargs['item_ids'], r.item_ids)
    def test_init_args_error_generic_type(self): # これパスされちゃ困るんだが……
        item_ids = [1, 2, 'A']
        r = Record(item_ids)
        self.assertEqual(item_ids, r.item_ids)
    

if __name__ == '__main__':
    unittest.main()
