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

HolyGrail  Copyright (C) 2010  Laurent Peuch  <cortex@worlddomination.be>
"""

import sqlobject

from holygrail_exceptions import ContextDoesntExist,\
    TodoDoesntExist, ContextStillHasElems, CanRemoveTheDefaultContext,\
    ProjectDoesntExist, NoDatabaseConfiguration, ItemDoesntExist,\
    WaitForError

from datetime import date, datetime, timedelta

import config

DATABASE_ACCESS = config.DATABASE_ACCESS if hasattr(config, "DATABASE_ACCESS") else None

__version__ = "Galahad 0.1"

class _Context(sqlobject.SQLObject):
    """
    A context.

    Context contains todos and items. It can be, for example, "at home", "at
    work" etc...

    WARNING avoid as much as possible to modify directly the todo
    attribute, prefer the api, and if you do that be really SURE to know
    what you are doing. You don't want to break anything, right ?

    Your are not supposed to create a context directly from this class, use
    add_context() instead.
    """
    description = sqlobject.UnicodeCol()
    default_context = sqlobject.BoolCol(default=False)
    created_at = sqlobject.DateCol(default=datetime.now())
    hide = sqlobject.BoolCol(default=False)
    position = sqlobject.IntCol(unique=True)

    def get_todos_and_items(self):
        """
        Get the todos and the items associated to this project.

        Return a list of a list of todos and a list of items.
        [[todos], [items]]
        """
        return [[i for i in _Todo.select(_Todo.q.context == self)],
                [j for j in _Item.select(_Item.q.context == self)]]

    def change_position(self, new_position):
        """
        Change the position of the context in the main_view.

        Arguments:
            * new_position: the new position of the context, if the position is
              > at the max position, it will simply be put at the end
        """
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

    def remove(self):
        """
        Remove the context.

        You can't remove the default context, CanRemoveTheDefaultContext will
        be raised if you tried to.
        """
        if self.default_context:
            raise CanRemoveTheDefaultContext
        elif _Todo.select(_Todo.q.context == self).count() != 0\
            or _Item.select(_Item.q.context == self).count() != 0:
            raise ContextStillHasElems
        else:
            self.destroySelf()

    def rename(self, new_description):
        """
        Change the description of the context.

        Argument:
            * new_description: the context's new description.
        """
        self.description = new_description

    def set_default(self):
        """
        Set this context as the new default context.
        """
        self.select(self.q.default_context == True)[0].default_context = False
        self.default_context = True

    def toggle_hide(self):
        """
        Toggle if this context is display in the main view.
        """
        self.hide = not self.hide


class _TagItem(sqlobject.SQLObject):
    item_id = sqlobject.ForeignKey("_Item")
    description = sqlobject.UnicodeCol()


class _Item(sqlobject.SQLObject):
    """
    An item.

    An item is a non checkable todo. It can be used to list stuff you don't
    want to be checkable. It can (will, hit me with a stick) be easily
    transform into a todo.

    WARNING avoid as much as possible to modify directly the todo
    attribute, prefer the api, and if you do that be really SURE to know
    what you are doing. You don't want to break anything, right ?

    Your are not supposed to create a item directly from this class, use
    add_item() instead.
    """
    description = sqlobject.UnicodeCol()
    created_at = sqlobject.DateCol(default=date.today())
    tickler = sqlobject.DateTimeCol(default=None)
    context = sqlobject.ForeignKey('_Context')
    project = sqlobject.ForeignKey('_Project', default=None)
    previous_todo = sqlobject.ForeignKey('_Todo', default=None)

    @property
    def tags(self):
        return [i.description for i in _TagItem.select(_TagItem.q.item_id == self.id)]

    def add_tag(self, tag):
        if not _TagItem.select(sqlobject.AND(_TagItem.q.description == tag, _TagItem.q.item_id == self)).count():
            _TagItem(item_id = self.id, description = tag)
        else:
            assert _TagItem.select(sqlobject.AND(_TagItem.q.description == tag, _TagItem.q.item_id == self)).count() == 1

    def remove_tag(self, req_tag):
        tag = _TagItem.select(sqlobject.AND(_TagItem.q.description == req_tag, _TagItem.q.item_id == self))
        if tag.count() == 0:
            raise ValueError('tag "%s" doesn\'t exist' % tag)
        assert tag.count() == 1
        tag[0].destroySelf()

    def visible(self):
        """
        A method that return True if the item will be display in the main_view
        or in list_items. You normaly needn't use it.
        """
        return (not self.previous_todo or self.previous_todo.completed)\
            and not self.context.hide\
            and (not self.project or (not self.project.hide and not self.project.completed and ((self.project.tickler == None) or (self.project.tickler < datetime.now()))))

    def change_context(self, context_id):
        """
        Change the context in witch the item belongs.
        """
        self.context = context_id

    def change_project(self, new_project_id):
        """
        Change the project in witch the item is. Set it to None if you don't
        want this item in a project.

        Argument:
            * the new project *id*
        """
        self.project = new_project_id

    def remove(self):
        """
        Remove the item from the database.
        """
        self.destroySelf()

    def rename(self, description):
        """
        Rename the todo with a new description

        Arguments:
            * new description
        """
        self.description = description

    def tickle(self, tickler):
        """
        Change the item tickler

        An item with a tickle superior to now won't be display in list_items
        or the main_view.

        Argument:
            * the new tickle *datetime*
        """
        self.tickler = tickler

    def wait_for(self, todo_id):
        """
        Define the todo that this item will wait to be completed to appears in
        list_items or the main_view.

        Argument:
            * the todo *id*
        """
        if todo_id is self:
            raise WaitForError("Can't wait for self")
        elif (todo_id.previous_todo and todo_id.previous_todo is self):
            raise WaitForError("Can't wait for a todo that is waiting for me")
        self.previous_todo = todo_id


class _TagTodo(sqlobject.SQLObject):
    todo_id = sqlobject.ForeignKey("_Todo")
    description = sqlobject.UnicodeCol()


class _Todo(_Item):
    """
    A Todo object.

    WARNING avoid as much as possible to modify directly the todo
    attribute, prefer the api, and if you do that be really SURE to know
    what you are doing. You don't want to break anything, right ?

    Your are not supposed to create a todo directly from this class, use
    add_todo() instead.
    """
    completed_at = sqlobject.DateTimeCol(default=None)
    _due = sqlobject.DateTimeCol(default=None)
    completed = sqlobject.BoolCol(default=False)

    @property
    def tags(self):
        return [i.description for i in _TagTodo.select(_TagTodo.q.todo_id == self.id)]

    def add_tag(self, tag):
        if not _TagTodo.select(sqlobject.AND(_TagTodo.q.description == tag, _TagTodo.q.todo_id == self)).count():
            _TagTodo(todo_id = self.id, description = tag)
        else:
            assert _TagTodo.select(sqlobject.AND(_TagTodo.q.description == tag, _TagTodo.q.todo_id == self)).count() == 1

    def remove_tag(self, req_tag):
        tag = _TagTodo.select(sqlobject.AND(_TagTodo.q.description == req_tag, _TagTodo.q.todo_id == self))
        if tag.count() == 0:
            raise ValueError('tag "%s" doesn\'t exist' % tag)
        assert tag.count() == 1
        tag[0].destroySelf()

    @property
    def due(self):
        # return my due date if
        # I don't have a project
        # my project don't have a due date
        # my due date is earlier than the project one
        # else, return project due date
        return self._due if None == self.project or\
                            (not self.project.due or
                                (self._due != None and self.project.due > self._due))\
                            else self.project.due

    def due_for(self, due):
        """
        Change the due date.

        Argument:
            * the *datetime* for witch the todo is due.
        """
        self._due = due

    def remove(self):
        """
        Remove the todo from the database.
        """
        # remove from todo that wait for this todo to be completed
        for i in self.select(_Todo.q.previous_todo == self):
            i.previous_todo = None
        for i in _Item.select(_Item.q.previous_todo == self):
            i.previous_todo = None
        super(_Todo, self).remove()

    def toggle(self):
        """
        Toggle to todo completion state.
        """
        self.completed = not self.completed
        self.completed_at = datetime.now() if self.completed else None


class _Project(sqlobject.SQLObject):
    """
    A project object.

    A project is made of items and/or todos. It's basically everything you want
    to do that need more than one next action.

    WARNING avoid as much as possible to modify directly the todo
    attribute, prefer the api, and if you do that be really SURE to know
    what you are doing. You don't want to break anything, right ?

    Your are not supposed to create a project directly from this class, use
    add_project() instead.
    """
    description = sqlobject.UnicodeCol()
    created_at = sqlobject.DateCol(default=datetime.now())
    completed = sqlobject.BoolCol(default=False)
    completed_at = sqlobject.DateTimeCol(default=None)
    tickler = sqlobject.DateTimeCol(default=None)
    due = sqlobject.DateTimeCol(default=None)
    default_context = sqlobject.ForeignKey('_Context', default=None)
    hide = sqlobject.BoolCol(default=False)

    def get_todos_and_items(self):
        """
        Get the todos and the items associated to this project.

        Return a list of a list of todos and a list of items.
        [[todos], [items]]
        """
        return [[i for i in _Todo.select(_Todo.q.project == self)],
                [j for j in _Item.select(_Item.q.project == self)]]

    def due_for(self, due):
        """
        Change the due date.

        Argument:
            * the *datetime* for witch the todo is due.
        """
        self.due = due

    def remove(self):
        """
        Remove this project.
        """
        for i in _Todo.select(_Todo.q.project == self):
            i.project = None
        for i in _Item.select(_Item.q.project == self):
            i.project = None
        self.destroySelf()

    def rename(self, new_description):
        """
        Change the description of this project.

        Argument:
            * the new_description as a string
        """
        self.description = new_description

    def tickle(self, tickler):
        """
        Change the project tickler. If the tickler of this project is superior
        to now, this project and it's todo/items won't be show.

        Argument:
            * the tickle in *datetime*
        """
        self.tickler = tickler

    def set_default_context(self, context_id):
        """
        Set the default context for this project. A todo or a item add to this
        project without a specified context will take the default context of
        the project.

        Argument:
            * the new default context *id*
        """
        self.default_context = context_id

    def toggle(self):
        """
        Toggle the completed state of this project.

        Todos or items from a completed project won't appear anymore but won't be
        set to completed.
        """
        self.completed = not self.completed
        self.completed_at = datetime.now() if self.completed else None

    def toggle_hide(self):
        """
        Toggle the hidden state of a project.

        Todos or items from an hidden project won't appears anymore.
        """
        self.hide = not self.hide


class Grail(object):

    def __init__(self, database_uri=None):
        """
        The main object, it's the interface with the todo database.

        If the database doesn't exist but an URI is given or a config file
        exist, the database will be automatically created.

        Arguments:
            * a different uri to connect to another database than the one into
              the configuration file (ie for tests)
        """
        if not database_uri and not DATABASE_ACCESS:
            raise NoDatabaseConfiguration
        self._connect(database_uri)
        self._table_exist()

    def _table_exist(self):
        """
        Intern method to check if the database exist and if the database is in a normal state.
        """
        # check that everything if normal (all table created or not created)
        if not ((not _Item.tableExists() and not _Todo.tableExists() and not _Project.tableExists() and not _Context.tableExists()) or (_Todo.tableExists() and _Project.tableExists() and _Context.tableExists() and _Item.tableExists())):
            print "Grail: WARNING: database in a non conform state, will probably bug. Do you need to launch a migration script ?"
        elif not _Todo.tableExists() and not _Project.tableExists() and not _Context.tableExists() and not _Item.tableExists():
            print "Grail: DB doesn't exist, I'll create it"
            self.reset_db("yes")

    def _connect(self, database_uri):
        """
        Connect to the database

        Argument:
            * a different uri to connect to another database than the one in the config.py file (ie: for unittest)
        """
        sqlobject.sqlhub.processConnection = sqlobject.connectionForURI(database_uri) if database_uri else sqlobject.connectionForURI(DATABASE_ACCESS)

    def reset_db(self, are_you_sure=False):
        """
        Reset the database. Use with caution.

        WARNING: this will destroy *EVERYTHING* in the database
        """
        if are_you_sure:
            _Context.dropTable(ifExists=True)
            _Project.dropTable(ifExists=True)
            _Item.dropTable(ifExists=True)
            _Todo.dropTable(ifExists=True)
            _TagTodo.dropTable(ifExists=True)
            _TagItem.dropTable(ifExists=True)


            _Context.createTable()
            _Project.createTable()
            _Todo.createTable()
            _Item.createTable()
            _TagTodo.createTable()
            _TagItem.createTable()

            # always have a context
            _Context(description="default context", default_context = True, position=0)
        else:
            print "You aren't sure, so I won't reset it"

    def add_todo(self, new_description, tickler=None, due=None, project=None, context=None, wait_for=None, unique=False):
        """
        Add a new todo then return it

        Arguments:
            * new_description, the description of the todo
            * unique, don't add the todo if it's already exist AND ISN'T COMPLETED, return -1 if the todo already exist
            * tickler, a datetime object the tickle the todo, default to None
            * due, a datetime for when the todo is due, default to None
            * project, the ID of the project link to this new todo, default to None
            * context, the ID of the context link to this new todo, default is the default context
            * wait_for, the ID of todo that this new todo wait to be completed to appears, default to None
        """
        if not context:
            if not project or not self.get_project(project).default_context:
                context = self.get_default_context().id
            else:
                context = self.get_project(project).default_context.id
        if unique and _Todo.select(sqlobject.AND(_Todo.q.description == new_description, _Todo.q.completed == False)).count() != 0:
            return -1
        return _Todo(description=new_description, tickler=tickler, _due=due, project=project, context=context, previous_todo=wait_for)

    def add_item(self, description, context=None, tickler=None, project=None, wait_for=None):
        """
        Add a new item then return it

        Arguments:
            * new_description, the description of the item
            * tickler, a datetime object the tickle the item, default to None
            * project, the ID of the project link to this new item, default to None
            * context, the ID of the context link to this new item, default is the default context
            * wait_for, the ID of todo that this new item wait to be completed to appears, default to None
        """
        if not context:
            if not project or not self.get_project(project).default_context:
                context = self.get_default_context().id
            else:
                context = self.get_project(project).default_context.id
        return _Item(description=description, tickler=tickler, context=context, project=project, previous_todo=wait_for)

    def add_project(self, description, default_context=None, tickler=None, due=None, hide=False):
        """
        Add a new project then return it

        Arguments:
            * description, the project description
            * default_context, the default context of this project
            * tickler, the tickler of this project in *datetime*
        """
        return _Project(description=description, default_context=default_context, due=due, tickler=tickler, hide=hide)

    def add_context(self, description, hide=False, default=False):
        """
        Add a new context then return it

        Arguments:
            * description, the project description
            * hide, if the project is hide
            * default, if the project is now the default context
        """
        new_context = _Context(position=_Context.select().count(), description=description, hide=hide)
        if default:
            new_context.set_default()
        return new_context

    def get_todo(self, todo_id):
        """
        Receive the id of a todo, return the todo
        Raise an exception if the todo doesn't exist

        Argument:
            * the todo description
        """
        try:
            return _Todo.get(todo_id)
        except sqlobject.SQLObjectNotFound:
            raise TodoDoesntExist(todo_id)

    def get_todo_by_desc(self, description):
        """
        Receive the description of a todo, return it
        Raise an exception if the todo doesn't exist

        Argument:
            * todo description
        """
        query = _Todo.select(_Todo.q.description == description)
        if query.count() == 0:
            raise TodoDoesntExist(description)
        return [i for i in query]

    def get_item(self, item_id):
        """
        Receive the id of a item, return the item
        Raise an exception if the item doesn't exist

        Argument:
            * item description
        """
        try:
            return _Item.get(item_id)
        except sqlobject.SQLObjectNotFound:
            raise ItemDoesntExist(item_id)

    def get_item_by_desc(self, description):
        """
        Receive the description of an item, return it
        Raise an exception if the item doesn't exist

        Arguments:
            * item description
        """
        query = _Item.select(_Item.q.description == description)
        if query.count() == 0:
            raise ItemDoesntExist(description)
        return [i for i in query]

    def get_project(self, project_id):
        """
        Receive the id of a project, return the item
        Raise an exception if the project doesn't exist

        Argument:
            * project description
        """
        try:
            return _Project.get(project_id)
        except sqlobject.SQLObjectNotFound:
            raise ProjectDoesntExist(project_id)

    def get_project_by_desc(self, description):
        """
        Receive the description of an project, return it
        Raise an exception if the project doesn't exist

        Arguments:
            * project description
        """
        return [i for i in _Project.select(_Project.q.description == description)]

    def get_context(self, context_id):
        """
        Receive the id of a context, return the context
        Raise an exception if the context doesn't exist

        Argument:
            * context description
        """
        try:
            return _Context.get(context_id)
        except sqlobject.SQLObjectNotFound:
            raise ContextDoesntExist(context_id)

    def get_context_by_desc(self, description):
        """
        Receive the description of an context, return it
        Raise an exception if the context doesn't exist

        Arguments:
            * context description
        """
        query = _Context.select(_Context.q.description == description)
        if query.count() == 0:
            raise ContextDoesntExist(description)
        return [i for i in query]

    def get_default_context(self):
        """
        Return the default context.
        """
        assert _Context.select(_Context.q.default_context == True).count() == 1
        return _Context.select(_Context.q.default_context == True)[0]

    def get_todos_from_tag(self, tag):
        return [i.todo_id for i in _TagTodo.select(_TagTodo.q.description == tag)]

    def get_items_from_tag(self, tag):
        return [i.item_id for i in _TagItem.select(_TagItem.q.description == tag)]

    def list_todos(self, all_todos=False):
        """
        Return a list of visible todos.

        Arguments:
            * all_todos=False by default, if True return all the todos.
        """
        return [i for i in _Todo.select(sqlobject.AND(_Todo.q.completed == False,
               sqlobject.OR(_Todo.q.tickler == None, _Todo.q.tickler < datetime.now()))).orderBy('id')\
                if i.visible()] if\
                not all_todos else [i for i in _Todo.select()]

    def list_items(self, all_items=False):
        """
        Return a list of visible items.

        Arguments:
            * all_items=False by default, if True return all the items.
        """
        return [i for i in _Item.select(sqlobject.OR(_Item.q.tickler == None, _Item.q.tickler < datetime.now())) if i.visible()]\
                if not all_items else [i for i in _Item.select()]

    def list_projects(self, all_projects=False):
        """
        Return a list of visible projects.

        Arguments:
            * all_projects=False by default, if True return all the projects.
        """
        return [i for i in _Project.select(sqlobject.AND(_Project.q.hide == False, sqlobject.OR(_Project.q.tickler == None, _Project.q.tickler < datetime.now())))]\
                if not all_projects else [i for i in _Project.select()]

    def list_contexts(self, all_contexts=False):
        """
        Return a list of visible contexts.

        Arguments:
            * all_contexts=False by default, if True return all the contexts.
        """
        return [i for i in _Context.select(_Context.q.hide == False).orderBy("position")] if not all_contexts\
            else [i for i in _Context.select()]

    def last_completed_todos(self):
        """
        Return a list of the last completed todos order in a none chronological order.
        """
        to_return = [i for i in _Todo.select(_Todo.q.completed == True).orderBy("completed_at")]
        to_return.reverse()
        return to_return

    def main_view(self):
        """
        Return the main view.

        The main view is a list of lists of:
            - visible context
            - list of visible items of this context
            - list of visible todos of this context

        Order by the context position.
        """
        items = self.list_items()
        todos = self.list_todos()
        contexts = self.list_contexts()
        main_view = []
        if not items and not todos:
            return main_view
        for context in contexts:
            context_items = [i for i in items if i.context == context]
            context_todos = [i for i in todos if i.context == context]
            if context_todos or context_items:
                main_view.append([context, context_items, context_todos])

        return main_view

    def search_for_todo(self, description):
        """
        Receive a string, return all the todo that match that string

        Argument:
            * a string
        """
        return [i for i in _Todo.select(_Todo.q.description.contains(description))]


if __name__ == "__main__":
    pass
