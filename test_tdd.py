#!/usr/bin/python
# -*- coding:Utf-8 -*-

import unittest
from tdd import TodoDB, TodoAlreadyExist, TodoDoesntExist

class MaTest(unittest.TestCase):

    def reinitialise(self):
        """
        Reinitialise the db to make test with a clean one
        """
        tododb = TodoDB('sqlite:/:memory:')
        tododb.drop_db()
        tododb.create_db()
        return tododb

    def test_create_a_db(self):
        """
        create a clean database to test
        """
        tododb = self.reinitialise()

    def test_connect(self):
        TodoDB()

    def test_connect_to_another_database(self):
        TodoDB("sqlite:/file")

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

    def test_get_todo_id(self):
        tododb = self.reinitialise()

        tododb.add_todo("This is a new todo")
        tododb.add_todo("This is a new todo 2")

        self.assertEqual(1, tododb.get_todo_id("This is a new todo"))
        self.assertEqual(2, tododb.get_todo_id("This is a new todo 2"))

    def test_get_todo_id_should_raise_an_exection_if_todo_doesnt_exist(self):
        tododb = self.reinitialise()

        self.assertRaises(TodoDoesntExist, tododb.get_todo_id, "todo")

    def test_remove_todo(self):
        tododb = self.reinitialise()

        was = tododb.todo_len()
        tododb.add_todo("This is a new todo")

        self.assertEqual(was + 1, tododb.todo_len())

        id = tododb.get_todo_id("This is a new todo")
        tododb.remove_todo(id)

        self.assertEqual(was, tododb.todo_len())

    def test_remove_should_raise_an_exception_if_todo_doesnt_exist(self):
        tododb = self.reinitialise()

        self.assertRaises(TodoDoesntExist, tododb.remove_todo, 3)

    def test_todo_len(self):
        tododb = self.reinitialise()
        self.assertEqual(0, tododb.todo_len())
        tododb.add_todo("New todo")
        self.assertEqual(1, tododb.todo_len())
        tododb.add_todo("New todo 2")
        self.assertEqual(2, tododb.todo_len())
        tododb.remove_todo(1)
        self.assertEqual(1, tododb.todo_len())
        tododb.remove_todo(2)
        self.assertEqual(0, tododb.todo_len())

    def test_seach_for_todo(self):
        tododb = self.reinitialise()

        todo_to_add = ("new todo", "another todo", "yet a todo", "tododo", "todotodo")
        todo_to_add_that_doesnt_match = ("blabla", "foo", "bar")

        for i in todo_to_add:
            tododb.add_todo(i)

        for i in todo_to_add_that_doesnt_match:
            tododb.add_todo(i)

        result = tododb.search_for_todo("todo")

        self.assertEqual(len(todo_to_add), len(result))

        for i in result:
            self.assertTrue(i["description"] in todo_to_add)

    def test_get_todo(self):
        tododb = self.reinitialise()

        tododb.add_todo("todo")

        todo = tododb.get_todo("todo")

        self.assertEqual(todo.id, 1)

        self.assertEqual(todo.description, "todo")

    def test_get_todo_should_return_the_created_todo(self):
        tododb = self.reinitialise()

        todo = tododb.add_todo("todo")

        self.assertEqual(todo.description, "todo")

    def test_get_todo_throw_except_if_doesnt_exist(self):
        tododb = self.reinitialise()

        self.assertRaises(TodoDoesntExist, tododb.get_todo, "haha I don't exist")

    def test_rename_todo(self):
        tododb = self.reinitialise()

        t = tododb.add_todo("first name")

        tododb.rename_todo(t.id, "second name")

        self.assertEqual(t.description, "second name")

    def test_rename_todo_should_raise_exception_if_doesnt_exist(self):
        tododb = self.reinitialise()

        self.assertRaises(TodoDoesntExist, tododb.rename_todo, 15, "haha I don't exist")

if __name__ == "__main__":
   unittest.main()

