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

class QuestDoesntExist(exceptions.Exception):
    def __init__(self, quest):
        self.quest = quest
        super(QuestDoesntExist, self).__init__()

    def __str__(self):
        return 'this quest doesn\'t exist: %s' % self.quest

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
