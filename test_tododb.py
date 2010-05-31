#!/usr/bin/python
# -*- coding:Utf-8 -*-


import unittest
import tododb

class MaTest(unittest.TestCase):
    def reinitialise(self):
        tododb.connect()
        tododb.drop_db()
        tododb.create_db()

    def test_create_a_db(self):
        self.reinitialise()

    def test_add_a_todo(self):
        self.reinitialise()


if __name__ == "__main__":
   unittest.main()

