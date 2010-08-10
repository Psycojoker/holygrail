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

import unittest, time

from datetime import date, datetime, timedelta

from tdd import TodoDB, TodoDoesntExist, TableAlreadyExist, CanRemoveTheDefaultContext, ContextDoesntExist, ContextStillHasElems, _Context, ProjectDoesntExist, _Todo, _Project, _Item, ItemDoesntExist, WaitForError

def comp_datetime(a, b):
    if a.year != b.year:
        return False
    if a.month != b.month:
        return False
    if a.day != b.day:
        return False
    if a.hour != b.hour:
        return False
    if a.second - b.second > 2:
        return False
    return True

class Test_TDD(unittest.TestCase):

    def setUp(self):
        self.tododb = self.reinitialise()

    def test_connect_to_another_database(self):
        TodoDB("sqlite:/:memory:")

    def reinitialise(self):
        """
        Reinitialise the db to make test with a clean one
        Use a sqlite db in memory to avoid losing user/dev data
        """
        self.tododb = TodoDB('sqlite:/:memory:')
        self.tododb.drop_db()
        self.tododb.create_db()
        return self.tododb

    #def test_connect_to_another_database(self):
        #TodoDB("sqlite:/:memory:")

    def test_add_a_todo(self):
        """
        You should be able to add a new todo.
        This should inscrease the number of todos by one
        """
        was = len(self.tododb.list_todos())
        todo = self.tododb.add_todo("This is a new todo")
        self.assertEqual(was + 1, len(self.tododb.list_todos()))
        self.assertTrue(todo in self.tododb.list_todos())

        # check if we can add two time a todo with the same description
        todo2 = self.tododb.add_todo("This is a new todo")
        self.assertEqual(was + 2, len(self.tododb.list_todos()))
        self.assertTrue(todo in self.tododb.list_todos())
        self.assertTrue(todo2 in self.tododb.list_todos())

    def test_add_todo_unique(self):
        todo = self.tododb.add_todo("This is a new todo")
        self.assertEqual(-1, self.tododb.add_todo("This is a new todo", unique=True))

    def test_add_todo_unique_toggle(self):
        todo = self.tododb.add_todo("This is a new todo")
        todo.toggle()
        self.assertNotEqual(-1, self.tododb.add_todo("This is a new todo", unique=True))

    def test_get_todo_by_desc(self):

        t1 = self.tododb.add_todo("This is a new todo")
        t2 = self.tododb.add_todo("This is a new todo 2")

        self.assertEqual(t1.id, self.tododb.get_todo_by_desc("This is a new todo")[0].id)
        self.assertEqual(t2.id, self.tododb.get_todo_by_desc("This is a new todo 2")[0].id)

    def test_get_todo_by_desc_mutiple(self):

        t1 = self.tododb.add_todo("This is a new todo")
        t2 = self.tododb.add_todo("This is a new todo")

        self.assertTrue(t1 in self.tododb.get_todo_by_desc("This is a new todo"))
        self.assertTrue(t2 in self.tododb.get_todo_by_desc("This is a new todo"))

    def test_get_todo_by_desc_should_raise_an_exection_if_todo_doesnt_exist(self):
        self.assertRaises(TodoDoesntExist, self.tododb.get_todo_by_desc, "todo")

    def test_remove_todo(self):

        was = len(self.tododb.list_todos())
        todo = self.tododb.add_todo("This is a new todo")

        self.assertEqual(was + 1, len(self.tododb.list_todos()))

        id = todo.id
        todo.remove()

        self.assertEqual(was, len(self.tododb.list_todos()))
        self.assertRaises(TodoDoesntExist, self.tododb.get_todo, id)

    def test_seach_for_todo(self):

        todo_to_add = ("new todo", "another todo", "yet a todo", "tododo", "todotodo")
        todo_to_add_that_doesnt_match = ("blabla", "foo", "bar")

        true = [self.tododb.add_todo(i) for i in todo_to_add]
        false = [self.tododb.add_todo(i) for i in todo_to_add_that_doesnt_match]
        result = self.tododb.search_for_todo("todo")

        self.assertEqual(len(todo_to_add), len(result))

        for i in result:
            self.assertTrue(i.description in todo_to_add)
            self.assertTrue(i in true)
            self.assertFalse(i.description in todo_to_add_that_doesnt_match)
            self.assertFalse(i in false)

    def test_get_todo(self):
        todo = self.tododb.add_todo("todo")
        self.assertTrue(todo is self.tododb.get_todo(todo.id))
        self.assertEqual(todo.description, "todo")

    def test_get_todo_throw_except_if_doesnt_exist(self):
        self.assertRaises(TodoDoesntExist, self.tododb.get_todo, 1337)

    def test_rename_todo(self):
        todo = self.tododb.add_todo("first name")
        todo.rename("second name")
        self.assertEqual(todo.description, "second name")

    def test_toggle_todo(self):

        t = self.tododb.add_todo("prout")

        self.assertFalse(t.completed)
        t.toggle()
        self.assertTrue(t.completed)
        t.toggle()
        self.assertFalse(t.completed)

    def test_list_todos(self):
        # empty
        self.assertEqual(0, len(self.tododb.list_todos()))
        t = self.tododb.add_todo("todo")
        # one todo
        self.assertEqual(1, len(self.tododb.list_todos()))
        self.assertTrue(t in self.tododb.list_todos())
        # two todo
        t2 = self.tododb.add_todo("todo 2")
        self.assertEqual(2, len(self.tododb.list_todos()))
        self.assertTrue(t in self.tododb.list_todos())
        self.assertTrue(t2 in self.tododb.list_todos())
        # only uncompleted
        t2.toggle()
        self.assertEqual(1, len(self.tododb.list_todos()))
        self.assertTrue(t in self.tododb.list_todos())
        self.assertTrue(t2 not in self.tododb.list_todos())
        # everything
        self.assertEqual(2, len(self.tododb.list_todos(all_todos=True)))
        self.assertTrue(t in self.tododb.list_todos(all_todos=True))
        self.assertTrue(t2 in self.tododb.list_todos(all_todos=True))

    def test_todo_should_be_created_today(self):
        todo = self.tododb.add_todo("this is a todo")
        self.assertEqual(todo.created_at, date.today())

    def test_todo_completion_date(self):
        todo = self.tododb.add_todo("this is a todo")
        self.assertEqual(todo.completed_at, None)
        todo.toggle()
        self.assertTrue(comp_datetime(todo.completed_at, datetime.now()))
        todo.toggle()
        self.assertEqual(todo.completed_at, None)
        todo.toggle()
        self.assertTrue(comp_datetime(todo.completed_at, datetime.now()))
        todo.toggle()
        self.assertEqual(todo.completed_at, None)

    def test_new_todo_shouldnt_have_tickler_by_default(self):
        todo = self.tododb.add_todo("new todo")
        self.assertEquals(None, todo.tickler)

    def test_tickler_at_creation(self):
        tickler = datetime(2010, 06, 25)
        todo = self.tododb.add_todo("new todo", tickler=tickler)
        self.assertEqual(tickler, todo.tickler)

    def test_add_tickle(self):
        tickler = datetime(2010, 06, 25)
        todo = self.tododb.add_todo("new todo")
        todo.tickle(tickler)
        self.assertEqual(tickler, todo.tickler)

    def test_list_dont_show_tickle_task(self):
        # for tomorrow
        tickler = datetime.now() + timedelta(1)
        todo = self.tododb.add_todo("new todo", tickler)
        self.assertTrue(todo not in self.tododb.list_todos())

    def test_list_all_show_tickle_task(self):
        # for tomorrow
        tickler = datetime.now() + timedelta(1)
        todo = self.tododb.add_todo("new todo", tickler)
        self.assertTrue(todo in self.tododb.list_todos(all_todos=True))

    def test_due_date_at_creation(self):
        due = datetime(2010, 06, 25)
        todo = self.tododb.add_todo("new todo", due=due)
        self.assertEqual(due, todo.due)

    def test_add_due(self):
        due = datetime(2010, 06, 25)
        todo = self.tododb.add_todo("new todo")
        todo.due_for(due)
        self.assertEqual(due, todo.due)

    def test_tdd_should_have_a_context_at_creation(self):
        self.assertEqual("default context", _Context.get(1).description)
        self.assertEqual(1, _Context.select().count())

    def test_create_raise_if_table_already_exist(self):
        self.assertRaises(TableAlreadyExist, self.tododb.create_db)

    def test_add_context(self):
        context = self.tododb.add_context("new context")
        self.assertEqual(context.description, "new context")
        self.assertEqual(2, _Context.select().count())

    def test_rename_context(self):
        _Context.get(1).rename("new description")
        self.assertEqual("new description", _Context.get(1).description)

    def test_remove_context(self):
        self.assertEqual(1, _Context.select().count())
        context = self.tododb.add_context("new context")
        self.assertEqual(2, _Context.select().count())
        context.remove()
        self.assertEqual(1, _Context.select().count())

    def test_default_context_at_init(self):
        context = self.tododb.get_default_context()
        self.assertEqual(1, context.id)
        self.assertEqual(True, context.default_context)

    def test_change_default_context(self):
        context = self.tododb.add_context("new context")
        context.set_default()
        self.assertEqual(context.default_context, True)

    def test_their_should_only_be_one_default_context(self):
        previous = self.tododb.get_default_context()
        context = self.tododb.add_context("new context")
        context.set_default()
        self.assertEqual(False, previous.default_context)
        self.assertEqual(context, self.tododb.get_default_context())
        self.assertEqual(1, _Context.select(_Context.q.default_context == True).count())

    def test_cant_remove_default_context(self):
        # to avoid having the exception NeedAtLeastOneContext if the exception we are waiting isn't raised
        # yes it will crash anyway
        self.tododb.add_context("prout")
        self.assertRaises(CanRemoveTheDefaultContext, self.tododb.get_default_context().remove)

    def test_a_todo_should_have_the_default_context(self):
        todo = self.tododb.add_todo("a todo")
        self.assertEqual(todo.context, self.tododb.get_default_context())
        todo = self.tododb.add_todo("another todo")
        self.assertEqual(todo.context, self.tododb.get_default_context())

    def test_get_context_by_desc(self):
        context = self.tododb.add_context("youpla")
        self.assertEqual(context, self.tododb.get_context_by_desc("youpla")[0])

    def test_get_context_by_desc_raise_if_dont_exist(self):
        self.assertRaises(ContextDoesntExist, self.tododb.get_context_by_desc, "I don't exist")

    def test_get_context(self):
        context = self.tododb.add_context("zoubiboulba suce mon zob")
        self.assertEqual(context, self.tododb.get_context(context.id))

    def test_get_context_raise_if_dont_exist(self):
        self.assertRaises(ContextDoesntExist, self.tododb.get_context, 1337)

    def test_add_todo_with_special_context(self):
        context = self.tododb.add_context("je devrais aller dormir")
        todo = self.tododb.add_todo("mouhaha", context=context.id)
        self.assertEqual(context, todo.context)

    def test_change_todo_context(self):
        context = self.tododb.add_context("je vais encore me coucher à pas d'heure ...")
        todo = self.tododb.add_todo("aller dormir")
        todo.change_context(context.id)
        self.assertEqual(context, todo.context)

    def test_cant_delete_context_with_todos(self):
        context = self.tododb.add_context("TDD rosk")
        todo = self.tododb.add_todo("HAHAHA I'M USING TEH INTERNETZ", context=context)
        self.assertRaises(ContextStillHasElems, context.remove)

    def test_list_contexts(self):
        self.assertTrue(self.tododb.get_default_context() in self.tododb.list_contexts())
        self.assertEqual(len(self.tododb.list_contexts()), 1)
        context = self.tododb.add_context("foobar")
        self.assertEqual(len(self.tododb.list_contexts()), 2)
        context.remove()
        self.assertEqual(len(self.tododb.list_contexts()), 1)

    def test_add_Context_default(self):
        context = self.tododb.add_context("zomg, ils ont osé faire un flim sur les schtroumphs", default=True)
        self.assertEqual(context, self.tododb.get_default_context())
        self.assertTrue(context.default_context)

    def test_context_should_have_a_creation_date(self):
        context = self.tododb.add_context("les fils de teuphu c'est super")
        self.assertEqual(date.today(), context.created_at)

    def test_add_project(self):
        project = self.tododb.add_project("project apocalypse")
        self.assertEqual("project apocalypse", project.description)

    def test_get_project(self):
        project = self.tododb.add_project("project manatan")
        self.assertEqual(project, self.tododb.get_project(project.id))

    def test_get_project_raise_if_dont_exist(self):
        self.assertRaises(ProjectDoesntExist, self.tododb.get_project, 42)

    def test_get_project_by_desc(self):
        project = self.tododb.add_project("acheter du saucisson")
        self.assertEqual(self.tododb.get_project_by_desc("acheter du saucisson")[0], project)
        self.assertEqual(len(self.tododb.get_project_by_desc("acheter du saucisson")), 1)
        self.tododb.add_project("acheter du saucisson")
        self.assertEqual(len(self.tododb.get_project_by_desc("acheter du saucisson")), 2)
        self.assertEqual(len(self.tododb.get_project_by_desc("acheter des cornichons")), 0)

    def test_rename_project(self):
        project = self.tododb.add_project("j'ai envie de chocolat")
        project.rename("the cake is a lie")
        self.assertEqual(project.description, "the cake is a lie")

    def test_list_projects(self):
        self.assertEqual(0, len(self.tododb.list_projects()))
        project = self.tododb.add_project("ce truc a l'air super http://smarterware.org/6172/hilary-mason-how-to-replace-yourself-with-a-small-shell-script")
        self.assertTrue(project in self.tododb.list_projects())
        self.assertEqual(1, len(self.tododb.list_projects()))

    def test_remove_project(self):
        self.assertEqual(0, len(self.tododb.list_projects()))
        project = self.tododb.add_project("lovely code vortex")
        self.assertEqual(1, len(self.tododb.list_projects()))
        old_id = project.id
        project.remove()
        self.assertRaises(ProjectDoesntExist, self.tododb.get_project, old_id)
        self.assertEqual(0, len(self.tododb.list_projects()))

    def test_change_todo_project(self):
        project = self.tododb.add_project("manger une pomme")
        todo = self.tododb.add_todo("le nouveau leak d'ACTA est dégeulasse")
        todo.change_project(project.id)
        self.assertEqual(todo.project, project)

    def test_next_todo(self):
        todo1 = self.tododb.add_todo("first todo")
        todo2 = self.tododb.add_todo("second todo")
        todo2.wait_for(todo1)
        self.assertEqual(todo1, todo2.previous_todo)

    def test_list_todo_with_previous_todo(self):
        todo1 = self.tododb.add_todo("first todo")
        todo2 = self.tododb.add_todo("second todo")
        todo2.wait_for(todo1)
        self.assertTrue(todo2 not in self.tododb.list_todos())

    def test_list_todo_with_previous_todo_with_completed(self):
        todo1 = self.tododb.add_todo("first todo")
        todo2 = self.tododb.add_todo("second todo")
        todo2.wait_for(todo1)
        todo1.toggle()
        self.assertTrue(todo2 in self.tododb.list_todos())

    def test_add_todo_wait_for(self):
        todo1 = self.tododb.add_todo("first todo")
        todo2 = self.tododb.add_todo("second todo", wait_for=todo1.id)
        self.assertEqual(todo1, todo2.previous_todo)

    def test_add_todo_with_a_project(self):
        project = self.tododb.add_project("gare a Gallo")
        todo = self.tododb.add_todo("first todo", project=project.id)
        self.assertEqual(project, todo.project)

    def test_project_should_have_a_creation_date(self):
        project = self.tododb.add_project("youplaboum")
        self.assertEqual(project.created_at, date.today())

    def test_set_default_context_to_project(self):
        project = self.tododb.add_project("youmi, I love chocolate")
        context = self.tododb.add_context("pc")
        project.set_default_context(context.id)
        self.assertEqual(context, project.default_context)

    def test_set_default_context_to_project_at_creation(self):
        context = self.tododb.add_context("pc")
        project = self.tododb.add_project("youmi, I love chocolate", default_context=context.id)
        self.assertEqual(context, project.default_context)

    def test_new_todo_with_project_with_default_context(self):
        context = self.tododb.add_context("pc")
        project = self.tododb.add_project("youmi, I love chocolate", default_context=context.id)
        todo = self.tododb.add_todo("pataplouf", project=project.id)
        self.assertEqual(todo.context, context)

    def test_new_todo_with_project_with_default_context_and_context(self):
        context = self.tododb.add_context("pc")
        other_context = self.tododb.add_context("mouhaha")
        project = self.tododb.add_project("youmi, I love chocolate", default_context=context.id)
        todo = self.tododb.add_todo("pataplouf", context=other_context, project=project.id)
        self.assertEqual(todo.context, other_context)

    def test_set_hide_context(self):
        context = self.tododb.add_context("pc")
        self.assertFalse(context.hide)
        context.toggle_hide()
        self.assertTrue(context.hide)
        context.toggle_hide()
        self.assertFalse(context.hide)
        context.toggle_hide()
        self.assertTrue(context.hide)

    def test_hide_context_in_list_context(self):
        context = self.tododb.add_context("pc")
        self.assertTrue(context in self.tododb.list_contexts())
        context.toggle_hide()
        self.assertFalse(context in self.tododb.list_contexts())

    def test_list_all_contexts(self):
        context = self.tododb.add_context("pc", hide=True)
        self.assertFalse(context in self.tododb.list_contexts())
        self.assertTrue(context in self.tododb.list_contexts(all_contexts=True))

    def test_context_hide_at_creation(self):
        context = self.tododb.add_context("pc", hide=True)
        self.assertTrue(context.hide)

    def test_hide_context_in_list_todo(self):
        context = self.tododb.add_context("pc", hide=True)
        todo = self.tododb.add_todo("atchoum", context=context)
        self.assertFalse(todo in self.tododb.list_todos())
        self.assertTrue(todo in self.tododb.list_todos(all_todos=True))

    def test_list_todo_with_previous_todo_with_deleted(self):
        todo1 = self.tododb.add_todo("first todo")
        todo2 = self.tododb.add_todo("second todo")
        todo2.wait_for(todo1)
        todo1.remove()
        self.assertTrue(todo2 in self.tododb.list_todos())
        self.assertEqual(None, todo2.previous_todo)

    def test_remove_project_with_todos(self):
        project = self.tododb.add_project("tchikaboum")
        todo = self.tododb.add_todo("arakiri", project=project.id)
        todo2 = self.tododb.add_todo("arakirikiki", project=project.id)
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
        context = self.tododb.get_default_context()
        self.assertEqual(0, context.position)

    def test_new_context_position(self):
        context = self.tododb.add_context("In Dublin fair city ...")
        self.assertEqual(1, context.position)
        context = self.tododb.add_context("where the girl are so pretty ...")
        self.assertEqual(2, context.position)

    def test_change_context_position_alone_default_to_max(self):
        context1 = self.tododb.get_default_context()
        context1.change_position(4)
        self.assertEqual(0, context1.position)

    def test_change_context_position_2_contexts_no_change(self):
        context1 = self.tododb.get_default_context()
        context2 = self.tododb.add_context("context2")
        context1.change_position(0)
        self.assertEqual(0, context1.position)
        self.assertEqual(1, context2.position)

    def test_change_context_position_2_contexts(self):
        context1 = self.tododb.get_default_context()
        context2 = self.tododb.add_context("context2")
        context1.change_position(1)
        self.assertEqual(1, context1.position)
        self.assertEqual(0, context2.position)

    def test_change_context_position_2_contexts_default_to_max(self):
        context1 = self.tododb.get_default_context()
        context2 = self.tododb.add_context("context2")
        context1.change_position(4)
        self.assertEqual(1, context1.position)
        self.assertEqual(0, context2.position)

    def test_change_context_position_2_contexts_swap(self):
        context1 = self.tododb.get_default_context()
        context2 = self.tododb.add_context("context2")
        context2.change_position(0)
        self.assertEqual(0, context2.position)
        self.assertEqual(1, context1.position)

    def test_change_context_position_2_contexts_swap_reverse(self):
        context1 = self.tododb.get_default_context()
        context2 = self.tododb.add_context("context2")
        context1.change_position(1)
        self.assertEqual(0, context2.position)
        self.assertEqual(1, context1.position)

    def test_change_context_position_2_contexts_swap_reverse_default_to_max(self):
        context1 = self.tododb.get_default_context()
        context2 = self.tododb.add_context("context2")
        context1.change_position(6)
        self.assertEqual(0, context2.position)
        self.assertEqual(1, context1.position)

    def test_change_context_position_3_contexts(self):
        context1 = self.tododb.get_default_context()
        context2 = self.tododb.add_context("context2")
        context3 = self.tododb.add_context("context3")
        context1.change_position(6)
        self.assertEqual(1, context3.position)
        self.assertEqual(0, context2.position)
        self.assertEqual(2, context1.position)

    def test_change_context_position_3_contexts_full(self):
        context1 = self.tododb.get_default_context()
        context2 = self.tododb.add_context("context2")
        context3 = self.tododb.add_context("context3")
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
        context1 = self.tododb.get_default_context()
        context1.rename("context1")
        context2 = self.tododb.add_context("context2")
        context3 = self.tododb.add_context("context3")
        context4 = self.tododb.add_context("context4")
        context5 = self.tododb.add_context("context5")
        context6 = self.tododb.add_context("context6")
        context1.change_position(4)
        self.assertEqual(4, context1.position)
        self.assertEqual(0, context2.position)
        self.assertEqual(1, context3.position)
        self.assertEqual(2, context4.position)
        self.assertEqual(3, context5.position)
        self.assertEqual(5, context6.position)

    def test_list_project_by_position(self):
        context1 = self.tododb.get_default_context()
        context1.rename("context1")
        context2 = self.tododb.add_context("context2")
        context3 = self.tododb.add_context("context3")
        context4 = self.tododb.add_context("context4")
        context5 = self.tododb.add_context("context5")
        context6 = self.tododb.add_context("context6")
        context1.change_position(4)
        contexts = self.tododb.list_contexts()
        self.assertEqual(contexts[4], context1)
        self.assertEqual(contexts[0], context2)
        self.assertEqual(contexts[1], context3)
        self.assertEqual(contexts[2], context4)
        self.assertEqual(contexts[3], context5)
        self.assertEqual(contexts[5], context6)

    def test_project_hide(self):
        project = self.tododb.add_project("lalala")
        self.assertFalse(project.hide)
        project.toggle_hide()
        self.assertTrue(project.hide)
        project.toggle_hide()
        self.assertFalse(project.hide)

    def test_project_hide_at_creation(self):
        project = self.tododb.add_project("lalala", hide=True)
        self.assertTrue(project.hide)

    def test_list_todo_with_project_hide(self):
        project = self.tododb.add_project("qsd")
        project.toggle_hide()
        todo = self.tododb.add_todo("toto", project=project.id)
        self.assertFalse(todo in self.tododb.list_todos())
        self.assertTrue(todo in self.tododb.list_todos(all_todos=True))

    def test_list_project_and_project_hide(self):
        project = self.tododb.add_project("huhu")
        project.toggle_hide()
        self.assertFalse(project in self.tododb.list_projects())

    def test_list_all_projects(self):
        project = self.tododb.add_project("huhu")
        self.assertTrue(project in self.tododb.list_projects())
        self.assertTrue(project in self.tododb.list_projects(all_projects=True))
        project.toggle_hide()
        self.assertFalse(project in self.tododb.list_projects())
        self.assertTrue(project in self.tododb.list_projects(all_projects=True))

    def test_add_item(self):
        was = _Item.select().count()
        item = self.tododb.add_item("This is a new item")
        self.assertEqual(item.description, "This is a new item")
        self.assertEqual(was + 1, _Item.select().count())

        # check if we can add two time a todo with the same description
        item2 = self.tododb.add_item("This is a new item")
        self.assertEqual(was + 2, _Item.select().count())

    def test_get_item_by_desc(self):

        t1 = self.tododb.add_item("This is a new item")
        t2 = self.tododb.add_item("This is a new item 2")

        self.assertEqual(t1.id, self.tododb.get_item_by_desc("This is a new item")[0].id)
        self.assertEqual(t2.id, self.tododb.get_item_by_desc("This is a new item 2")[0].id)

    def test_get_item_by_desc_mutiple(self):

        t1 = self.tododb.add_item("This is a new item")
        t2 = self.tododb.add_item("This is a new item")

        self.assertTrue(t1 in self.tododb.get_item_by_desc("This is a new item"))
        self.assertTrue(t2 in self.tododb.get_item_by_desc("This is a new item"))

    def test_get_item_by_desc_should_raise_an_exection_if_todo_doesnt_exist(self):
        self.assertRaises(ItemDoesntExist, self.tododb.get_item_by_desc, "toto")

    def test_remove_item(self):
        was = _Item.select().count()
        item = self.tododb.add_item("This is a new item")
        self.assertEqual(was + 1, _Item.select().count())
        item.remove()
        self.assertEqual(was, _Item.select().count())

    def test_get_item(self):
        item = self.tododb.add_item("item")
        self.assertTrue(item is self.tododb.get_item(item.id))
        self.assertEqual(item.description, "item")

    def test_get_item_throw_except_if_doesnt_exist(self):
        self.assertRaises(ItemDoesntExist, self.tododb.get_item, 35)

    def test_rename_item(self):
        item = self.tododb.add_item("first name")
        item.rename("second name")
        self.assertEqual(item.description, "second name")

    def test_list_items(self):
        # empty
        self.assertEqual(0, len(self.tododb.list_items()))
        item = self.tododb.add_item("item")
        # one todo
        self.assertEqual(1, len(self.tododb.list_items()))
        self.assertTrue(item in self.tododb.list_items())
        # two todo
        t2 = self.tododb.add_item("item 2")
        self.assertEqual(2, len(self.tododb.list_items()))
        self.assertTrue(item in self.tododb.list_items())
        self.assertTrue(t2 in self.tododb.list_items())

    def test_item_should_be_created_today(self):
        item = self.tododb.add_item("this is a item")
        self.assertEqual(item.created_at, date.today())

    def test_new_item_shouldnt_have_tickler_by_default(self):
        item = self.tododb.add_item("new item")
        self.assertEquals(None, item.tickler)

    def test_item_tickler_at_creation(self):
        tickler = datetime(2010, 06, 25)
        item = self.tododb.add_item("new item", tickler=tickler)
        self.assertEqual(tickler, item.tickler)

    def test_item_add_tickle(self):
        tickler = datetime(2010, 06, 25)
        item = self.tododb.add_item("new item")
        item.tickle(tickler)
        self.assertEqual(tickler, item.tickler)

    def test_list_dont_show_tickle_item(self):
        # for tomorrow
        tickler = datetime.now() + timedelta(1)
        item = self.tododb.add_item("new item", tickler=tickler)
        self.assertTrue(item not in self.tododb.list_items())

    def test_list_all_show_tickle_items(self):
        # for tomorrow
        tickler = datetime.now() + timedelta(1)
        item = self.tododb.add_item("new item", tickler)
        self.assertTrue(item in self.tododb.list_items(all_items=True))

    def test_a_item_should_have_the_default_context(self):
        item = self.tododb.add_item("a item")
        self.assertEqual(item.context, self.tododb.get_default_context())
        item = self.tododb.add_item("another item")
        self.assertEqual(item.context, self.tododb.get_default_context())

    def test_add_item_with_special_context(self):
        context = self.tododb.add_context("je devrais aller dormir")
        item = self.tododb.add_item("mouhaha", context=context.id)
        self.assertEqual(context, item.context)

    def test_change_item_context(self):
        context = self.tododb.add_context("je vais encore me coucher à pas d'heure ...")
        item = self.tododb.add_item("aller dormir")
        item.change_context(context.id)
        self.assertEqual(context, item.context)

    def test_cant_delete_context_with_items(self):
        context = self.tododb.add_context("TDD rosk")
        item = self.tododb.add_item("HAHAHA I'M USING TEH INTERNETZ", context=context)
        self.assertRaises(ContextStillHasElems, context.remove)

    def test_add_item_with_a_project(self):
        project = self.tododb.add_project("gare a Gallo")
        item = self.tododb.add_item("first item", project=project.id)
        self.assertEqual(project, item.project)

    def test_change_item_project(self):
        project = self.tododb.add_project("manger une pomme")
        item = self.tododb.add_item("le nouveau leak d'ACTA est dégeulasse")
        item.change_project(project.id)
        self.assertEqual(item.project, project)

    def test_next_todo_for_item(self):
        todo = self.tododb.add_todo("todo")
        item = self.tododb.add_item("item")
        item.wait_for(todo)
        self.assertEqual(todo, item.previous_todo)

    def test_list_item_with_previous_todo(self):
        todo = self.tododb.add_todo("todo")
        item = self.tododb.add_item("item")
        item.wait_for(todo)
        self.assertTrue(item not in self.tododb.list_items())

    def test_list_item_with_previous_todo_with_completed(self):
        todo = self.tododb.add_todo("first todo")
        item = self.tododb.add_item("second todo")
        item.wait_for(todo)
        todo.toggle()
        self.assertTrue(item in self.tododb.list_items())

    def test_add_item_wait_for(self):
        todo = self.tododb.add_todo("first todo")
        item = self.tododb.add_item("second item", wait_for=todo.id)
        self.assertEqual(todo, item.previous_todo)

    def test_new_item_with_project_with_default_context(self):
        context = self.tododb.add_context("pc")
        project = self.tododb.add_project("youmi, I love chocolate", default_context=context.id)
        item = self.tododb.add_item("pataplouf", project=project.id)
        self.assertEqual(item.context, context)

    def test_new_item_with_project_with_default_context_and_context(self):
        context = self.tododb.add_context("pc")
        other_context = self.tododb.add_context("mouhaha")
        project = self.tododb.add_project("youmi, I love chocolate", default_context=context.id)
        item = self.tododb.add_item("pataplouf", context=other_context, project=project.id)
        self.assertEqual(item.context, other_context)

    def test_list_item_with_previous_item_with_deleted(self):
        todo = self.tododb.add_todo("todo")
        item = self.tododb.add_item("item")
        item.wait_for(todo)
        todo.remove()
        self.assertTrue(item in self.tododb.list_items())
        self.assertEqual(None, item.previous_todo)

    def test_remove_project_with_items(self):
        project = self.tododb.add_project("tchikaboum")
        item = self.tododb.add_item("arakiri", project=project.id)
        item2 = self.tododb.add_item("arakirikiki", project=project.id)
        project.remove()
        self.assertEqual(None, item.project)
        self.assertEqual(None, item2.project)

    def test_list_item_with_project_hide(self):
        project = self.tododb.add_project("qsd")
        project.toggle_hide()
        item = self.tododb.add_item("toto", project=project.id)
        self.assertFalse(item in self.tododb.list_items())
        self.assertTrue(item in self.tododb.list_items(all_items=True))

    def test_hide_context_in_list_item(self):
        context = self.tododb.add_context("pc", hide=True)
        item = self.tododb.add_item("atchoum", context=context)
        self.assertFalse(item in self.tododb.list_items())
        self.assertTrue(item in self.tododb.list_items(all_items=True))

    def test_project_completion(self):
        project = self.tododb.add_project("bah")
        self.assertFalse(project.completed)
        project.toggle()
        self.assertTrue(project.completed)
        project.toggle()
        self.assertFalse(project.completed)

    def test_project_completion_date(self):
        project = self.tododb.add_project("yamakasi")
        project.toggle()
        self.assertTrue(comp_datetime(datetime.now(), project.completed_at))
        project.toggle()
        self.assertEqual(None, project.completed_at)

    def test_todo_with_project_completion(self):
        project = self.tododb.add_project("the wild rover")
        todo = self.tododb.add_todo("s", project=project.id)
        project.toggle()
        self.assertFalse(todo in self.tododb.list_todos())

    def test_item_with_project_completion(self):
        project = self.tododb.add_project("the wild rover")
        item = self.tododb.add_item("s", project=project.id)
        project.toggle()
        self.assertFalse(item in self.tododb.list_items())

    def test_project_tickler(self):
        project = self.tododb.add_project("j'ai faim")
        tickler = datetime(2010, 06, 25)
        project.tickle(tickler)
        self.assertEqual(tickler, project.tickler)

    def test_project_tickler_at_creation(self):
        tickler = datetime(2010, 06, 25)
        project = self.tododb.add_project("j'ai faim", tickler=tickler)
        self.assertEqual(tickler, project.tickler)

    def test_list_project_tickler(self):
        # for tomorrow
        tickler = datetime.now() + timedelta(1)
        project = self.tododb.add_project("haha, j'ai visité LA brasserie de Guiness", tickler=tickler)
        self.assertFalse(project in self.tododb.list_projects())
        self.assertTrue(project in self.tododb.list_projects(all_projects=True))

    def test_todo_with_project_tickler(self):
        tickler = datetime.now() + timedelta(1)
        project = self.tododb.add_project("j'avais pas réalisé que c'était eux qui avaient inventé le guiness world record book", tickler=tickler)
        todo = self.tododb.add_todo("chier, il pleut", project=project.id)
        self.assertFalse(todo in self.tododb.list_todos())
        self.assertTrue(todo in self.tododb.list_todos(all_todos=True))

    def test_item_with_project_tickler(self):
        tickler = datetime.now() + timedelta(1)
        project = self.tododb.add_project("j'avais pas réalisé que c'était eux qui avaient inventé le guiness world record book", tickler=tickler)
        item = self.tododb.add_item("chier, il pleut", project=project.id)
        self.assertFalse(item in self.tododb.list_items())
        self.assertTrue(item in self.tododb.list_items(all_items=True))

    def test_main_view(self):
        # empty since the only context is empty
        self.assertEqual([], self.tododb.main_view())

    def test_main_view_one_todo(self):
        todo = self.tododb.add_todo("kropotkine")
        self.assertEqual([[self.tododb.get_default_context(), [], [todo]]], self.tododb.main_view())

    def test_main_view_one_item(self):
        item = self.tododb.add_item("kropotkine")
        self.assertEqual([[self.tododb.get_default_context(), [item], []]], self.tododb.main_view())

    def test_main_view_one_item_one_todo(self):
        item = self.tododb.add_item("kropotkine")
        todo = self.tododb.add_todo("kropotkikine")
        self.assertEqual([[self.tododb.get_default_context(), [item], [todo]]], self.tododb.main_view())

    def test_main_view_one_item_one_todo_one_empty_context(self):
        item = self.tododb.add_item("kropotkine")
        todo = self.tododb.add_todo("kropotkikine")
        self.tododb.add_context("empty context")
        self.assertEqual([[self.tododb.get_default_context(), [item], [todo]]], self.tododb.main_view())

    def test_main_view_one_item_one_todo_one_non_empty_context(self):
        item = self.tododb.add_item("kropotkine")
        todo = self.tododb.add_todo("kropotkikine")
        context = self.tododb.add_context("context")
        other_todo = self.tododb.add_todo("James Joyce a l'air terrible", context=context)
        self.assertEqual([[self.tododb.get_default_context(), [item], [todo]],
                          [context, [], [other_todo]]], self.tododb.main_view())
        other_item = self.tododb.add_item("yiha !", context=context)
        self.assertEqual([[self.tododb.get_default_context(), [item], [todo]],
                          [context, [other_item], [other_todo]]], self.tododb.main_view())

    def test_last_completed_todos_empty(self):
        last_completed_todos = self.tododb.last_completed_todos()
        self.assertEqual([], last_completed_todos)

    def test_last_completed_todos_one_todo(self):
        todo = self.tododb.add_todo("pouet")
        todo.toggle()
        last_completed_todos = self.tododb.last_completed_todos()
        self.assertEqual([todo], last_completed_todos)

    def test_last_completed_todos_multiple_todos(self):
        todo1 = self.tododb.add_todo("pouet")
        todo2 = self.tododb.add_todo("pouet pouet")
        todo3 = self.tododb.add_todo("taratata pouet pouet")
        todo1.toggle()
        time.sleep(1)
        todo3.toggle()
        time.sleep(1)
        todo2.toggle()
        last_completed_todos = self.tododb.last_completed_todos()
        self.assertEqual([todo2, todo3, todo1], last_completed_todos)

    def test_project_due(self):
        project = self.tododb.add_project("je code dans un avion qui revient d'irlande")
        due = date.today()
        project.due_for(due)
        self.assertEqual(project.due, due)

    def test_project_due_at_creation(self):
        due = datetime.now()
        project = self.tododb.add_project("je code dans un avion qui revient d'irlande", due=due)
        self.assertTrue(comp_datetime(project.due, due))

    def test_project_due_date_on_a_todo(self):
        due = datetime.now()
        project = self.tododb.add_project("je code dans un avion qui revient d'irlande", due=due)
        todo = self.tododb.add_todo("la gamine qui est dans le siège devant moi arrête pas de faire plein de conneries", project=project.id)
        self.assertTrue(comp_datetime(todo.due, due))

    def test_project_due_date_on_a_todo_with_earlier_todo(self):
        due = datetime.now()
        project = self.tododb.add_project("je code dans un avion qui revient d'irlande", due=(due + timedelta(1)))
        todo = self.tododb.add_todo("la gamine qui est dans le siège devant moi arrête pas de faire plein de conneries", project=project.id, due=due)
        self.assertTrue(comp_datetime(todo.due, due))

    def test_project_due_date_on_a_todo_with_later_todo(self):
        due = datetime.now()
        project = self.tododb.add_project("je code dans un avion qui revient d'irlande", due=due)
        todo = self.tododb.add_todo("la gamine qui est dans le siège devant moi arrête pas de faire plein de conneries", project=project.id, due=(due + timedelta(1)))
        self.assertTrue(comp_datetime(todo.due, due))

    def test_get_todos_and_items_on_context_empty(self):
        context = self.tododb.add_context("regardcitoyens ça déchire")
        self.assertEqual([[], []], context.get_todos_and_items())

    def test_get_todos_and_items_on_context_todo(self):
        context = self.tododb.add_context("regardcitoyens ça déchire")
        todo = self.tododb.add_todo("youplaboum", context=context.id)
        self.assertTrue(todo in context.get_todos_and_items()[0])

    def test_get_todos_and_items_on_context_item(self):
        context = self.tododb.add_context("regardcitoyens ça déchire")
        item = self.tododb.add_item("huhu haha", context=context.id)
        self.assertTrue(item in context.get_todos_and_items()[1])

    def test_get_todos_and_items_on_context_item_n_todo(self):
        context = self.tododb.add_context("regardcitoyens ça déchire")
        todo = self.tododb.add_todo("youplaboum", context=context.id)
        item = self.tododb.add_item("huhu haha", context=context.id)
        self.assertTrue(todo in context.get_todos_and_items()[0])
        self.assertTrue(item in context.get_todos_and_items()[1])

    def test_get_todos_and_items_on_project_empty(self):
        project = self.tododb.add_project("regardcitoyens ça déchire")
        self.assertEqual([[], []], project.get_todos_and_items())

    def test_get_todos_and_items_on_project_todo(self):
        project = self.tododb.add_project("regardcitoyens ça déchire")
        todo = self.tododb.add_todo("youplaboum", project=project.id)
        self.assertTrue(todo in project.get_todos_and_items()[0])

    def test_get_todos_and_items_on_project_item(self):
        project = self.tododb.add_project("regardcitoyens ça déchire")
        item = self.tododb.add_item("huhu haha", project=project.id)
        self.assertTrue(item in project.get_todos_and_items()[1])

    def test_get_todos_and_items_on_project_item_n_todo(self):
        project = self.tododb.add_project("regardcitoyens ça déchire")
        todo = self.tododb.add_todo("youplaboum", project=project.id)
        item = self.tododb.add_item("huhu haha", project=project.id)
        self.assertTrue(todo in project.get_todos_and_items()[0])
        self.assertTrue(item in project.get_todos_and_items()[1])

    def test_cant_wait_for_a_todo_that_wait_for_you(self):
        todo1 = self.tododb.add_todo("youplaboum")
        todo2 = self.tododb.add_todo("tien, zimmermann se fait draguer sur twitter", wait_for=todo1)
        self.assertRaises(WaitForError, todo1.wait_for, todo2)

    def test_todo_cant_wait_for_self(self):
        todo = self.tododb.add_todo("ima new todo")
        self.assertRaises(WaitForError, todo.wait_for, todo)

    # TODO: refactorer les exceptions, favoriser un message plutôt que plein d'exceptions différentes
    # TODO: faire un utils.py et rajouter plein de petits outils dedans comme un parseur de date etc ...
    # TODO: faire marcher sd <- migrer vers lucid
    # TODO: tien et si je faisais un nouveau attribut "drop" en plus de completed
    # TODO: faire une méthode de converstion d'un item en todo
    # TODO: envisager de changer le fichier de config pour qu'écrire l'accès à la bdd soit plus simple
    # TODO: add other search methods
    # TODO: reset db à la place de drop db et un confirmation demandé

if __name__ == "__main__":
   unittest.main()

