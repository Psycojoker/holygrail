#!/usr/bin/python
# -*- coding:Utf-8 -*-

"""
This file is part of Toudoudone.

Toudoudone is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Toudoudone is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Toudoudone.  If not, see <http://www.gnu.org/licenses/>.

Toudoudone  Copyright (C) 2010  Laurent Peuch <cortex@worlddomination.be>
"""

import unittest

from datetime import date, datetime, timedelta

from tdd import TodoDB, TodoDoesntExist, TableAlreadyExist, CanRemoveTheDefaultContext, ContextDoesntExist, ContextStillHasTodos, _Context

class Test_TDD(unittest.TestCase):

    def reinitialise(self):
        """
        Reinitialise the db to make test with a clean one
        Use a sqlite db in memory to avoid losing user/dev data
        """
        tododb = TodoDB('sqlite:/:memory:')
        tododb.drop_db()
        tododb.create_db()
        return tododb

    def test_connect_to_another_database(self):
        TodoDB("sqlite:/:memory:")

    def test_add_a_todo(self):
        """
        You should be able to add a new todo.
        This should inscrease the number of todos by one
        """
        tododb = self.reinitialise()
        was = len(tododb.list_todos())
        todo = tododb.add_todo("This is a new todo")
        self.assertEqual(was + 1, len(tododb.list_todos()))
        self.assertTrue(todo in tododb.list_todos())

        # check if we can add two time a todo with the same description
        todo2 = tododb.add_todo("This is a new todo")
        self.assertEqual(was + 2, len(tododb.list_todos()))
        self.assertTrue(todo in tododb.list_todos())
        self.assertTrue(todo2 in tododb.list_todos())

    def test_add_todo_unique(self):
        tododb = self.reinitialise()
        todo = tododb.add_todo("This is a new todo")
        self.assertEqual(-1, tododb.add_todo("This is a new todo", unique=True))

    def test_get_todo_by_desc(self):
        tododb = self.reinitialise()

        t1 = tododb.add_todo("This is a new todo")
        t2 = tododb.add_todo("This is a new todo 2")

        self.assertEqual(t1.id, tododb.get_todo_by_desc("This is a new todo")[0].id)
        self.assertEqual(t2.id, tododb.get_todo_by_desc("This is a new todo 2")[0].id)

    def test_get_todo_by_desc_mutiple(self):
        tododb = self.reinitialise()

        t1 = tododb.add_todo("This is a new todo")
        t2 = tododb.add_todo("This is a new todo")

        self.assertTrue(t1 in tododb.get_todo_by_desc("This is a new todo"))
        self.assertTrue(t2 in tododb.get_todo_by_desc("This is a new todo"))

    def test_get_todo_by_desc_should_raise_an_exection_if_todo_doesnt_exist(self):
        tododb = self.reinitialise()
        self.assertRaises(TodoDoesntExist, tododb.get_todo_by_desc, "todo")

    def test_remove_todo(self):
        tododb = self.reinitialise()

        was = len(tododb.list_todos())
        todo = tododb.add_todo("This is a new todo")

        self.assertEqual(was + 1, len(tododb.list_todos()))

        id = todo.id
        todo.remove()

        self.assertEqual(was, len(tododb.list_todos()))
        self.assertRaises(TodoDoesntExist, tododb.get_todo, id)

    def test_seach_for_todo(self):
        tododb = self.reinitialise()

        todo_to_add = ("new todo", "another todo", "yet a todo", "tododo", "todotodo")
        todo_to_add_that_doesnt_match = ("blabla", "foo", "bar")

        true = [tododb.add_todo(i) for i in todo_to_add]
        false = [tododb.add_todo(i) for i in todo_to_add_that_doesnt_match]
        result = tododb.search_for_todo("todo")

        self.assertEqual(len(todo_to_add), len(result))

        for i in result:
            self.assertTrue(i.description in todo_to_add)
            self.assertTrue(i in true)
            self.assertFalse(i.description in todo_to_add_that_doesnt_match)
            self.assertFalse(i in false)

    def test_get_todo(self):
        tododb = self.reinitialise()
        todo = tododb.add_todo("todo")
        self.assertTrue(todo is tododb.get_todo(todo.id))
        self.assertEqual(todo.description, "todo")

    def test_get_todo_throw_except_if_doesnt_exist(self):
        tododb = self.reinitialise()
        self.assertRaises(TodoDoesntExist, tododb.get_todo_by_desc, "haha I don't exist")

    def test_rename_todo(self):
        tododb = self.reinitialise()
        todo = tododb.add_todo("first name")
        todo.rename("second name")
        self.assertEqual(todo.description, "second name")

    def test_toggle_todo(self):
        tododb = self.reinitialise()

        t = tododb.add_todo("prout")

        self.assertFalse(t.completed)
        t.toggle()
        self.assertTrue(t.completed)
        t.toggle()
        self.assertFalse(t.completed)

    def test_list_todos(self):
        tododb = self.reinitialise()
        # empty
        self.assertEqual(0, len(tododb.list_todos()))
        t = tododb.add_todo("todo")
        # one todo
        self.assertEqual(1, len(tododb.list_todos()))
        self.assertTrue(t in tododb.list_todos())
        # two todo
        t2 = tododb.add_todo("todo 2")
        self.assertEqual(2, len(tododb.list_todos()))
        self.assertTrue(t in tododb.list_todos())
        self.assertTrue(t2 in tododb.list_todos())
        # only uncompleted
        t2.toggle()
        self.assertEqual(1, len(tododb.list_todos()))
        self.assertTrue(t in tododb.list_todos())
        self.assertTrue(t2 not in tododb.list_todos())
        # everything
        self.assertEqual(2, len(tododb.list_todos(all_todos=True)))
        self.assertTrue(t in tododb.list_todos(all_todos=True))
        self.assertTrue(t2 in tododb.list_todos(all_todos=True))

    def test_todo_should_be_created_today(self):
        tododb = self.reinitialise()
        todo = tododb.add_todo("this is a todo")
        self.assertEqual(todo.created_at, date.today())

    def test_todo_completion_date(self):
        tododb = self.reinitialise()
        todo = tododb.add_todo("this is a todo")
        self.assertEqual(todo.completed_at, None)
        todo.toggle()
        self.assertEqual(todo.completed_at, date.today())
        todo.toggle()
        self.assertEqual(todo.completed_at, None)
        todo.toggle()
        self.assertEqual(todo.completed_at, date.today())
        todo.toggle()
        self.assertEqual(todo.completed_at, None)

    def test_new_todo_shouldnt_have_tickler_by_default(self):
        tododb = self.reinitialise()
        todo = tododb.add_todo("new todo")
        self.assertEquals(None, todo.tickler)

    def test_tickler_at_creation(self):
        tododb = self.reinitialise()
        tickler = datetime(2010, 06, 25)
        todo = tododb.add_todo("new todo", tickler=tickler)
        self.assertEqual(tickler, todo.tickler)

    def test_add_tickle(self):
        tododb = self.reinitialise()
        tickler = datetime(2010, 06, 25)
        todo = tododb.add_todo("new todo")
        todo.tickle(tickler)
        self.assertEqual(tickler, todo.tickler)

    def test_list_dont_show_tickle_task(self):
        tododb = self.reinitialise()
        # for tomorrow
        tickler = datetime.now() + timedelta(1)
        todo = tododb.add_todo("new todo", tickler)
        self.assertTrue(todo not in tododb.list_todos())

    def test_list_all_show_tickle_task(self):
        tododb = self.reinitialise()
        # for tomorrow
        tickler = datetime.now() - timedelta(1)
        todo = tododb.add_todo("new todo", tickler)
        self.assertTrue(todo in tododb.list_todos())

    def test_due_date_at_creation(self):
        tododb = self.reinitialise()
        due = datetime(2010, 06, 25)
        todo = tododb.add_todo("new todo", due=due)
        self.assertEqual(due, todo.due)

    def test_add_due(self):
        tododb = self.reinitialise()
        due = datetime(2010, 06, 25)
        todo = tododb.add_todo("new todo")
        todo.due_for(due)
        self.assertEqual(due, todo.due)

    def test_tdd_should_have_a_context_at_creation(self):
        tododb = self.reinitialise()
        self.assertEqual("default context", _Context.get(1).description)
        self.assertEqual(1, _Context.select().count())

    def test_create_raise_if_table_already_exist(self):
        tododb = self.reinitialise()
        self.assertRaises(TableAlreadyExist, tododb.create_db)

    def test_add_context(self):
        tododb = self.reinitialise()
        context = tododb.add_context("new context")
        self.assertEqual(context.description, "new context")
        self.assertEqual(2, _Context.select().count())

    def test_rename_context(self):
        tododb = self.reinitialise()
        _Context.get(1).rename("new description")
        self.assertEqual("new description", _Context.get(1).description)

    def test_remove_context(self):
        tododb = self.reinitialise()
        self.assertEqual(1, _Context.select().count())
        context = tododb.add_context("new context")
        self.assertEqual(2, _Context.select().count())
        context.remove()
        self.assertEqual(1, _Context.select().count())

    def test_default_context_at_init(self):
        tododb = self.reinitialise()
        context = tododb.get_default_context()
        self.assertEqual(1, context.id)
        self.assertEqual(True, context.default_context)

    def test_change_default_context(self):
        tododb = self.reinitialise()
        context = tododb.add_context("new context")
        context.set_default()
        self.assertEqual(context.default_context, True)

    def test_their_should_only_be_one_default_context(self):
        tododb = self.reinitialise()
        previous = tododb.get_default_context()
        context = tododb.add_context("new context")
        context.set_default()
        self.assertEqual(False, previous.default_context)
        self.assertEqual(context, tododb.get_default_context())
        self.assertEqual(1, _Context.select(_Context.q.default_context == True).count())

    def test_cant_remove_default_context(self):
        tododb = self.reinitialise()
        # to avoid having the exception NeedAtLeastOneContext if the exception we are waiting isn't raised
        # yes it will crash anyway
        tododb.add_context("prout")
        self.assertRaises(CanRemoveTheDefaultContext, tododb.get_default_context().remove)

    def test_a_todo_should_have_the_default_context(self):
        tododb = self.reinitialise()
        todo = tododb.add_todo("a todo")
        self.assertEqual(todo.context, tododb.get_default_context())
        todo = tododb.add_todo("another todo")
        self.assertEqual(todo.context, tododb.get_default_context())

    def test_get_context_by_desc(self):
        tododb = self.reinitialise()
        context = tododb.add_context("youpla")
        self.assertEqual(context, tododb.get_context_by_desc("youpla")[0])

    def test_get_context_by_desc_raise_if_dont_exist(self):
        tododb = self.reinitialise()
        self.assertRaises(ContextDoesntExist, tododb.get_context_by_desc, "I don't exist")

    def test_get_context(self):
        tododb = self.reinitialise()
        context = tododb.add_context("zoubiboulba suce mon zob")
        self.assertEqual(context, tododb.get_context(context.id))

    def test_get_context_raise_if_dont_exist(self):
        tododb = self.reinitialise()
        self.assertRaises(ContextDoesntExist, tododb.get_context, 1337)

    def test_add_todo_with_special_context(self):
        tododb = self.reinitialise()
        context = tododb.add_context("je devrais aller dormir")
        todo = tododb.add_todo("mouhaha", context=context.id)
        self.assertEqual(context, todo.context)

    def test_change_todo_context(self):
        tododb = self.reinitialise()
        context = tododb.add_context("je vais encore me coucher à pas d'heure ...")
        todo = tododb.add_todo("aller dormir")
        todo.change_context(context.id)
        self.assertEqual(context, todo.context)

    def test_cant_delete_context_with_todos(self):
        tododb = self.reinitialise()
        context = tododb.add_context("TDD rosk")
        todo = tododb.add_todo("HAHAHA I'M USING TEH INTERNETZ", context=context)
        self.assertRaises(ContextStillHasTodos, context.remove)

    def test_list_contexts(self):
        tododb = self.reinitialise()
        self.assertTrue(tododb.get_default_context() in tododb.list_contexts())
        self.assertEqual(len(tododb.list_contexts()), 1)
        context = tododb.add_context("foobar")
        self.assertEqual(len(tododb.list_contexts()), 2)
        context.remove()
        self.assertEqual(len(tododb.list_contexts()), 1)

    def test_add_Context_default(self):
        tododb = self.reinitialise()
        context = tododb.add_context("zomg, ils ont osé faire un flim sur les schtroumphs", default=True)
        self.assertEqual(context, tododb.get_default_context())
        self.assertTrue(context.default_context)

    def test_context_should_have_a_creation_date(self):
        tododb = self.reinitialise()
        context = tododb.add_context("les fils de teuphu c'est super")
        self.assertEqual(date.today(), context.created_at)

    def test_add_project(self):
        tododb = self.reinitialise()
        project = tododb.add_project("project apocalypse")
        self.assertEqual("project apocalypse", project.description)

    def test_get_project(self):
        tododb = self.reinitialise()
        project = tododb.add_project("project manatan")
        self.assertEqual(project, tododb.get_project(project.id))

if __name__ == "__main__":
   unittest.main()

