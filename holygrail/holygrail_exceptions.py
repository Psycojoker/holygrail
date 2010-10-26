"""
This file is part of HolyGrail.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

HolyGrail  Copyright (C) 2010  Laurent Peuch  <cortex@worlddomination.be>
"""


import exceptions

class RealmStillHasElems(exceptions.Exception):
    def __init__(self):
        super(RealmStillHasElems, self).__init__()

    def __str__(self):
        return 'This realm still containt elems, can\'t remove it'

class MissionDoesntExist(exceptions.Exception):
    def __init__(self, mission):
        self.mission = mission
        super(MissionDoesntExist, self).__init__()

    def __str__(self):
        return 'this mission doesn\'t exist: %s' % self.mission

class RealmDoesntExist(exceptions.Exception):
    def __init__(self, realm):
        self.realm = realm
        super(RealmDoesntExist, self).__init__()

    def __str__(self):
        return 'this realm doesn\'t exist: %s' % self.realm

class TableAlreadyExist(exceptions.Exception):
    def __init__(self, table):
        self.table = table
        super(TableAlreadyExist, self).__init__()

    def __str__(self):
        return "%s" % self.table

class CanRemoveTheDefaultRealm(exceptions.Exception):
    def __init__(self):
        super(CanRemoveTheDefaultRealm, self).__init__()

    def __str__(self):
        return "can't remove the default realm, change it before remove it"

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
        return """Their isn't any uri for the database, etheir give MissionDB an uri at creation or create a config file with a DATABASE_ACCESS variable that containt the string of the uri
    Do you have a ~/.holygrailrc ? Take a look here http://blog.worlddomination.be/holygrail/#configuration"""

class WaitForError(exceptions.Exception):
    def __init__(self, error):
        self.error = error
        super(WaitForError, self).__init__()

    def __str__(self):
        return self.error
