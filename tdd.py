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

class ContextStillHasTodos(exceptions.Exception):
    def __init__(self):
        super(ContextStillHasTodos, self).__init__()

    def __str__(self):
        return 'This context still containt todos, can\'t remove it'

class TodoDoesntExist(exceptions.Exception):
    def __init__(self, todo):
        self.todo = todo
        super(TodoDoesntExist, self).__init__()

    def __str__(self):
        return 'this todo doesn\'t exist: %s' % self.todo

class ContextDoesntExist(exceptions.Exception):
    def __init__(self, context):
        self.context = context
        super(ContextDoesntExist, self).__init__()

    def __str__(self):
        return 'this context doesn\'t exist: %s' % self.context

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

class _Context(sqlobject.SQLObject):
    description = sqlobject.StringCol()
    default_context = sqlobject.BoolCol(default=False)
    created_at = sqlobject.DateCol(default=datetime.now())
    #position = IntCol(unique=True)
    #hide = BoolCol(default=False)

    def rename(self, new_description):
        self.description = new_description

    def remove(self):
        if self.default_context:
            raise CanRemoveTheDefaultContext
        elif _Todo.select(_Todo.q.context == self).count() != 0:
            raise ContextStillHasTodos
        else:
            self.destroySelf()

    def set_default(self):
        self.select(self.q.default_context == True)[0].default_context = False
        self.default_context = True

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
    context = sqlobject.ForeignKey('_Context')
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

    def change_context(self, context_id):
        self.context = context_id

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

class TodoDB(object):

    def __init__(self, database_uri = None):
        """
        The main object, it's the interface with the todo database.

        Arguments:
            * a different uri to connect to another database than the one into
              the configuration file (ie for tests)
        """
        self._connect(database_uri)

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
            _Context.createTable()
            #Project.createTable(ifNotExists=True)
            #Item.createTable(ifNotExists=True)
            _Todo.createTable()
        except Exception, e:
            # ultimely dirty, I really don't know why I push this
            # I haven't found another way to do this :(
            if str(e).endswith("exists"):
                raise TableAlreadyExist(str(e))
            else:
                raise e

        # always have a context
        _Context(description="default context", default_context = True)

    def drop_db(self):
        """
        Drop the database if it isn't already drop

        WARNING: this will destroy *everything* in the database
        """
        _Context.dropTable(ifExists=True)
        #Project.dropTable(ifExists=True)
        #Item.dropTable(ifExists=True)
        _Todo.dropTable(ifExists=True)

    def add_todo(self, new_description, tickler=None, due=None, context=None, unique=False):
        """
        Add a new todo, return it

        Arguments:
            * the description of the todo
        """
        if not context:
            context = self.get_default_context().id
        if unique and _Todo.select(_Todo.q.description == new_description).count() != 0:
            return -1
        return _Todo(description=new_description, tickler=tickler, due=due, context=context)

    def get_todo_by_desc(self, description):
        """
        Receive a the description of a todo, return it
        Raise an exception if the todo doesn't exist

        Arguments:
            * todo description
        """
        query = _Todo.select(_Todo.q.description == description)
        if query.count() == 0:
            raise TodoDoesntExist(description)
        return [i for i in query]

    def search_for_todo(self, description):
        """
        Receive a string, return all the todo that match that string

        Arguments:
            * a string
        """
        return [i for i in _Todo.select() if description in i.description]

    def get_todo(self, todo_id):
        """
        Receive the id of a todo, return the todo
        Raise an exception if the todo doesn't exist

        Arguments:
            * todo description
        """
        try:
            return _Todo.get(todo_id)
        except sqlobject.SQLObjectNotFound:
            raise TodoDoesntExist(todo_id)

    def list_todos(self, all_todos=False):
        """
        Return a list of todos, by default only uncompleted todos.

        Arguments:
            * all =False by default, if True return all the todos.
        """
        return [i for i in _Todo.select(sqlobject.AND(_Todo.q.completed == False,
               sqlobject.OR(_Todo.q.tickler == None, _Todo.q.tickler < datetime.now()))).orderBy('id')] if\
                not all_todos else [i for i in _Todo.select()]

    def add_context(self, description, default=False):
        # TODO docstring
        new_context = _Context(description=description)
        if default:
            new_context.set_default()
        return new_context

    def get_default_context(self):
        assert _Context.select(_Context.q.default_context == True).count() == 1
        return _Context.select(_Context.q.default_context == True)[0]

    def get_context_by_desc(self, description):
        # TODO docstring
        query = _Context.select(_Context.q.description == description)
        if query.count() == 0:
            raise ContextDoesntExist(description)
        return [i for i in query]

    def get_context(self, context_id):
        try:
            return _Context.get(context_id)
        except sqlobject.SQLObjectNotFound:
            raise ContextDoesntExist(context_id)

    def list_contexts(self):
        return [i for i in _Context.select()]

if __name__ == "__main__":
    pass
