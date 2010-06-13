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

from sqlobject import *

from config import DATABASE_ACCESS

class TodoAlreadyExist(exceptions.Exception):
    def __init__(self, todo):
        self.todo = todo

    def __str__(self):
        return 'this todo already exist in the database: "%s"' % self.todo

class TodoDoesntExist(exceptions.Exception):
    def __init__(self, todo):
        self.todo = todo

    def __str__(self):
        return 'this todo doesn\'t exist: %s' % self.todo

class TodoDB(object):

    def __init__(self, database_uri = None):
        """
        The main object, it's the interface with the todo database.

        Arguments:
            * a different uri to connect to another database than the one into
              the configuration file (ie for tests)
        """
        self.connect(database_uri)

    #class Context(SQLObject):
        #description = StringCol()
        #position = IntCol(unique=True)
        #hide = BoolCol(default=False)
        #created_at = DateTimeCol(default=datetime.now())
        #completed_at = DateTimeCol(default=None)

    #class Project(SQLObject):
        #description = StringCol()
        #state = EnumCol(enumValues=('active', 'completed', 'hidden'), default="active")
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

    class _Todo(SQLObject):
        """
        A Todo object.

        WARNING avoid as much as possible to modify directly the todo
        attribute, prefere the api, and if you do that be really SURE to know
        what you are doing. You don't want to break anything, right ?

        Arguments:
            * description: a text field that discribe the todo
        """
        description = StringCol()
        #notes = StringCol(default=None)
        #context = ForeignKey('Context')
        #project = IntCol(default=None)
        #created_at = DateTimeCol(default=datetime.now())
        #completed_at = DateTimeCol(default=None)
        #due = DateCol(default=None)
        #tickler = DateCol(default=None)
        completed = BoolCol(default=False)
        #next_todo = IntCol(default=None)
        #previous_todo = IntCol(default=None)

    def connect(self, database_uri):
        """
        Connect to the database

        Arguments:
            * a different uri to connect to another database than the one in the config.py file (ie: for unittest)
        """
        sqlhub.processConnection = connectionForURI(database_uri) if database_uri else connectionForURI(DATABASE_ACCESS)

    def create_db(self):
        """
        Create the database if it isn't already create
        """
        #Context.createTable(ifNotExists=True)
        #Project.createTable(ifNotExists=True)
        #Item.createTable(ifNotExists=True)
        self._Todo.createTable(ifNotExists=True)

    def drop_db(self):
        """
        Drop the database if it isn't already drop

        WARNING: this will destroy *everything* in the database
        """
        #Context.dropTable(ifExists=True)
        #Project.dropTable(ifExists=True)
        #Item.dropTable(ifExists=True)
        self._Todo.dropTable(ifExists=True)

    def todo_len(self):
        return self._Todo.select().count()

    def add_todo(self, new_description):
        """
        Add a new todo, return it

        Arguments:
            * the description of the todo
        """
        assert self._Todo.select(self._Todo.q.description == new_description).count() <= 1,\
            'multiple instance of this todo exist in the database: "%s"' % new_description

        if self._Todo.select(self._Todo.q.description == new_description).count() > 0:
            raise TodoAlreadyExist(new_description)

        todo = self._Todo(description=new_description)

        assert self._Todo.select(self._Todo.q.description == new_description).count() == 1,\
            'The count of this new todo differt from 1, more than one or none of this todo has been add: "%s"' % new_description

        return todo

    def remove_todo(self, id):
        """
        Revceived the id of a todo, delete it

        Arguments:
            * todo id
        """
        try:
            self._Todo.get(id).destroySelf()
        except SQLObjectNotFound:
            raise TodoDoesntExist(id)

        # assert, only on contract programming purpose
        if __debug__:
            try:
                self._Todo.get(id)
                raise AssertionError("This todo should have been destroyed: \"%s\"" % todo)
            except SQLObjectNotFound:
                pass

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
        assert query.count() == 1, "There is more than one instance of this todo in the database: \"%s\"" % description
        return query[0]

    def search_for_todo(self, description):
        """
        Receive a string, return all the todo that match that string

        Arguments:
            * a string
        """
        return [i for i in self._Todo.select() if description in i.description]

    def get_todo(self, id):
        """
        Receive the id of a todo, return the todo
        Raise an exception if the todo doesn't exist

        Arguments:
            * todo description
        """
        try:
            return self._Todo.get(id)
        except SQLObjectNotFound:
            raise TodoDoesntExist(id)

    def rename_todo(self, id, new_description):
        """
        Receive an id and a new description, rename the todo with it
        Raise an exception if the todo doesn't exist.

        Arguments:
            * todo id
            * todo new description
        """
        try:
            self._Todo.get(id).description = new_description
        except SQLObjectNotFound, e:
            raise TodoDoesntExist(id)

    def toggle(self, id):
        """
        Receive an id, toggle the completion of a todo.

        Arguments:
            * todo id
        """
        try:
            todo = self._Todo.get(id)
        except SQLObjectNotFound, e:
            raise TodoDoesntExist(id)

        todo.completed = not todo.completed

    def list_todos(self, all=False):
        return [i for i in self._Todo.select(self._Todo.q.completed == False)] if not all else [i for i in self._Todo.select()]

if __name__ == "__main__":
    t = TodoDB()
    t.search_for_todo("t")
