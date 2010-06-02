#!/usr/bin/python
# -*- coding:Utf-8 -*-

import exceptions

from sqlobject import *

from config import DATABASE_ACCESS

#from datetime import datetime

class TodoAlreadyExist(exceptions.Exception):
    def __init__(self, todo_name):
        self.todo_name = todo_name

    def __str__(self):
        return 'this todo already exist in the database: "%s"' % self.todo_name

class TodoDoesntExist(exceptions.Exception):
    def __init__(self, todo_name):
        self.todo_name = todo_name

    def __str__(self):
        return 'this todo doesn\'t exist: %s' % self.todo_name

class TodoDB(object):
    def __init__(self):
        self.connect()

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
        A Todo

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
        #completed = BoolCol(default=False)
        #next_todo = IntCol(default=None)
        #previous_todo = IntCol(default=None)

    # TODO: how the fuck can I for the use of innodb for mysql ?
    #def connect(selfuser = None, password = None, db_type = None):
    def connect(self):
        """
        Connect to the database
        """
        # todo, generalisation
        sqlhub.processConnection = connectionForURI(DATABASE_ACCESS)

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
        """
        #Context.dropTable(ifExists=True)
        #Project.dropTable(ifExists=True)
        #Item.dropTable(ifExists=True)
        self._Todo.dropTable(ifExists=True)

    def todo_len(self):
        return self._Todo.select().count()

    def add_todo(self, new_description):
        """
        Add a new todo

        Arguments:
            * the description of the todo
        """
        assert self._Todo.select(self._Todo.q.description == new_description).count() <= 1, 'multiple instance of this todo exist in the database: "%s"' % new_description
        if self._Todo.select(self._Todo.q.description == new_description).count() > 0:
            raise TodoAlreadyExist(new_description)

        self._Todo(description=new_description)

        assert self._Todo.select(self._Todo.q.description == new_description).count() == 1, 'The count of this new todo differt from 1, more than one of this todo has been add or none of it has been add: "%s"' % new_description

    def remove_todo(self, todo):
        """
        Revceived the id of a todo, delete it

        Arguments:
            * todo id
        """
        try:
            self._Todo.get(todo).destroySelf()
        except SQLObjectNotFound:
            raise TodoDoesntExist(todo)

        # assert, only on contract programming purpose
        if __debug__:
            try:
                self._Todo.get(todo)
                raise AssertionError("This todo should have been destroyed: \"%s\"" % todo)
            except SQLObjectNotFound:
                pass

    def get_todo_id(self, description):
        """
        Receveid a the description of a todo, return it's id

        Arguments:
            * todo description
        """
        query = self._Todo.select(self._Todo.q.description == description)
        if query.count() == 0:
            raise TodoDoesntExist, description
        assert query.count() == 1, "There is more than one instance of this todo in the database: \"%s\"" % description
        return query[0].id

    def search_for_todo(self, description):
        todos = self._Todo.select()

        result = []
        for i in todos:
            if description in i.description:
                result.append({"id" : i.id, "description" : i.description})

        return result

if __name__ == "__main__":
    pass
