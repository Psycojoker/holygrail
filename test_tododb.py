#!/usr/bin/python
# -*- coding:Utf-8 -*-

import unittest
from tododb import TodoDB, TodoAlreadyExist, TodoDoesntExist

class MaTest(unittest.TestCase):

    def reinitialise(self):
        """
        Reinitialise the db to make test with a clean one
        """
        tododb = TodoDB()
        tododb.drop_db()
        tododb.create_db()
        return tododb

    def test_create_a_db(self):
        """
        create a clean database to test
        """
        tododb = self.reinitialise()

    def test_add_a_todo(self):
        """
        You should be able to add a new todo.
        This should inscrease the number of todos by one
        """
        tododb = self.reinitialise()

        was = tododb.todo_len()

        tododb.add_todo("This is a new todo")

        self.assertEqual(was + 1, tododb.todo_len())

    def test_cant_add_two_time_the_same_todo(self):
        """
        You shouldn't be able to add two time a todo with the same description
        """
        tododb = self.reinitialise()

        was = tododb.todo_len()

        tododb.add_todo("This is a new todo")

        self.assertEqual(was + 1, tododb.todo_len())

        self.assertRaises(TodoAlreadyExist, tododb.add_todo, "This is a new todo")

    def test_raise_if_todo_already_exist_multiple_time(self):
        tododb = self.reinitialise()

        was = tododb.todo_len()

        tododb.add_todo("This is a new todo")

        self.assertEqual(was + 1, tododb.todo_len())
        tododb._Todo(description="This is a new todo")
        self.assertEqual(was + 2, tododb.todo_len())

        self.assertRaises(AssertionError, tododb.add_todo, "This is a new todo")

    def test_remove_todo_from_description(self):
        tododb = self.reinitialise()

        was = tododb.todo_len()
        tododb.add_todo("This is a new todo")
        self.assertEqual(was + 1, tododb.todo_len())
        tododb.remove_todo("This is a new todo")
        self.assertEqual(was, tododb.todo_len())

    def test_get_todo_id(self):
        tododb = self.reinitialise()

        tododb.add_todo("This is a new todo")
        tododb.add_todo("This is a new todo 2")

        self.assertEqual(1, tododb.get_todo_id("This is a new todo"))
        self.assertEqual(2, tododb.get_todo_id("This is a new todo 2"))

    def test_remove_todo_from_id(self):
        tododb = self.reinitialise()

        was = tododb.todo_len()
        tododb.add_todo("This is a new todo")

        self.assertEqual(was + 1, tododb.todo_len())

        id = tododb.get_todo_id("This is a new todo")
        tododb.remove_todo(id)

        self.assertEqual(was, tododb.todo_len())

    def test_remove_should_raise_an_exception_if_todo_doesnt_exist(self):
        tododb = self.reinitialise()

        self.assertRaises(TodoDoesntExist, tododb.remove_todo, "This is a new todo")

    def test_remove_should_raise_an_exception_if_todo_doesnt_exist_from_id(self):
        tododb = self.reinitialise()

        self.assertRaises(TodoDoesntExist, tododb.remove_todo, 3)

    def test_remove_should_raise_an_assert_if_multiple_todo_exist(self):
        tododb = self.reinitialise()

        was = tododb.todo_len()

        tododb.add_todo("This is a new todo")

        self.assertEqual(was + 1, tododb.todo_len())
        tododb._Todo(description="This is a new todo")
        self.assertEqual(was + 2, tododb.todo_len())

        self.assertRaises(AssertionError, tododb.remove_todo, "This is a new todo")

if __name__ == "__main__":
   unittest.main()

