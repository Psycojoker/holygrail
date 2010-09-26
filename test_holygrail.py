#!/usr/bin/python
# -*- coding:Utf-8 -*-

"""
This file is part of HolyGrail.

HolyGrail is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

HolyGrail is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with HolyGrail.  If not, see <http://www.gnu.org/licenses/>.

HolyGrail  Copyright (C) 2010  Laurent Peuch <cortex@worlddomination.be>
"""

import unittest, time

from datetime import date, datetime, timedelta

from holygrail import Grail, TodoDoesntExist, CanRemoveTheDefaultContext, ContextDoesntExist, ContextStillHasElems, _Context, QuestDoesntExist, _Todo, _Quest, WaitForError

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
        self.grail = self.reinitialise()

    def test_connect_to_another_database(self):
        Grail("sqlite:/:memory:")

    def reinitialise(self):
        """
        Reinitialise the db to make test with a clean one
        Use a sqlite db in memory to avoid losing user/dev data
        """
        grail = Grail('sqlite:/:memory:')
        grail.reset_db("yes")
        return grail

    def test_add_a_todo(self):
        """
        You should be able to add a new todo.
        This should inscrease the number of todos by one
        """
        was = len(self.grail.list_todos())
        todo = self.grail.add_todo("This is a new todo")
        self.assertEqual(was + 1, len(self.grail.list_todos()))
        self.assertTrue(todo in self.grail.list_todos())

        # check if we can add two time a todo with the same description
        todo2 = self.grail.add_todo("This is a new todo")
        self.assertEqual(was + 2, len(self.grail.list_todos()))
        self.assertTrue(todo in self.grail.list_todos())
        self.assertTrue(todo2 in self.grail.list_todos())

    def test_add_todo_unique(self):
        todo = self.grail.add_todo("This is a new todo")
        self.assertEqual(-1, self.grail.add_todo("This is a new todo", unique=True))

    def test_add_todo_unique_toggle(self):
        todo = self.grail.add_todo("This is a new todo")
        todo.toggle()
        self.assertNotEqual(-1, self.grail.add_todo("This is a new todo", unique=True))

    def test_get_todo_by_desc(self):

        t1 = self.grail.add_todo("This is a new todo")
        t2 = self.grail.add_todo("This is a new todo 2")

        self.assertEqual(t1.id, self.grail.get_todo_by_desc("This is a new todo")[0].id)
        self.assertEqual(t2.id, self.grail.get_todo_by_desc("This is a new todo 2")[0].id)

    def test_get_todo_by_desc_mutiple(self):

        t1 = self.grail.add_todo("This is a new todo")
        t2 = self.grail.add_todo("This is a new todo")

        self.assertTrue(t1 in self.grail.get_todo_by_desc("This is a new todo"))
        self.assertTrue(t2 in self.grail.get_todo_by_desc("This is a new todo"))

    def test_get_todo_by_desc_should_raise_an_exection_if_todo_doesnt_exist(self):
        self.assertRaises(TodoDoesntExist, self.grail.get_todo_by_desc, "todo")

    def test_remove_todo(self):

        was = len(self.grail.list_todos())
        todo = self.grail.add_todo("This is a new todo")

        self.assertEqual(was + 1, len(self.grail.list_todos()))

        id = todo.id
        todo.remove()

        self.assertEqual(was, len(self.grail.list_todos()))
        self.assertRaises(TodoDoesntExist, self.grail.get_todo, id)

    def test_seach_for_todo(self):

        todo_to_add = ("new todo", "another todo", "yet a todo", "tododo", "todotodo")
        todo_to_add_that_doesnt_match = ("blabla", "foo", "bar")

        true = [self.grail.add_todo(i) for i in todo_to_add]
        false = [self.grail.add_todo(i) for i in todo_to_add_that_doesnt_match]
        result = self.grail.search_for_todo("todo")

        self.assertEqual(len(todo_to_add), len(result))

        for i in result:
            self.assertTrue(i.description in todo_to_add)
            self.assertTrue(i in true)
            self.assertFalse(i.description in todo_to_add_that_doesnt_match)
            self.assertFalse(i in false)

    def test_get_todo(self):
        todo = self.grail.add_todo("todo")
        self.assertTrue(todo is self.grail.get_todo(todo.id))
        self.assertEqual(todo.description, "todo")

    def test_get_todo_throw_except_if_doesnt_exist(self):
        self.assertRaises(TodoDoesntExist, self.grail.get_todo, 1337)

    def test_rename_todo(self):
        todo = self.grail.add_todo("first name")
        todo.rename("second name")
        self.assertEqual(todo.description, "second name")

    def test_toggle_todo(self):

        t = self.grail.add_todo("prout")

        self.assertFalse(t.completed)
        t.toggle()
        self.assertTrue(t.completed)
        t.toggle()
        self.assertFalse(t.completed)

    def test_list_todos(self):
        # empty
        self.assertEqual(0, len(self.grail.list_todos()))
        t = self.grail.add_todo("todo")
        # one todo
        self.assertEqual(1, len(self.grail.list_todos()))
        self.assertTrue(t in self.grail.list_todos())
        # two todo
        t2 = self.grail.add_todo("todo 2")
        self.assertEqual(2, len(self.grail.list_todos()))
        self.assertTrue(t in self.grail.list_todos())
        self.assertTrue(t2 in self.grail.list_todos())
        # only uncompleted
        t2.toggle()
        self.assertEqual(1, len(self.grail.list_todos()))
        self.assertTrue(t in self.grail.list_todos())
        self.assertTrue(t2 not in self.grail.list_todos())
        # everything
        self.assertEqual(2, len(self.grail.list_todos(all_todos=True)))
        self.assertTrue(t in self.grail.list_todos(all_todos=True))
        self.assertTrue(t2 in self.grail.list_todos(all_todos=True))

    def test_todo_should_be_created_today(self):
        todo = self.grail.add_todo("this is a todo")
        self.assertEqual(todo.created_at, date.today())

    def test_todo_completion_date(self):
        todo = self.grail.add_todo("this is a todo")
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
        todo = self.grail.add_todo("new todo")
        self.assertEquals(None, todo.tickler)

    def test_tickler_at_creation(self):
        tickler = datetime(2010, 06, 25)
        todo = self.grail.add_todo("new todo", tickler=tickler)
        self.assertEqual(tickler, todo.tickler)

    def test_add_tickle(self):
        tickler = datetime(2010, 06, 25)
        todo = self.grail.add_todo("new todo")
        todo.tickle(tickler)
        self.assertEqual(tickler, todo.tickler)

    def test_list_dont_show_tickle_task(self):
        # for tomorrow
        tickler = datetime.now() + timedelta(1)
        todo = self.grail.add_todo("new todo", tickler)
        self.assertTrue(todo not in self.grail.list_todos())

    def test_list_all_show_tickle_task(self):
        # for tomorrow
        tickler = datetime.now() + timedelta(1)
        todo = self.grail.add_todo("new todo", tickler)
        self.assertTrue(todo in self.grail.list_todos(all_todos=True))

    def test_due_date_at_creation(self):
        due = datetime(2010, 06, 25)
        todo = self.grail.add_todo("new todo", due=due)
        self.assertEqual(due, todo.due)

    def test_add_due(self):
        due = datetime(2010, 06, 25)
        todo = self.grail.add_todo("new todo")
        todo.due_for(due)
        self.assertEqual(due, todo.due)

    def test_tdd_should_have_a_context_at_creation(self):
        self.assertEqual("default context", _Context.get(1).description)
        self.assertEqual(1, _Context.select().count())

    def test_add_context(self):
        context = self.grail.add_context("new context")
        self.assertEqual(context.description, "new context")
        self.assertEqual(2, _Context.select().count())

    def test_rename_context(self):
        _Context.get(1).rename("new description")
        self.assertEqual("new description", _Context.get(1).description)

    def test_remove_context(self):
        self.assertEqual(1, _Context.select().count())
        context = self.grail.add_context("new context")
        self.assertEqual(2, _Context.select().count())
        context.remove()
        self.assertEqual(1, _Context.select().count())

    def test_default_context_at_init(self):
        context = self.grail.get_default_context()
        self.assertEqual(1, context.id)
        self.assertEqual(True, context.default_context)

    def test_change_default_context(self):
        context = self.grail.add_context("new context")
        context.set_default()
        self.assertEqual(context.default_context, True)

    def test_their_should_only_be_one_default_context(self):
        previous = self.grail.get_default_context()
        context = self.grail.add_context("new context")
        context.set_default()
        self.assertEqual(False, previous.default_context)
        self.assertEqual(context, self.grail.get_default_context())
        self.assertEqual(1, _Context.select(_Context.q.default_context == True).count())

    def test_cant_remove_default_context(self):
        # to avoid having the exception NeedAtLeastOneContext if the exception we are waiting isn't raised
        # yes it will crash anyway
        self.grail.add_context("prout")
        self.assertRaises(CanRemoveTheDefaultContext, self.grail.get_default_context().remove)

    def test_a_todo_should_have_the_default_context(self):
        todo = self.grail.add_todo("a todo")
        self.assertEqual(todo.context, self.grail.get_default_context())
        todo = self.grail.add_todo("another todo")
        self.assertEqual(todo.context, self.grail.get_default_context())

    def test_get_context_by_desc(self):
        context = self.grail.add_context("youpla")
        self.assertEqual(context, self.grail.get_context_by_desc("youpla")[0])

    def test_get_context_by_desc_raise_if_dont_exist(self):
        self.assertRaises(ContextDoesntExist, self.grail.get_context_by_desc, "I don't exist")

    def test_get_context(self):
        context = self.grail.add_context("zoubiboulba suce mon zob")
        self.assertEqual(context, self.grail.get_context(context.id))

    def test_get_context_raise_if_dont_exist(self):
        self.assertRaises(ContextDoesntExist, self.grail.get_context, 1337)

    def test_add_todo_with_special_context(self):
        context = self.grail.add_context("je devrais aller dormir")
        todo = self.grail.add_todo("mouhaha", context=context.id)
        self.assertEqual(context, todo.context)

    def test_change_todo_context(self):
        context = self.grail.add_context("je vais encore me coucher à pas d'heure ...")
        todo = self.grail.add_todo("aller dormir")
        todo.change_context(context.id)
        self.assertEqual(context, todo.context)

    def test_cant_delete_context_with_todos(self):
        context = self.grail.add_context("TDD rosk")
        todo = self.grail.add_todo("HAHAHA I'M USING TEH INTERNETZ", context=context)
        self.assertRaises(ContextStillHasElems, context.remove)

    def test_list_contexts(self):
        self.assertTrue(self.grail.get_default_context() in self.grail.list_contexts())
        self.assertEqual(len(self.grail.list_contexts()), 1)
        context = self.grail.add_context("foobar")
        self.assertEqual(len(self.grail.list_contexts()), 2)
        context.remove()
        self.assertEqual(len(self.grail.list_contexts()), 1)

    def test_add_Context_default(self):
        context = self.grail.add_context("zomg, ils ont osé faire un flim sur les schtroumphs", default=True)
        self.assertEqual(context, self.grail.get_default_context())
        self.assertTrue(context.default_context)

    def test_context_should_have_a_creation_date(self):
        context = self.grail.add_context("les fils de teuphu c'est super")
        self.assertEqual(date.today(), context.created_at)

    def test_add_quest(self):
        quest = self.grail.add_quest("quest apocalypse")
        self.assertEqual("quest apocalypse", quest.description)

    def test_get_quest(self):
        quest = self.grail.add_quest("quest manatan")
        self.assertEqual(quest, self.grail.get_quest(quest.id))

    def test_get_quest_raise_if_dont_exist(self):
        self.assertRaises(QuestDoesntExist, self.grail.get_quest, 42)

    def test_get_quest_by_desc(self):
        quest = self.grail.add_quest("acheter du saucisson")
        self.assertEqual(self.grail.get_quest_by_desc("acheter du saucisson")[0], quest)
        self.assertEqual(len(self.grail.get_quest_by_desc("acheter du saucisson")), 1)
        self.grail.add_quest("acheter du saucisson")
        self.assertEqual(len(self.grail.get_quest_by_desc("acheter du saucisson")), 2)
        self.assertEqual(len(self.grail.get_quest_by_desc("acheter des cornichons")), 0)

    def test_rename_quest(self):
        quest = self.grail.add_quest("j'ai envie de chocolat")
        quest.rename("the cake is a lie")
        self.assertEqual(quest.description, "the cake is a lie")

    def test_list_quests(self):
        self.assertEqual(0, len(self.grail.list_quests()))
        quest = self.grail.add_quest("ce truc a l'air super http://smarterware.org/6172/hilary-mason-how-to-replace-yourself-with-a-small-shell-script")
        self.assertTrue(quest in self.grail.list_quests())
        self.assertEqual(1, len(self.grail.list_quests()))

    def test_remove_quest(self):
        self.assertEqual(0, len(self.grail.list_quests()))
        quest = self.grail.add_quest("lovely code vortex")
        self.assertEqual(1, len(self.grail.list_quests()))
        old_id = quest.id
        quest.remove()
        self.assertRaises(QuestDoesntExist, self.grail.get_quest, old_id)
        self.assertEqual(0, len(self.grail.list_quests()))

    def test_change_todo_quest(self):
        quest = self.grail.add_quest("manger une pomme")
        todo = self.grail.add_todo("le nouveau leak d'ACTA est dégeulasse")
        todo.change_quest(quest.id)
        self.assertEqual(todo.quest, quest)

    def test_next_todo(self):
        todo1 = self.grail.add_todo("first todo")
        todo2 = self.grail.add_todo("second todo")
        todo2.wait_for(todo1)
        self.assertEqual(todo1, todo2.previous_todo)

    def test_list_todo_with_previous_todo(self):
        todo1 = self.grail.add_todo("first todo")
        todo2 = self.grail.add_todo("second todo")
        todo2.wait_for(todo1)
        self.assertTrue(todo2 not in self.grail.list_todos())

    def test_list_todo_with_previous_todo_with_completed(self):
        todo1 = self.grail.add_todo("first todo")
        todo2 = self.grail.add_todo("second todo")
        todo2.wait_for(todo1)
        todo1.toggle()
        self.assertTrue(todo2 in self.grail.list_todos())

    def test_add_todo_wait_for(self):
        todo1 = self.grail.add_todo("first todo")
        todo2 = self.grail.add_todo("second todo", wait_for=todo1.id)
        self.assertEqual(todo1, todo2.previous_todo)

    def test_add_todo_with_a_quest(self):
        quest = self.grail.add_quest("gare a Gallo")
        todo = self.grail.add_todo("first todo", quest=quest.id)
        self.assertEqual(quest, todo.quest)

    def test_quest_should_have_a_creation_date(self):
        quest = self.grail.add_quest("youplaboum")
        self.assertEqual(quest.created_at, date.today())

    def test_set_default_context_to_quest(self):
        quest = self.grail.add_quest("youmi, I love chocolate")
        context = self.grail.add_context("pc")
        quest.set_default_context(context.id)
        self.assertEqual(context, quest.default_context)

    def test_set_default_context_to_quest_at_creation(self):
        context = self.grail.add_context("pc")
        quest = self.grail.add_quest("youmi, I love chocolate", default_context=context.id)
        self.assertEqual(context, quest.default_context)

    def test_new_todo_with_quest_with_default_context(self):
        context = self.grail.add_context("pc")
        quest = self.grail.add_quest("youmi, I love chocolate", default_context=context.id)
        todo = self.grail.add_todo("pataplouf", quest=quest.id)
        self.assertEqual(todo.context, context)

    def test_new_todo_with_quest_with_default_context_and_context(self):
        context = self.grail.add_context("pc")
        other_context = self.grail.add_context("mouhaha")
        quest = self.grail.add_quest("youmi, I love chocolate", default_context=context.id)
        todo = self.grail.add_todo("pataplouf", context=other_context, quest=quest.id)
        self.assertEqual(todo.context, other_context)

    def test_set_hide_context(self):
        context = self.grail.add_context("pc")
        self.assertFalse(context.hide)
        context.toggle_hide()
        self.assertTrue(context.hide)
        context.toggle_hide()
        self.assertFalse(context.hide)
        context.toggle_hide()
        self.assertTrue(context.hide)

    def test_hide_context_in_list_context(self):
        context = self.grail.add_context("pc")
        self.assertTrue(context in self.grail.list_contexts())
        context.toggle_hide()
        self.assertFalse(context in self.grail.list_contexts())

    def test_list_all_contexts(self):
        context = self.grail.add_context("pc", hide=True)
        self.assertFalse(context in self.grail.list_contexts())
        self.assertTrue(context in self.grail.list_contexts(all_contexts=True))

    def test_context_hide_at_creation(self):
        context = self.grail.add_context("pc", hide=True)
        self.assertTrue(context.hide)

    def test_hide_context_in_list_todo(self):
        context = self.grail.add_context("pc", hide=True)
        todo = self.grail.add_todo("atchoum", context=context)
        self.assertFalse(todo in self.grail.list_todos())
        self.assertTrue(todo in self.grail.list_todos(all_todos=True))

    def test_list_todo_with_previous_todo_with_deleted(self):
        todo1 = self.grail.add_todo("first todo")
        todo2 = self.grail.add_todo("second todo")
        todo2.wait_for(todo1)
        todo1.remove()
        self.assertTrue(todo2 in self.grail.list_todos())
        self.assertEqual(None, todo2.previous_todo)

    def test_remove_quest_with_todos(self):
        quest = self.grail.add_quest("tchikaboum")
        todo = self.grail.add_todo("arakiri", quest=quest.id)
        todo2 = self.grail.add_todo("arakirikiki", quest=quest.id)
        quest.remove()
        self.assertEqual(None, todo.quest)
        self.assertEqual(None, todo2.quest)

    def test_auto_create_tables(self):
        Grail('sqlite:/:memory:')
        _Context.dropTable(ifExists=True)
        _Quest.dropTable(ifExists=True)
        _Todo.dropTable(ifExists=True)
        Grail('sqlite:/:memory:')
        self.assertTrue(_Todo.tableExists())
        self.assertTrue(_Context.tableExists())
        self.assertTrue(_Quest.tableExists())

    def test_context_position(self):
        context = self.grail.get_default_context()
        self.assertEqual(0, context.position)

    def test_new_context_position(self):
        context = self.grail.add_context("In Dublin fair city ...")
        self.assertEqual(1, context.position)
        context = self.grail.add_context("where the girl are so pretty ...")
        self.assertEqual(2, context.position)

    def test_change_context_position_alone_default_to_max(self):
        context1 = self.grail.get_default_context()
        context1.change_position(4)
        self.assertEqual(0, context1.position)

    def test_change_context_position_2_contexts_no_change(self):
        context1 = self.grail.get_default_context()
        context2 = self.grail.add_context("context2")
        context1.change_position(0)
        self.assertEqual(0, context1.position)
        self.assertEqual(1, context2.position)

    def test_change_context_position_2_contexts(self):
        context1 = self.grail.get_default_context()
        context2 = self.grail.add_context("context2")
        context1.change_position(1)
        self.assertEqual(1, context1.position)
        self.assertEqual(0, context2.position)

    def test_change_context_position_2_contexts_default_to_max(self):
        context1 = self.grail.get_default_context()
        context2 = self.grail.add_context("context2")
        context1.change_position(4)
        self.assertEqual(1, context1.position)
        self.assertEqual(0, context2.position)

    def test_change_context_position_2_contexts_swap(self):
        context1 = self.grail.get_default_context()
        context2 = self.grail.add_context("context2")
        context2.change_position(0)
        self.assertEqual(0, context2.position)
        self.assertEqual(1, context1.position)

    def test_change_context_position_2_contexts_swap_reverse(self):
        context1 = self.grail.get_default_context()
        context2 = self.grail.add_context("context2")
        context1.change_position(1)
        self.assertEqual(0, context2.position)
        self.assertEqual(1, context1.position)

    def test_change_context_position_2_contexts_swap_reverse_default_to_max(self):
        context1 = self.grail.get_default_context()
        context2 = self.grail.add_context("context2")
        context1.change_position(6)
        self.assertEqual(0, context2.position)
        self.assertEqual(1, context1.position)

    def test_change_context_position_3_contexts(self):
        context1 = self.grail.get_default_context()
        context2 = self.grail.add_context("context2")
        context3 = self.grail.add_context("context3")
        context1.change_position(6)
        self.assertEqual(1, context3.position)
        self.assertEqual(0, context2.position)
        self.assertEqual(2, context1.position)

    def test_change_context_position_3_contexts_full(self):
        context1 = self.grail.get_default_context()
        context2 = self.grail.add_context("context2")
        context3 = self.grail.add_context("context3")
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
        context1 = self.grail.get_default_context()
        context1.rename("context1")
        context2 = self.grail.add_context("context2")
        context3 = self.grail.add_context("context3")
        context4 = self.grail.add_context("context4")
        context5 = self.grail.add_context("context5")
        context6 = self.grail.add_context("context6")
        context1.change_position(4)
        self.assertEqual(4, context1.position)
        self.assertEqual(0, context2.position)
        self.assertEqual(1, context3.position)
        self.assertEqual(2, context4.position)
        self.assertEqual(3, context5.position)
        self.assertEqual(5, context6.position)

    def test_list_quest_by_position(self):
        context1 = self.grail.get_default_context()
        context1.rename("context1")
        context2 = self.grail.add_context("context2")
        context3 = self.grail.add_context("context3")
        context4 = self.grail.add_context("context4")
        context5 = self.grail.add_context("context5")
        context6 = self.grail.add_context("context6")
        context1.change_position(4)
        contexts = self.grail.list_contexts()
        self.assertEqual(contexts[4], context1)
        self.assertEqual(contexts[0], context2)
        self.assertEqual(contexts[1], context3)
        self.assertEqual(contexts[2], context4)
        self.assertEqual(contexts[3], context5)
        self.assertEqual(contexts[5], context6)

    def test_quest_hide(self):
        quest = self.grail.add_quest("lalala")
        self.assertFalse(quest.hide)
        quest.toggle_hide()
        self.assertTrue(quest.hide)
        quest.toggle_hide()
        self.assertFalse(quest.hide)

    def test_quest_hide_at_creation(self):
        quest = self.grail.add_quest("lalala", hide=True)
        self.assertTrue(quest.hide)

    def test_list_todo_with_quest_hide(self):
        quest = self.grail.add_quest("qsd")
        quest.toggle_hide()
        todo = self.grail.add_todo("toto", quest=quest.id)
        self.assertFalse(todo in self.grail.list_todos())
        self.assertTrue(todo in self.grail.list_todos(all_todos=True))

    def test_list_quest_and_quest_hide(self):
        quest = self.grail.add_quest("huhu")
        quest.toggle_hide()
        self.assertFalse(quest in self.grail.list_quests())

    def test_list_all_quests(self):
        quest = self.grail.add_quest("huhu")
        self.assertTrue(quest in self.grail.list_quests())
        self.assertTrue(quest in self.grail.list_quests(all_quests=True))
        quest.toggle_hide()
        self.assertFalse(quest in self.grail.list_quests())
        self.assertTrue(quest in self.grail.list_quests(all_quests=True))

    #def test_next_todo_for_item(self):
        #todo = self.grail.add_todo("todo")
        #item = self.grail.add_item("item")
        #item.wait_for(todo)
        #self.assertEqual(todo, item.previous_todo)

    #def test_list_item_with_previous_todo(self):
        #todo = self.grail.add_todo("todo")
        #item = self.grail.add_item("item")
        #item.wait_for(todo)
        #self.assertTrue(item not in self.grail.list_items())

    #def test_list_item_with_previous_todo_with_completed(self):
        #todo = self.grail.add_todo("first todo")
        #item = self.grail.add_item("second todo")
        #item.wait_for(todo)
        #todo.toggle()
        #self.assertTrue(item in self.grail.list_items())

    #def test_add_item_wait_for(self):
        #todo = self.grail.add_todo("first todo")
        #item = self.grail.add_item("second item", wait_for=todo.id)
        #self.assertEqual(todo, item.previous_todo)

    def test_quest_completion(self):
        quest = self.grail.add_quest("bah")
        self.assertFalse(quest.completed)
        quest.toggle()
        self.assertTrue(quest.completed)
        quest.toggle()
        self.assertFalse(quest.completed)

    def test_quest_completion_date(self):
        quest = self.grail.add_quest("yamakasi")
        quest.toggle()
        self.assertTrue(comp_datetime(datetime.now(), quest.completed_at))
        quest.toggle()
        self.assertEqual(None, quest.completed_at)

    def test_todo_with_quest_completion(self):
        quest = self.grail.add_quest("the wild rover")
        todo = self.grail.add_todo("s", quest=quest.id)
        quest.toggle()
        self.assertFalse(todo in self.grail.list_todos())

    def test_quest_tickler(self):
        quest = self.grail.add_quest("j'ai faim")
        tickler = datetime(2010, 06, 25)
        quest.tickle(tickler)
        self.assertEqual(tickler, quest.tickler)

    def test_quest_tickler_at_creation(self):
        tickler = datetime(2010, 06, 25)
        quest = self.grail.add_quest("j'ai faim", tickler=tickler)
        self.assertEqual(tickler, quest.tickler)

    def test_list_quest_tickler(self):
        # for tomorrow
        tickler = datetime.now() + timedelta(1)
        quest = self.grail.add_quest("haha, j'ai visité LA brasserie de Guiness", tickler=tickler)
        self.assertFalse(quest in self.grail.list_quests())
        self.assertTrue(quest in self.grail.list_quests(all_quests=True))

    def test_todo_with_quest_tickler(self):
        tickler = datetime.now() + timedelta(1)
        quest = self.grail.add_quest("j'avais pas réalisé que c'était eux qui avaient inventé le guiness world record book", tickler=tickler)
        todo = self.grail.add_todo("chier, il pleut", quest=quest.id)
        self.assertFalse(todo in self.grail.list_todos())
        self.assertTrue(todo in self.grail.list_todos(all_todos=True))

    def test_main_view(self):
        # empty since the only context is empty
        self.assertEqual([], self.grail.main_view())

    def test_main_view_one_todo(self):
        todo = self.grail.add_todo("kropotkine")
        self.assertEqual([[self.grail.get_default_context(), [todo]]], self.grail.main_view())

    def test_main_view_one_todo_one_empty_context(self):
        todo = self.grail.add_todo("kropotkikine")
        self.grail.add_context("empty context")
        self.assertEqual([[self.grail.get_default_context(), [todo]]], self.grail.main_view())

    def test_main_view_one_todo_one_non_empty_context(self):
        todo = self.grail.add_todo("kropotkikine")
        context = self.grail.add_context("context")
        other_todo = self.grail.add_todo("James Joyce a l'air terrible", context=context)
        self.assertEqual([[self.grail.get_default_context(), [todo]],
                          [context, [other_todo]]], self.grail.main_view())
        self.assertEqual([[self.grail.get_default_context(), [todo]],
                          [context, [other_todo]]], self.grail.main_view())

    def test_last_completed_todos_empty(self):
        last_completed_todos = self.grail.last_completed_todos()
        self.assertEqual([], last_completed_todos)

    def test_last_completed_todos_one_todo(self):
        todo = self.grail.add_todo("pouet")
        todo.toggle()
        last_completed_todos = self.grail.last_completed_todos()
        self.assertEqual([todo], last_completed_todos)

    def test_last_completed_todos_multiple_todos(self):
        todo1 = self.grail.add_todo("pouet")
        todo2 = self.grail.add_todo("pouet pouet")
        todo3 = self.grail.add_todo("taratata pouet pouet")
        todo1.toggle()
        time.sleep(1)
        todo3.toggle()
        time.sleep(1)
        todo2.toggle()
        last_completed_todos = self.grail.last_completed_todos()
        self.assertEqual([todo2, todo3, todo1], last_completed_todos)

    def test_quest_due(self):
        quest = self.grail.add_quest("je code dans un avion qui revient d'irlande")
        due = date.today()
        quest.due_for(due)
        self.assertEqual(quest.due, due)

    def test_quest_due_at_creation(self):
        due = datetime.now()
        quest = self.grail.add_quest("je code dans un avion qui revient d'irlande", due=due)
        self.assertTrue(comp_datetime(quest.due, due))

    def test_quest_due_date_on_a_todo(self):
        due = datetime.now()
        quest = self.grail.add_quest("je code dans un avion qui revient d'irlande", due=due)
        todo = self.grail.add_todo("la gamine qui est dans le siège devant moi arrête pas de faire plein de conneries", quest=quest.id)
        self.assertTrue(comp_datetime(todo.due, due))

    def test_quest_due_date_on_a_todo_with_earlier_todo(self):
        due = datetime.now()
        quest = self.grail.add_quest("je code dans un avion qui revient d'irlande", due=(due + timedelta(1)))
        todo = self.grail.add_todo("la gamine qui est dans le siège devant moi arrête pas de faire plein de conneries", quest=quest.id, due=due)
        self.assertTrue(comp_datetime(todo.due, due))

    def test_quest_due_date_on_a_todo_with_later_todo(self):
        due = datetime.now()
        quest = self.grail.add_quest("je code dans un avion qui revient d'irlande", due=due)
        todo = self.grail.add_todo("la gamine qui est dans le siège devant moi arrête pas de faire plein de conneries", quest=quest.id, due=(due + timedelta(1)))
        self.assertTrue(comp_datetime(todo.due, due))

    def test_get_todos_on_context_empty(self):
        context = self.grail.add_context("regardcitoyens ça déchire")
        self.assertEqual([], context.get_todos())

    def test_get_todos_on_context_todo(self):
        context = self.grail.add_context("regardcitoyens ça déchire")
        todo = self.grail.add_todo("youplaboum", context=context.id)
        self.assertTrue(todo in context.get_todos())

    def test_get_todos_on_quest_empty(self):
        quest = self.grail.add_quest("regardcitoyens ça déchire")
        self.assertEqual([], quest.get_todos())

    def test_get_todos_on_quest_todo(self):
        quest = self.grail.add_quest("regardcitoyens ça déchire")
        todo = self.grail.add_todo("youplaboum", quest=quest.id)
        self.assertTrue(todo in quest.get_todos())

    def test_cant_wait_for_a_todo_that_wait_for_you(self):
        todo1 = self.grail.add_todo("youplaboum")
        todo2 = self.grail.add_todo("tien, zimmermann se fait draguer sur twitter", wait_for=todo1)
        self.assertRaises(WaitForError, todo1.wait_for, todo2)

    def test_todo_cant_wait_for_self(self):
        todo = self.grail.add_todo("ima new todo")
        self.assertRaises(WaitForError, todo.wait_for, todo)

