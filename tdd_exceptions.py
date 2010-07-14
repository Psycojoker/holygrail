"""
Custom exceptions for toudoudone
"""

import exceptions

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
