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

Toudoudone  Copyright (C) 2010  Laurent Peuch  <cortex@worlddomination.be>
"""

import sqlobject

from tdd_exceptions import TableAlreadyExist, ContextDoesntExist,\
    TodoDoesntExist, ContextStillHasTodos, CanRemoveTheDefaultContext,\
    ProjectDoesntExist, NoDatabaseConfiguration, ItemDoesntExist

from datetime import date, datetime

import config

DATABASE_ACCESS = config.DATABASE_ACCESS if hasattr(config, "DATABASE_ACCESS") else None

__version__ = "Ignus 0.1"

class _Context(sqlobject.SQLObject):
    description = sqlobject.StringCol()
    default_context = sqlobject.BoolCol(default=False)
    created_at = sqlobject.DateCol(default=datetime.now())
    hide = sqlobject.BoolCol(default=False)
    position = sqlobject.IntCol(unique=True)

    def change_position(self, new_position):
        if new_position == self.position:
            return

        contexts = [i for i in self.select().orderBy("position")]
        if new_position > self.position:
            # since insert() insert before
            contexts.insert(new_position + 1, self)
            contexts.remove(self)
        else:
            contexts.remove(self)
            contexts.insert(new_position, self)
        for i in contexts:
            i.position = None
        for i in contexts:
            i.position = contexts.index(i)

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

    def toggle_hide(self):
        self.hide = not self.hide

class _Item(sqlobject.SQLObject):
    description = sqlobject.StringCol()
    #context = ForeignKey('Context')
    #project = IntCol(default=None)
    #created_at = DateTimeCol(default=datetime.now())
    #hidden = BoolCol(default=False)
    #tickler = DateCol(default=None)
    #previous_todo = IntCol(default=None)

    def remove(self):
        """
        Remove the item from the database.
        """
        self.destroySelf()

class _Todo(_Item):
    """
    A Todo object.

    WARNING avoid as much as possible to modify directly the todo
    attribute, prefere the api, and if you do that be really SURE to know
    what you are doing. You don't want to break anything, right ?

    Arguments:
        * description: a text field that discribe the todo
    """
    context = sqlobject.ForeignKey('_Context')
    project = sqlobject.ForeignKey('_Project', default=None)
    created_at = sqlobject.DateCol(default=date.today())
    completed_at = sqlobject.DateCol(default=None)
    due = sqlobject.DateTimeCol(default=None)
    tickler = sqlobject.DateTimeCol(default=None)
    completed = sqlobject.BoolCol(default=False)
    previous_todo = sqlobject.ForeignKey('_Todo', default=None)
    # will wait popular demand to be implemented
    #notes = StringCol(default=None)

    def visible(self):
        return (not self.previous_todo or self.previous_todo.completed)\
            and not self.context.hide\
            and (not self.project or not self.project.hide)

    def wait_for(self, todo_id):
        self.previous_todo = todo_id

    def remove(self):
        """
        Remove the todo from the database.
        """
        # remove todo that wait for this todo to be completed
        for i in self.select(_Todo.q.previous_todo == self):
            i.previous_todo = None
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

    def change_project(self, new_project_id):
        self.project = new_project_id

class _Project(sqlobject.SQLObject):
    description = sqlobject.StringCol()
    created_at = sqlobject.DateCol(default=datetime.now())
    #completed_at = DateTimeCol(default=None)
    #tickler = DateCol(default=None)
    #due = DateCol(default=None)
    default_context = sqlobject.ForeignKey('_Context', default=None)
    hide = sqlobject.BoolCol(default=False)

    def rename(self, new_description):
        self.description = new_description

    def remove(self):
        for i in _Todo.select(_Todo.q.project == self):
            i.project = None
        self.destroySelf()

    def set_default_context(self, context_id):
        self.default_context = context_id

    def toggle_hide(self):
        self.hide = not self.hide

class TodoDB(object):

    def __init__(self, database_uri=None):
        """
        The main object, it's the interface with the todo database.

        Arguments:
            * a different uri to connect to another database than the one into
              the configuration file (ie for tests)
        """
        if not database_uri and not DATABASE_ACCESS:
            raise NoDatabaseConfiguration
        self._connect(database_uri)
        self._table_exist()

    def _table_exist(self):
        # check that everything if normal (all table created or not created)
        assert (not _Item.tableExists() and not _Todo.tableExists() and not _Project.tableExists() and not _Context.tableExists()) or (_Todo.tableExists() and _Project.tableExists() and _Context.tableExists() and _Item.tableExists())
        if not _Todo.tableExists() and not _Project.tableExists() and not _Context.tableExists() and not _Item.tableExists():
            # TODO uncomment for release
            #print "DB doesn't exist, I'll create it"
            self.create_db()

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
            _Project.createTable(ifNotExists=True)
            #Item.createTable(ifNotExists=True)
            _Todo.createTable()
            _Item.createTable()
        except Exception, e:
            # ultimely dirty, I really don't know why I push this
            # I haven't found another way to do this :(
            if str(e).endswith("exists"):
                raise TableAlreadyExist(str(e))
            else:
                raise e

        # always have a context
        _Context(description="default context", default_context = True, position=0)

    def drop_db(self):
        """
        Drop the database if it isn't already drop

        WARNING: this will destroy *everything* in the database
        """
        _Context.dropTable(ifExists=True)
        _Project.dropTable(ifExists=True)
        _Item.dropTable(ifExists=True)
        _Todo.dropTable(ifExists=True)

    def add_todo(self, new_description, tickler=None, due=None, project=None, context=None, wait_for=None, unique=False):
        """
        Add a new todo, return it

        Arguments:
            * the description of the todo
            * unique, don't add the todo if it's already exist AND INS'T COMPLETED
        """
        if not context:
            if not project or not self.get_project(project).default_context:
                context = self.get_default_context().id
            else:
                context = self.get_project(project).default_context.id
        if unique and _Todo.select(sqlobject.AND(_Todo.q.description == new_description, _Todo.q.completed == False)).count() != 0:
            return -1
        return _Todo(description=new_description, tickler=tickler, due=due, project=project, context=context, previous_todo=wait_for)

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
               sqlobject.OR(_Todo.q.tickler == None, _Todo.q.tickler < datetime.now()))).orderBy('id')\
                if i.visible()] if\
                not all_todos else [i for i in _Todo.select()]

    def add_context(self, description, hide=False, default=False):
        # TODO docstring
        new_context = _Context(position=_Context.select().count(), description=description, hide=hide)
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
        return [i for i in _Context.select(_Context.q.hide == False).orderBy("position")]

    def add_project(self, description, default_context=None):
        return _Project(description=description, default_context=default_context)

    def get_project(self, project_id):
        try:
            return _Project.get(project_id)
        except sqlobject.SQLObjectNotFound:
            raise ProjectDoesntExist(project_id)

    def get_project_by_desc(self, description):
        return [i for i in _Project.select(_Project.q.description == description)]

    def list_projects(self, all_projects=False):
        return [i for i in _Project.select(_Project.q.hide == False)]\
                if not all_projects else [i for i in _Project.select()]

    def add_item(self, description):
        return _Item(description=description)

    def get_item_by_desc(self, description):
        """
        Receive a the description of an item, return it
        Raise an exception if the item doesn't exist

        Arguments:
            * item description
        """
        query = _Item.select(_Item.q.description == description)
        if query.count() == 0:
            raise ItemDoesntExist(description)
        return [i for i in query]

if __name__ == "__main__":
    pass
