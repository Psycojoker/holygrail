#!/usr/bin/python
# -*- coding:Utf-8 -*-

from sqlobject import *

from datetime import datetime

def connect(user = None, password = None, db_type = None):
    """
    Connect to the database
    """
    # todo, generalisation
    sqlhub.processConnection = connectionForURI('mysql://tasks:toto@localhost/tasks')

def create_db():
    """
    Create the database if it isn't already create
    """

    class Context(SQLObject):
        description = StringCol()
        position = IntCol(unique=True)
        hide = BoolCol(default=False)
        created_at = DateTimeCol(default=datetime.now())
        completed_at = DateTimeCol(default=None)

    Context.createTable(ifNotExists=True)

    class Project(SQLObject):
        description = StringCol()
        #position = IntCol()
        state = EnumCol(enumValues=('active', 'completed', 'hidden'), default="active")
        created_at = DateTimeCol(default=datetime.now())
        completed_at = DateTimeCol(default=None)
        tickler = DateCol(default=None)
        default_context_id = IntCol(default=None)

    Project.createTable(ifNotExists=True)

    class Todo(SQLObject):
        description = StringCol()
        context = ForeignKey('Context')
        project = IntCol(default=None)
        created_at = DateTimeCol(default=datetime.now())
        completed_at = DateTimeCol(default=None)
        due = DateCol(default=None)
        tickler = DateCol(default=None)
        state = EnumCol(enumValues=('active', 'completed', 'hidden'), default="active")
        next_todo = IntCol(default=None)
        previous_todo = IntCol(default=None)

    Todo.createTable(ifNotExists=True)

print Todo.select()
