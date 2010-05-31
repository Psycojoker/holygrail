#!/usr/bin/python
# -*- coding:Utf-8 -*-


import unittest
from tododb import TodoDB

class MaTest(unittest.TestCase):

    def reinitialise(self):
        tododb = TodoDB()
        tododb.connect()
        tododb.drop_db()
        tododb.create_db()
        return tododb

    def test_create_a_db(self):
        tododb = self.reinitialise()

    def test_add_a_todo(self):
        tododb = self.reinitialise()

        was = tododb.todo_len()

        tododb.add_todo("This is a new todo")

        self.assertEqual(was + 1, tododb.todo_len())

if __name__ == "__main__":
   unittest.main()

