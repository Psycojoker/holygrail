#!/usr/bin/python
# -*- coding:Utf-8 -*-

import exceptions

from sqlobject import *

#from datetime import datetime

def _select_len(select):
    len = 0
    for i in select:
        len += 1

    return len

class TodoAlreadyExist(exceptions.Exception):
    def __init__(self, todo_name):
        self.todo_name = todo_name

    def __str__(self):
        return 'this todo already exist in the database: "%s"' % self.todo_name

class TodoDoesntExist(exceptions.Exception):
    def __init__(self, todo_name):
        self.todo_name = todo_name

    def __str__(self):
        if type(self.todo_name) == int or type(self.todo_name) == long:
            return 'there is no todo with this id: %i' % self.todo_name
        else:
            return 'todo with this name doesn\'t exist: %s' % self.todo_name

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
        sqlhub.processConnection = connectionForURI('mysql://tasks:toto@localhost/tasks')

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
        return _select_len(self._Todo.select())

    def add_todo(self, new_description):
        # should be == 0 but I want to raise a special exception if the todo already exist
        assert _select_len(self._Todo.select(self._Todo.q.description == new_description)) <= 1, 'multiple instance of this todo exist in the database: "%s"' % new_description
        if _select_len(self._Todo.select(self._Todo.q.description == new_description)) > 0:
            raise TodoAlreadyExist(new_description)

        self._Todo(description=new_description)

    def remove_todo(self, todo):
        # if todo is an id
        if type(todo) == long or type(todo) == int:
            self._Todo.get(todo).destroySelf()
        else:
            self._Todo.select(self._Todo.q.description == todo)[0].destroySelf()

    def get_todo_id(self, description):
        return self._Todo.select(self._Todo.q.description == description)[0].id
