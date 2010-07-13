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


import exceptions

import sqlobject

from datetime import date, datetime

from config import DATABASE_ACCESS

#class TodoAlreadyExist(exceptions.Exception):
    #def __init__(self, todo):
        #self.todo = todo
        #super(TodoAlreadyExist, self).__init__()

    #def __str__(self):
        #return 'this todo already exist in the database: "%s"' % self.todo

class NeedAtLeastOneContext(exceptions.Exception):
    def __init__(self):
        super(NeedAtLeastOneContext, self).__init__()

    def __str__(self):
        return 'TDD need at least one context to work correctly'

class TodoDoesntExist(exceptions.Exception):
    def __init__(self, todo):
        self.todo = todo
        super(TodoDoesntExist, self).__init__()

    def __str__(self):
        return 'this todo doesn\'t exist: %s' % self.todo

class TableAlreadyExist(exceptions.Exception):
    def __init__(self, table):
        self.table = table
        super(TableAlreadyExist, self).__init__()

    def __str__(self):
        return "%s" % self.table

class CanRemoveTheDefaultContext(exceptions.Exception):
    def __init__(self):
        super(CanRemoveTheDefaultContext, self).__init__()

    def __str__(self):
        return "can't remove the default context, change it before remove it"

class TodoDB(object):

    def __init__(self, database_uri = None):
        """
        The main object, it's the interface with the todo database.

        Arguments:
            * a different uri to connect to another database than the one into
              the configuration file (ie for tests)
        """
        self._connect(database_uri)

    class _Context(sqlobject.SQLObject):
        description = sqlobject.StringCol()
        default_context = sqlobject.BoolCol(default=False)
        #position = IntCol(unique=True)
        #hide = BoolCol(default=False)
        #created_at = DateTimeCol(default=datetime.now())

        def rename(self, new_description):
            self.description = new_description

        def remove(self):
            if self.select().count() == 1:
                raise NeedAtLeastOneContext
            elif self.default_context:
                raise CanRemoveTheDefaultContext
            else:
                self.destroySelf()

        def set_default(self):
            self.select(self.q.default_context == True)[0].default_context = False
            self.default_context = True

    #class Project(SQLObject):
        #description = StringCol()
        #state = EnumCol(enumValues=('active', 'completed', 'hidden'),
        # default="active")
        #created_at = DateTimeCol(default=datetime.now())
        #completed_at = DateTimeCol(default=None)
        #tickler = DateCol(default=None)
        #due = DateCol(default=None)
        #default_context_id = IntCol(default=None)

    #class Item(SQLObject):
        #description = StringCol()
        #context = ForeignKey('Context')
        #project = IntCol(default=None)
        #created_at = DateTimeCol(default=datetime.now())
        #hidden = BoolCol(default=False)
        ##tickler = DateCol(default=None)
        ##next_todo = IntCol(default=None)
        ##previous_todo = IntCol(default=None)

    class _Todo(sqlobject.SQLObject):
        """
        A Todo object.

        WARNING avoid as much as possible to modify directly the todo
        attribute, prefere the api, and if you do that be really SURE to know
        what you are doing. You don't want to break anything, right ?

        Arguments:
            * description: a text field that discribe the todo
        """
        description = sqlobject.StringCol()
        #context = ForeignKey('Context')
        #project = IntCol(default=None)
        created_at = sqlobject.DateCol(default=date.today())
        completed_at = sqlobject.DateCol(default=None)
        due = sqlobject.DateTimeCol(default=None)
        tickler = sqlobject.DateTimeCol(default=None)
        completed = sqlobject.BoolCol(default=False)
        # do this in a new table ?
        #next_todo = IntCol(default=None)
        #previous_todo = IntCol(default=None)
        # will wait popular demand to be implemented
        #notes = StringCol(default=None)

        def remove(self):
            """
            Remove the todo from the database.
            """
            self.destroySelf()

        def rename(self, description):
            """
            Rename the todo with a new description

            Arguments:
                * new description
            """
            self.description = description

        def toggle(self):
            """
            Toggle to todo completion state
            """
            self.completed = not self.completed
            self.completed_at = date.today() if self.completed else None

        def tickle(self, tickler):
            """
            Change the todo tickler
            """
            self.tickler = tickler

        def due_for(self, due):
            """
            Change the due date
            """
            self.due = due

    def _connect(self, database_uri):
        """
        Connect to the database

        Arguments:
            * a different uri to connect to another database than the one in the config.py file (ie: for unittest)
        """
        sqlobject.sqlhub.processConnection = sqlobject.connectionForURI(database_uri) if database_uri else sqlobject.connectionForURI(DATABASE_ACCESS)

    def create_db(self):
        """
        Create the database if it isn't already create
        """
        try:
            self._Context.createTable()
            #Project.createTable(ifNotExists=True)
            #Item.createTable(ifNotExists=True)
            self._Todo.createTable()
        except Exception, e:
            # ultimely dirty, I really don't know why I push this
            # I haven't found another way to do this :(
            if str(e).endswith("exists"):
                raise TableAlreadyExist(str(e))
            else:
                raise e

        # always have a context
        self._Context(description="default context", default_context = True)

    def drop_db(self):
        """
        Drop the database if it isn't already drop

        WARNING: this will destroy *everything* in the database
        """
        self._Context.dropTable(ifExists=True)
        #Project.dropTable(ifExists=True)
        #Item.dropTable(ifExists=True)
        self._Todo.dropTable(ifExists=True)

    def add_todo(self, new_description, tickler=None, due=None, unique=False):
        """
        Add a new todo, return it

        Arguments:
            * the description of the todo
        """
        if unique and self._Todo.select(self._Todo.q.description == new_description).count() != 0:
            return -1
        return self._Todo(description=new_description, tickler=tickler, due=due)

    def get_todo_by_desc(self, description):
        """
        Receive a the description of a todo, return it
        Raise an exception if the todo doesn't exist

        Arguments:
            * todo description
        """
        query = self._Todo.select(self._Todo.q.description == description)
        if query.count() == 0:
            raise TodoDoesntExist(description)
        return [i for i in query]

    def search_for_todo(self, description):
        """
        Receive a string, return all the todo that match that string

        Arguments:
            * a string
        """
        return [i for i in self._Todo.select() if description in i.description]

    def get_todo(self, todo_id):
        """
        Receive the id of a todo, return the todo
        Raise an exception if the todo doesn't exist

        Arguments:
            * todo description
        """
        try:
            return self._Todo.get(todo_id)
        except sqlobject.SQLObjectNotFound:
            raise TodoDoesntExist(todo_id)

    def list_todos(self, all_todos=False):
        """
        Return a list of todos, by default only uncompleted todos.

        Arguments:
            * all =False by default, if True return all the todos.
        """
        return [i for i in self._Todo.select(sqlobject.AND(self._Todo.q.completed == False,
               sqlobject.OR(self._Todo.q.tickler == None, self._Todo.q.tickler < datetime.now()))).orderBy('id')] if\
                not all_todos else [i for i in self._Todo.select()]

    def add_context(self, description):
        return self._Context(description=description)

    def get_default_context(self):
        assert self._Context.select(self._Context.q.default_context == True).count() == 1
        return self._Context.select(self._Context.q.default_context == True)[0]

if __name__ == "__main__":
    pass
    #t = TodoDB()
    #t.search_for_todo("t")
