"""
Custom exceptions for toudoudone
"""

import exceptions

class ContextStillHasElems(exceptions.Exception):
    def __init__(self):
        super(ContextStillHasElems, self).__init__()

    def __str__(self):
        return 'This context still containt elems, can\'t remove it'

class TodoDoesntExist(exceptions.Exception):
    def __init__(self, todo):
        self.todo = todo
        super(TodoDoesntExist, self).__init__()

    def __str__(self):
        return 'this todo doesn\'t exist: %s' % self.todo

class ItemDoesntExist(exceptions.Exception):
    def __init__(self, item):
        self.item = item
        super(ItemDoesntExist, self).__init__()

    def __str__(self):
        return 'this item doesn\'t exist: %s' % self.item

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

class ProjectDoesntExist(exceptions.Exception):
    def __init__(self, project):
        self.project = project
        super(ProjectDoesntExist, self).__init__()

    def __str__(self):
        return 'this project doesn\'t exist: %s' % self.project

class NoDatabaseConfiguration(exceptions.Exception):
    def __init__(self):
        super(NoDatabaseConfiguration, self).__init__()

    def __str__(self):
        return "Their isn't any uri for the database, etheir give TodoDB an uri at creation or create a config file with a DATABASE_ACCESS variable that containt the string of the uri"

class WaitForError(exceptions.Exception):
    def __init__(self, error):
        self.error = error
        super(WaitForError, self).__init__()

    def __str__(self):
        return self.error
