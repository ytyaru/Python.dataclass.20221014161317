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
    birth: datetime = field(metadata={'DF':'CURRENT_TIMESTAMP'})
    value: Decimal
    _ = field(default=None, metadata={'UK':'id name'})
    #_: None = field(default=None, metadata={'UK':'id name'})

# fieldのmetadataは辞書型のみセット可能。しかも読取専用

class TestDataClass(unittest.TestCase):
    def setUp(self): pass
    def tearDown(self): pass
    def test_print_dict(self):
        print(Record.__dict__)
        #print(Record.__annotations__)
        #print(Record.__dataclass_fields__)
    def test_annotations(self):
        self.assertEqual(['id', 'name', 'birth', 'value', '_'], list(Record.__annotations__.keys()))
        self.assertEqual([int, str, datetime, Decimal, None], list(Record.__annotations__.values()))
    def test_dataclass_fields(self):
        self.assertEqual(['id', 'name', 'birth', 'value', '_'], list(Record.__dataclass_fields__.keys()))
        self.assertEqual('id', Record.__dataclass_fields__['id'].name)
        self.assertEqual(int, Record.__dataclass_fields__['id'].type)
        self.assertEqual(dataclasses._MISSING_TYPE, type(Record.__dataclass_fields__['id'].default))
        self.assertEqual(dataclasses._MISSING_TYPE, type(Record.__dataclass_fields__['id'].default_factory))
        self.assertEqual(types.MappingProxyType, type(Record.__dataclass_fields__['id'].metadata))
    def test_missing_type(self):
        dataclasses._MISSING_TYPE
    def test_init_missing_required_args(self):
        msg = "Record.__init__() missing 4 required positional arguments: 'id', 'name', 'birth', and 'value'"
        with self.assertRaises(TypeError) as cm:
        #with self.assertRaises(TypeError, msg=f"TypeError: Record.__init__() missing 4 required positional arguments: 'id', 'name', 'birth', and 'value'") as cm:
            Record()
        self.assertEqual(msg, cm.exception.args[0])
    def test_init_args_0(self):
        id = 1
        name = 'A'
        birth = datetime.now()
        value = Decimal('0.1')
        r = Record(id, name, birth, value)
        self.assertEqual(id, r.id)
        self.assertEqual(name, r.name)
        self.assertEqual(birth, r.birth)
        self.assertEqual(value, r.value)
    def test_init_args_1(self):
        args = [1, 'A', datetime.now(), Decimal('0.1')]
        r = Record(*args)
        self.assertEqual(args[0], r.id)
        self.assertEqual(args[1], r.name)
        self.assertEqual(args[2], r.birth)
        self.assertEqual(args[3], r.value)
    def test_init_kwargs_0(self):
        kwargs = {'id': 1, 'name': 'A', 'birth': datetime.now(), 'value': Decimal('0.1')}
        r = Record(**kwargs)
        self.assertEqual(kwargs['id'], r.id)
        self.assertEqual(kwargs['name'], r.name)
        self.assertEqual(kwargs['birth'], r.birth)
        self.assertEqual(kwargs['value'], r.value)


if __name__ == '__main__':
    unittest.main()
