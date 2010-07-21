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

from tdd import TodoDB, TodoDoesntExist, TableAlreadyExist, CanRemoveTheDefaultContext, ContextDoesntExist, ContextStillHasTodos, _Context, ProjectDoesntExist, _Todo, _Project, _Item, ItemDoesntExist

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

    def test_add_todo_unique_toggle(self):
        tododb = self.reinitialise()
        todo = tododb.add_todo("This is a new todo")
        todo.toggle()
        self.assertNotEqual(-1, tododb.add_todo("This is a new todo", unique=True))

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
        self.assertRaises(TodoDoesntExist, tododb.get_todo, 1337)

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
        tickler = datetime.now() + timedelta(1)
        todo = tododb.add_todo("new todo", tickler)
        self.assertTrue(todo in tododb.list_todos(all_todos=True))

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

    def test_get_project_raise_if_dont_exist(self):
        tododb = self.reinitialise()
        self.assertRaises(ProjectDoesntExist, tododb.get_project, 42)

    def test_get_project_by_desc(self):
        tododb = self.reinitialise()
        project = tododb.add_project("acheter du saucisson")
        self.assertEqual(tododb.get_project_by_desc("acheter du saucisson")[0], project)
        self.assertEqual(len(tododb.get_project_by_desc("acheter du saucisson")), 1)
        tododb.add_project("acheter du saucisson")
        self.assertEqual(len(tododb.get_project_by_desc("acheter du saucisson")), 2)
        self.assertEqual(len(tododb.get_project_by_desc("acheter des cornichons")), 0)

    def test_rename_project(self):
        tododb = self.reinitialise()
        project = tododb.add_project("j'ai envie de chocolat")
        project.rename("the cake is a lie")
        self.assertEqual(project.description, "the cake is a lie")

    def test_list_projects(self):
        tododb = self.reinitialise()
        self.assertEqual(0, len(tododb.list_projects()))
        project = tododb.add_project("ce truc a l'air super http://smarterware.org/6172/hilary-mason-how-to-replace-yourself-with-a-small-shell-script")
        self.assertTrue(project in tododb.list_projects())
        self.assertEqual(1, len(tododb.list_projects()))

    def test_remove_project(self):
        tododb = self.reinitialise()
        self.assertEqual(0, len(tododb.list_projects()))
        project = tododb.add_project("lovely code vortex")
        self.assertEqual(1, len(tododb.list_projects()))
        old_id = project.id
        project.remove()
        self.assertRaises(ProjectDoesntExist, tododb.get_project, old_id)
        self.assertEqual(0, len(tododb.list_projects()))

    def test_change_todo_project(self):
        tododb = self.reinitialise()
        project = tododb.add_project("manger une pomme")
        todo = tododb.add_todo("le nouveau leak d'ACTA est dégeulasse")
        todo.change_project(project.id)
        self.assertEqual(todo.project, project)

    def test_next_todo(self):
        tododb = self.reinitialise()
        todo1 = tododb.add_todo("first todo")
        todo2 = tododb.add_todo("second todo")
        todo2.wait_for(todo1)
        self.assertEqual(todo1, todo2.previous_todo)

    def test_list_todo_with_previous_todo(self):
        tododb = self.reinitialise()
        todo1 = tododb.add_todo("first todo")
        todo2 = tododb.add_todo("second todo")
        todo2.wait_for(todo1)
        self.assertTrue(todo2 not in tododb.list_todos())

    def test_list_todo_with_previous_todo_with_completed(self):
        tododb = self.reinitialise()
        todo1 = tododb.add_todo("first todo")
        todo2 = tododb.add_todo("second todo")
        todo2.wait_for(todo1)
        todo1.toggle()
        self.assertTrue(todo2 in tododb.list_todos())

    def test_add_todo_wait_for(self):
        tododb = self.reinitialise()
        todo1 = tododb.add_todo("first todo")
        todo2 = tododb.add_todo("second todo", wait_for=todo1.id)
        self.assertEqual(todo1, todo2.previous_todo)

    def test_add_todo_with_a_project(self):
        tododb = self.reinitialise()
        project = tododb.add_project("gare a Gallo")
        todo = tododb.add_todo("first todo", project=project.id)
        self.assertEqual(project, todo.project)

    def test_project_should_have_a_creation_date(self):
        tododb = self.reinitialise()
        project = tododb.add_project("youplaboum")
        self.assertEqual(project.created_at, date.today())

    def test_set_default_context_to_project(self):
        tododb = self.reinitialise()
        project = tododb.add_project("youmi, I love chocolate")
        context = tododb.add_context("pc")
        project.set_default_context(context.id)
        self.assertEqual(context, project.default_context)

    def test_set_default_context_to_project_at_creation(self):
        tododb = self.reinitialise()
        context = tododb.add_context("pc")
        project = tododb.add_project("youmi, I love chocolate", default_context=context.id)
        self.assertEqual(context, project.default_context)

    def test_new_todo_with_project_with_default_context(self):
        tododb = self.reinitialise()
        context = tododb.add_context("pc")
        project = tododb.add_project("youmi, I love chocolate", default_context=context.id)
        todo = tododb.add_todo("pataplouf", project=project.id)
        self.assertEqual(todo.context, context)

    def test_new_todo_with_project_with_default_context_and_context(self):
        tododb = self.reinitialise()
        context = tododb.add_context("pc")
        other_context = tododb.add_context("mouhaha")
        project = tododb.add_project("youmi, I love chocolate", default_context=context.id)
        todo = tododb.add_todo("pataplouf", context=other_context, project=project.id)
        self.assertEqual(todo.context, other_context)

    def test_set_hide_context(self):
        tododb = self.reinitialise()
        context = tododb.add_context("pc")
        self.assertFalse(context.hide)
        context.toggle_hide()
        self.assertTrue(context.hide)
        context.toggle_hide()
        self.assertFalse(context.hide)
        context.toggle_hide()
        self.assertTrue(context.hide)

    def test_hide_context_in_list_context(self):
        tododb = self.reinitialise()
        context = tododb.add_context("pc")
        self.assertTrue(context in tododb.list_contexts())
        context.toggle_hide()
        self.assertFalse(context in tododb.list_contexts())

    def test_context_hide_at_creation(self):
        tododb = self.reinitialise()
        context = tododb.add_context("pc", hide=True)
        self.assertTrue(context.hide)

    def test_hide_context_in_list_todo(self):
        tododb = self.reinitialise()
        context = tododb.add_context("pc", hide=True)
        todo = tododb.add_todo("atchoum", context=context)
        self.assertFalse(todo in tododb.list_todos())
        self.assertTrue(todo in tododb.list_todos(all_todos=True))

    def test_list_todo_with_previous_todo_with_deleted(self):
        tododb = self.reinitialise()
        todo1 = tododb.add_todo("first todo")
        todo2 = tododb.add_todo("second todo")
        todo2.wait_for(todo1)
        todo1.remove()
        self.assertTrue(todo2 in tododb.list_todos())
        self.assertEqual(None, todo2.previous_todo)

    def test_remove_project_with_todos(self):
        tododb = self.reinitialise()
        project = tododb.add_project("tchikaboum")
        todo = tododb.add_todo("arakiri", project=project.id)
        todo2 = tododb.add_todo("arakirikiki", project=project.id)
        project.remove()
        self.assertEqual(None, todo.project)
        self.assertEqual(None, todo2.project)

    def test_auto_create_tables(self):
        TodoDB('sqlite:/:memory:').drop_db()
        TodoDB('sqlite:/:memory:')
        self.assertTrue(_Todo.tableExists())
        self.assertTrue(_Context.tableExists())
        self.assertTrue(_Project.tableExists())

    def test_context_position(self):
        tododb = self.reinitialise()
        context = tododb.get_default_context()
        self.assertEqual(0, context.position)

    def test_new_context_position(self):
        tododb = self.reinitialise()
        context = tododb.add_context("In Dublin fair city ...")
        self.assertEqual(1, context.position)
        context = tododb.add_context("where the girl are so pretty ...")
        self.assertEqual(2, context.position)

    def test_change_context_position_alone_default_to_max(self):
        tododb = self.reinitialise()
        context1 = tododb.get_default_context()
        context1.change_position(4)
        self.assertEqual(0, context1.position)

    def test_change_context_position_2_contexts_no_change(self):
        tododb = self.reinitialise()
        context1 = tododb.get_default_context()
        context2 = tododb.add_context("context2")
        context1.change_position(0)
        self.assertEqual(0, context1.position)
        self.assertEqual(1, context2.position)

    def test_change_context_position_2_contexts(self):
        tododb = self.reinitialise()
        context1 = tododb.get_default_context()
        context2 = tododb.add_context("context2")
        context1.change_position(1)
        self.assertEqual(1, context1.position)
        self.assertEqual(0, context2.position)

    def test_change_context_position_2_contexts_default_to_max(self):
        tododb = self.reinitialise()
        context1 = tododb.get_default_context()
        context2 = tododb.add_context("context2")
        context1.change_position(4)
        self.assertEqual(1, context1.position)
        self.assertEqual(0, context2.position)

    def test_change_context_position_2_contexts_swap(self):
        tododb = self.reinitialise()
        context1 = tododb.get_default_context()
        context2 = tododb.add_context("context2")
        context2.change_position(0)
        self.assertEqual(0, context2.position)
        self.assertEqual(1, context1.position)

    def test_change_context_position_2_contexts_swap_reverse(self):
        tododb = self.reinitialise()
        context1 = tododb.get_default_context()
        context2 = tododb.add_context("context2")
        context1.change_position(1)
        self.assertEqual(0, context2.position)
        self.assertEqual(1, context1.position)

    def test_change_context_position_2_contexts_swap_reverse_default_to_max(self):
        tododb = self.reinitialise()
        context1 = tododb.get_default_context()
        context2 = tododb.add_context("context2")
        context1.change_position(6)
        self.assertEqual(0, context2.position)
        self.assertEqual(1, context1.position)

    def test_change_context_position_3_contexts(self):
        tododb = self.reinitialise()
        context1 = tododb.get_default_context()
        context2 = tododb.add_context("context2")
        context3 = tododb.add_context("context3")
        context1.change_position(6)
        self.assertEqual(1, context3.position)
        self.assertEqual(0, context2.position)
        self.assertEqual(2, context1.position)

    def test_change_context_position_3_contexts_full(self):
        tododb = self.reinitialise()
        context1 = tododb.get_default_context()
        context2 = tododb.add_context("context2")
        context3 = tododb.add_context("context3")
        context2.change_position(6)
        self.assertEqual(1, context3.position)
        self.assertEqual(2, context2.position)
        self.assertEqual(0, context1.position)
        context1.change_position(6)
        self.assertEqual(0, context3.position)
        self.assertEqual(1, context2.position)
        self.assertEqual(2, context1.position)
        context3.change_position(6)
        self.assertEqual(2, context3.position)
        self.assertEqual(0, context2.position)
        self.assertEqual(1, context1.position)
        context3.change_position(0)
        self.assertEqual(0, context3.position)
        self.assertEqual(1, context2.position)
        self.assertEqual(2, context1.position)
        context2.change_position(1)
        self.assertEqual(0, context3.position)
        self.assertEqual(1, context2.position)
        self.assertEqual(2, context1.position)

    def test_change_context_position_6_contexts(self):
        tododb = self.reinitialise()
        context1 = tododb.get_default_context()
        context1.rename("context1")
        context2 = tododb.add_context("context2")
        context3 = tododb.add_context("context3")
        context4 = tododb.add_context("context4")
        context5 = tododb.add_context("context5")
        context6 = tododb.add_context("context6")
        context1.change_position(4)
        self.assertEqual(4, context1.position)
        self.assertEqual(0, context2.position)
        self.assertEqual(1, context3.position)
        self.assertEqual(2, context4.position)
        self.assertEqual(3, context5.position)
        self.assertEqual(5, context6.position)

    def test_list_project_by_position(self):
        tododb = self.reinitialise()
        context1 = tododb.get_default_context()
        context1.rename("context1")
        context2 = tododb.add_context("context2")
        context3 = tododb.add_context("context3")
        context4 = tododb.add_context("context4")
        context5 = tododb.add_context("context5")
        context6 = tododb.add_context("context6")
        context1.change_position(4)
        contexts = tododb.list_contexts()
        self.assertEqual(contexts[4], context1)
        self.assertEqual(contexts[0], context2)
        self.assertEqual(contexts[1], context3)
        self.assertEqual(contexts[2], context4)
        self.assertEqual(contexts[3], context5)
        self.assertEqual(contexts[5], context6)

    def test_project_hide(self):
        tododb = self.reinitialise()
        project = tododb.add_project("lalala")
        self.assertFalse(project.hide)
        project.toggle_hide()
        self.assertTrue(project.hide)
        project.toggle_hide()
        self.assertFalse(project.hide)

    def test_list_todo_with_project_hide(self):
        tododb = self.reinitialise()
        project = tododb.add_project("qsd")
        project.toggle_hide()
        todo = tododb.add_todo("toto", project=project.id)
        self.assertFalse(todo in tododb.list_todos())
        self.assertTrue(todo in tododb.list_todos(all_todos=True))

    def test_list_project_and_project_hide(self):
        tododb = self.reinitialise()
        project = tododb.add_project("huhu")
        project.toggle_hide()
        self.assertFalse(project in tododb.list_projects())

    def test_list_all_projects(self):
        tododb = self.reinitialise()
        project = tododb.add_project("huhu")
        self.assertTrue(project in tododb.list_projects())
        self.assertTrue(project in tododb.list_projects(all_projects=True))
        project.toggle_hide()
        self.assertFalse(project in tododb.list_projects())
        self.assertTrue(project in tododb.list_projects(all_projects=True))

    def test_add_item(self):
        tododb = self.reinitialise()
        was = _Item.select().count()
        item = tododb.add_item("This is a new item")
        self.assertEqual(item.description, "This is a new item")
        self.assertEqual(was + 1, _Item.select().count())

        # check if we can add two time a todo with the same description
        item2 = tododb.add_item("This is a new item")
        self.assertEqual(was + 2, _Item.select().count())

    def test_get_item_by_desc(self):
        tododb = self.reinitialise()

        t1 = tododb.add_item("This is a new item")
        t2 = tododb.add_item("This is a new item 2")

        self.assertEqual(t1.id, tododb.get_item_by_desc("This is a new item")[0].id)
        self.assertEqual(t2.id, tododb.get_item_by_desc("This is a new item 2")[0].id)

    def test_get_item_by_desc_mutiple(self):
        tododb = self.reinitialise()

        t1 = tododb.add_item("This is a new item")
        t2 = tododb.add_item("This is a new item")

        self.assertTrue(t1 in tododb.get_item_by_desc("This is a new item"))
        self.assertTrue(t2 in tododb.get_item_by_desc("This is a new item"))

    def test_get_item_by_desc_should_raise_an_exection_if_todo_doesnt_exist(self):
        tododb = self.reinitialise()
        self.assertRaises(ItemDoesntExist, tododb.get_item_by_desc, "toto")

    def test_remove_item(self):
        tododb = self.reinitialise()
        was = _Item.select().count()
        item = tododb.add_item("This is a new item")
        self.assertEqual(was + 1, _Item.select().count())
        item.remove()
        self.assertEqual(was, _Item.select().count())

    def test_get_item(self):
        tododb = self.reinitialise()
        item = tododb.add_item("item")
        self.assertTrue(item is tododb.get_item(item.id))
        self.assertEqual(item.description, "item")

    def test_get_item_throw_except_if_doesnt_exist(self):
        tododb = self.reinitialise()
        self.assertRaises(ItemDoesntExist, tododb.get_item, 35)

    def test_rename_item(self):
        tododb = self.reinitialise()
        item = tododb.add_item("first name")
        item.rename("second name")
        self.assertEqual(item.description, "second name")

    def test_list_items(self):
        tododb = self.reinitialise()
        # empty
        self.assertEqual(0, len(tododb.list_items()))
        item = tododb.add_item("item")
        # one todo
        self.assertEqual(1, len(tododb.list_items()))
        self.assertTrue(item in tododb.list_items())
        # two todo
        t2 = tododb.add_item("item 2")
        self.assertEqual(2, len(tododb.list_items()))
        self.assertTrue(item in tododb.list_items())
        self.assertTrue(t2 in tododb.list_items())

    def test_item_should_be_created_today(self):
        tododb = self.reinitialise()
        item = tododb.add_item("this is a item")
        self.assertEqual(item.created_at, date.today())

    def test_new_item_shouldnt_have_tickler_by_default(self):
        tododb = self.reinitialise()
        item = tododb.add_item("new item")
        self.assertEquals(None, item.tickler)

    def test_item_tickler_at_creation(self):
        tododb = self.reinitialise()
        tickler = datetime(2010, 06, 25)
        item = tododb.add_item("new item", tickler=tickler)
        self.assertEqual(tickler, item.tickler)

    def test_item_add_tickle(self):
        tododb = self.reinitialise()
        tickler = datetime(2010, 06, 25)
        item = tododb.add_item("new item")
        item.tickle(tickler)
        self.assertEqual(tickler, item.tickler)

    def test_list_dont_show_tickle_item(self):
        tododb = self.reinitialise()
        # for tomorrow
        tickler = datetime.now() + timedelta(1)
        item = tododb.add_item("new item", tickler=tickler)
        self.assertTrue(item not in tododb.list_items())

    def test_list_all_show_tickle_items(self):
        tododb = self.reinitialise()
        # for tomorrow
        tickler = datetime.now() + timedelta(1)
        item = tododb.add_item("new item", tickler)
        self.assertTrue(item in tododb.list_items(all_items=True))

    def test_a_item_should_have_the_default_context(self):
        tododb = self.reinitialise()
        item = tododb.add_item("a item")
        self.assertEqual(item.context, tododb.get_default_context())
        item = tododb.add_item("another item")
        self.assertEqual(item.context, tododb.get_default_context())

    # def test_project_completion(self):
    # def test_todo_with_project_completion(self):
    # def test_project_completion_date(self):
    # def test_project_tickler(self):
    # def tet_main_view(self):

    # TODO: refactorer les exceptions, favoriser un message plutôt que plein d'exceptions différentes
    # TODO: faire un utils.py et rajouter plein de petits outils dedans comme un parseur de date etc ...
    # TODO: faire marcher sd <- migrer vers lucid
    # TODO: peut être donner une méthode Todo pour dire si elle s'affiche
    # TODO: tien et si je faisais un nouveau attribut "drop" en plus de completed
    # TODO: réorganiser les méthodes pour les grouper de manière similaire (par add, par list etc ...)

if __name__ == "__main__":
   unittest.main()

