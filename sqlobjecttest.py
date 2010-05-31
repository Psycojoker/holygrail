#!/usr/bin/python
# -*- coding:Utf-8 -*-

from sqlobject import *

from datetime import datetime

class Context(SQLObject):
    description = StringCol()
    position = IntCol(unique=True)
    hide = BoolCol(default=False)
    created_at = DateTimeCol(default=datetime.now())
    completed_at = DateTimeCol(default=None)

class Project(SQLObject):
    description = StringCol()
    state = EnumCol(enumValues=('active', 'completed', 'hidden'), default="active")
    created_at = DateTimeCol(default=datetime.now())
    completed_at = DateTimeCol(default=None)
    tickler = DateCol(default=None)
    due = DateCol(default=None)
    default_context_id = IntCol(default=None)

class Item(SQLObject):
    description = StringCol()
    context = ForeignKey('Context')
    project = IntCol(default=None)
    created_at = DateTimeCol(default=datetime.now())
    hidden = BoolCol(default=False)
    #tickler = DateCol(default=None)
    #next_todo = IntCol(default=None)
    #previous_todo = IntCol(default=None)

class Todo(SQLObject):
    description = StringCol()
    notes = StringCol(default=None)
    context = ForeignKey('Context')
    project = IntCol(default=None)
    created_at = DateTimeCol(default=datetime.now())
    completed_at = DateTimeCol(default=None)
    due = DateCol(default=None)
    tickler = DateCol(default=None)
    completed = BoolCol(default=False)
    next_todo = IntCol(default=None)
    previous_todo = IntCol(default=None)

# TODO: how the fuck can I for the use of innodb for mysql ?
#def connect(user = None, password = None, db_type = None):
def connect():
    """
    Connect to the database
    """
    # todo, generalisation
    sqlhub.processConnection = connectionForURI('mysql://tasks:toto@localhost/tasks')

def create_db():
    """
    Create the database if it isn't already create
    """
    Context.createTable(ifNotExists=True)
    Project.createTable(ifNotExists=True)
    Todo.createTable(ifNotExists=True)
    Item.createTable(ifNotExists=True)

def drop_db():
    """
    Drop the database if it isn't already drop
    """
    Context.dropTable(ifNotExists=True)
    Project.dropTable(ifNotExists=True)
    Todo.dropTable(ifNotExists=True)
    Item.dropTable(ifNotExists=True)

connect()
