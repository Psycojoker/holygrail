#!/usr/bin/python
# -*- coding:Utf-8 -*-


import unittest
import tododb

class MaTest(unittest.TestCase):
    def test_create_a_db(self):
        tododb.connect()
        tododb.drop_db()
        tododb.create_db()

if __name__ == "__main__":
   unittest.main()