class TestTags(unittest.TestCase):

    def setUp(self):
        self.grail = self.reinitialise()

    def reinitialise(self):
        """
        Reinitialise the db to make test with a clean one
        Use a sqlite db in memory to avoid losing user/dev data
        """
        grail = Grail('sqlite:/:memory:')
        grail.reset_db("yes")
        return grail

    def test_tags_on_todo_empty(self):
        todo = self.grail.add_todo("plop")
        self.assertFalse(todo.tags)

    def test_tags_todo_one(self):
        todo = self.grail.add_todo("tatatags")
        todo.add_tag("plop")
        self.assertEqual(todo.tags, ["plop",])

    def test_tags_todo_avoid_duplication(self):
        todo = self.grail.add_todo("tatatags")
        todo.add_tag("plop")
        self.assertEqual(todo.tags, ["plop",])
        todo.add_tag("plop")
        self.assertEqual(todo.tags, ["plop",])

    def test_tags_todo_multiple(self):
        todo = self.grail.add_todo("tsointsoin")
        todo.add_tag("plop")
        todo.add_tag("plup")
        self.assertTrue("plop" in todo.tags)
        self.assertTrue("plup" in todo.tags)
        self.assertEqual(len(todo.tags), 2)

    def test_tags_todo_remove_tag(self):
        todo = self.grail.add_todo("tsointsoin")
        todo.add_tag("plop")
        todo.remove_tag("plop")
        self.assertEqual([], todo.tags)

    def test_tags_todo_remove_tags(self):
        todo = self.grail.add_todo("tsointsoin")
        todo.add_tag("plop")
        todo.add_tag("yop")
        todo.remove_tag("plop")
        self.assertEqual(["yop"], todo.tags)
        todo.remove_tag("yop")
        self.assertEqual([], todo.tags)

    def test_tags_todo_remove_tag_raise(self):
        todo = self.grail.add_todo("tsointsoin")
        todo.add_tag("plop")
        self.assertRaises(ValueError, todo.remove_tag, "ploup")

    def test_tags_todo_get_todo_empty(self):
        self.assertEqual([], self.grail.get_todos_from_tag("pouet"))

    def test_tags_todo_get_one_todo(self):
        todo1 = self.grail.add_todo("tsointsoin")
        todo1.add_tag("plop")
        self.assertEqual([todo1], self.grail.get_todos_from_tag("plop"))

    def test_tags_todo_get_two_todos(self):
        todo1 = self.grail.add_todo("tsointsoin")
        todo1.add_tag("plop")
        todo2 = self.grail.add_todo("tsointsoin")
        todo2.add_tag("plop")
        todos = self.grail.get_todos_from_tag("plop")
        self.assertTrue(todo1 in todos)
        self.assertTrue(todo2 in todos)
        self.assertEqual(2, len(todos))

    def test_todo_with_quest_without_datetime(self):
        quest = self.grail.add_quest("quest")
        todo = self.grail.add_todo("prout", quest=quest.id)
        self.grail.list_todos()

    # TODO: refactorer les exceptions, favoriser un message plutôt que plein d'exceptions différentes
    # TODO: faire un utils.py et rajouter plein de petits outils dedans comme un parseur de date etc ...
    # TODO: faire marcher sd <- migrer vers lucid
    # TODO: tien et si je faisais un nouveau attribut "drop" en plus de completed
    # TODO: envisager de changer le fichier de config pour qu'écrire l'accès à la bdd soit plus simple
    # TODO: add other search methods
    # TODO: spliter mes tests unitaires en plusieurs classes

if __name__ == "__main__":
   unittest.main()

