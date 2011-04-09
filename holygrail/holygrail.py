#!/usr/bin/python
# -*- coding:Utf-8 -*-

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

import sqlobject
import os
import ConfigParser


from holygrail_exceptions import RealmDoesntExist,\
    MissionDoesntExist, RealmStillHasElems, CanRemoveTheDefaultRealm,\
    QuestDoesntExist, NoDatabaseConfiguration, WaitForError

from datetime import date, datetime, timedelta

config = ConfigParser.ConfigParser()
config.read(["holygrailrc", os.path.expanduser("~/.holygrailrc")])
DATABASE_ACCESS = config.get("holygrail", "uri") if config.has_option("holygrail", "uri") else None

__version__ = "Galahad 0.1"

class _Realm(sqlobject.SQLObject):
    """
    A realm.

    Realm contains missions. It can be, for example, "at home", "at work" etc...

    WARNING avoid as much as possible to modify directly the mission
    attribute, prefer the api, and if you do that be really SURE to know
    what you are doing. You don't want to break anything, right ?

    Your are not supposed to create a realm directly from this class, use
    add_realm() instead.
    """
    description = sqlobject.UnicodeCol()
    default_realm = sqlobject.BoolCol(default=False)
    created_at = sqlobject.DateCol(default=datetime.now())
    hide = sqlobject.BoolCol(default=False)
    position = sqlobject.IntCol(unique=True)

    def get_missions(self, all_missions=False):
        """
        Get the missions associated to this quest.

        Return a list of a list of missions.
        """
        def visible(mission):
            """
            A method that return True if the mission will be display in the main_view
            or in list_missions. You normaly needn't use it.
            """
            return (not mission.previous_mission or mission.previous_mission.completed)\
                and (not mission.quest or (not mission.quest.hide and not mission.quest.completed\
                and ((mission.quest.tickler == None) or (mission.quest.tickler < datetime.now()))))

        if not all_missions:
            for i in _Mission.select(sqlobject.AND(_Mission.q.completed == False, sqlobject.OR(_Mission.q.tickler == None, _Mission.q.tickler < datetime.now()), _Mission.q.realm == self)):
                if visible(i):
                    yield i
        else:
            for i in _Mission.select(_Mission.q.realm == self):
                yield i

    def change_position(self, new_position):
        """
        Change the position of the realm in the main_view.

        Arguments:
            * new_position: the new position of the realm, if the position is
              > at the max position, it will simply be put at the end
        """
        if new_position == self.position:
            return

        realms = [i for i in self.select().orderBy("position")]
        if new_position > self.position:
            # since insert() insert before
            realms.insert(new_position + 1, self)
            realms.remove(self)
        else:
            realms.remove(self)
            realms.insert(new_position, self)
        for i in realms:
            i.position = None
        for i in realms:
            i.position = realms.index(i)

    def remove(self):
        """
        Remove the realm.

        You can't remove a realm who has mission, RealmStillHasElems will be
        raised if you tried to.

        You can't remove the default realm, CanRemoveTheDefaultRealm will
        be raised if you tried to.
        """
        if self.default_realm:
            raise CanRemoveTheDefaultRealm
        elif _Mission.select(_Mission.q.realm == self).count() != 0:
            raise RealmStillHasElems
        else:
            self.destroySelf()

        # update position after removing one realm
        realms = [i for i in _Realm.select().orderBy("position")]
        i = 0
        while i < len(realms):
            realms[i].position = i
            i += 1

    def rename(self, new_description):
        """
        Change the description of the realm.

        Argument:
            * new_description: the realm's new description.
        """
        self.description = new_description

    def set_default(self):
        """
        Set this realm as the new default realm.
        """
        self.select(self.q.default_realm == True)[0].default_realm = False
        self.default_realm = True

    def toggle_hide(self):
        """
        Toggle if this realm is display in the main view.
        """
        self.hide = not self.hide


class _Mission(sqlobject.SQLObject):
    """
    A Mission object.

    WARNING avoid as much as possible to modify directly the mission
    attribute, prefer the api, and if you do that be really SURE to know
    what you are doing. You don't want to break anything, right ?

    Your are not supposed to create a mission directly from this class, use
    add_mission() instead.
    """
    description = sqlobject.UnicodeCol()
    created_at = sqlobject.DateCol(default=date.today())
    tickler = sqlobject.DateTimeCol(default=None)
    realm = sqlobject.ForeignKey('_Realm')
    quest = sqlobject.ForeignKey('_Quest', default=None)
    previous_mission = sqlobject.ForeignKey('_Mission', default=None)
    completed_at = sqlobject.DateTimeCol(default=None)
    _due = sqlobject.DateTimeCol(default=None)
    completed = sqlobject.BoolCol(default=False)

    def visible(self):
        """
        A method that return True if the mission will be display in the main_view
        or in list_missions. You normaly needn't use it.
        """
        return (not self.previous_mission or self.previous_mission.completed)\
            and not self.realm.hide\
            and (not self.quest or (not self.quest.hide and not self.quest.completed and ((self.quest.tickler == None) or (self.quest.tickler < datetime.now()))))

    def change_realm(self, realm_id):
        """
        Change the realm in witch the mission belongs.
        """
        self.realm = realm_id

    def change_quest(self, new_quest_id):
        """
        Change the quest in witch the mission is. Set it to None if you don't
        want this mission in a quest.

        Argument:
            * the new quest *id*
        """
        self.quest = new_quest_id

    def remove(self):
        """
        Remove the mission from the database.
        """
        # remove from mission that wait for this mission to be completed
        for i in self.select(_Mission.q.previous_mission == self):
            i.previous_mission = None
        self.destroySelf()

    def rename(self, description):
        """
        Rename the mission with a new description

        Arguments:
            * new description
        """
        self.description = description

    def tickle(self, tickler):
        """
        Change the mission tickler

        An mission with a tickle superior to now won't be display in list_missions
        or the main_view.

        Argument:
            * the new tickle *datetime*
        """
        self.tickler = tickler

    def wait_for(self, mission_id):
        """
        Define the mission that this mission will wait to be completed to appears in
        list_missions or the main_view.

        Argument:
            * the mission *id*
        """
        if mission_id is self:
            raise WaitForError("Can't wait for self")
        elif (mission_id.previous_mission and mission_id.previous_mission is self):
            raise WaitForError("Can't wait for a mission that is waiting for me")
        self.previous_mission = mission_id

    @property
    def tags(self):
        return [i.description for i in _TagMission.select(_TagMission.q.mission_id == self.id)]

    def add_tag(self, tag):
        if not _TagMission.select(sqlobject.AND(_TagMission.q.description == tag, _TagMission.q.mission_id == self)).count():
            _TagMission(mission_id = self.id, description = tag)
        else:
            assert _TagMission.select(sqlobject.AND(_TagMission.q.description == tag, _TagMission.q.mission_id == self)).count() == 1

    def remove_tag(self, req_tag):
        tag = _TagMission.select(sqlobject.AND(_TagMission.q.description == req_tag, _TagMission.q.mission_id == self))
        if tag.count() == 0:
            raise ValueError('tag "%s" doesn\'t exist' % tag)
        assert tag.count() == 1
        tag[0].destroySelf()

    @property
    def due(self):
        # return my due date if
        # I don't have a quest
        # my quest don't have a due date
        # my due date is earlier than the quest one
        # else, return quest due date
        return self._due if None == self.quest or\
                            (not self.quest.due or
                                (self._due != None and self.quest.due > self._due))\
                            else self.quest.due

    def due_for(self, due):
        """
        Change the due date.

        Argument:
            * the *datetime* for witch the mission is due.
        """
        self._due = due

    def toggle(self):
        """
        Toggle to mission completion state.
        """
        self.completed = not self.completed
        self.completed_at = datetime.now() if self.completed else None


class _TagMission(sqlobject.SQLObject):
    mission_id = sqlobject.ForeignKey("_Mission")
    description = sqlobject.UnicodeCol()


class _Quest(sqlobject.SQLObject):
    """
    A quest object.

    A quest is made of missions. It's basically everything you want to do that
    need more than one next action.

    WARNING avoid as much as possible to modify directly the mission
    attribute, prefer the api, and if you do that be really SURE to know
    what you are doing. You don't want to break anything, right ?

    Your are not supposed to create a quest directly from this class, use
    add_quest() instead.
    """
    description = sqlobject.UnicodeCol()
    created_at = sqlobject.DateCol(default=datetime.now())
    completed = sqlobject.BoolCol(default=False)
    completed_at = sqlobject.DateTimeCol(default=None)
    tickler = sqlobject.DateTimeCol(default=None)
    due = sqlobject.DateTimeCol(default=None)
    default_realm = sqlobject.ForeignKey('_Realm', default=None)
    hide = sqlobject.BoolCol(default=False)

    def get_missions(self, all_missions=False):
        """
        Get the missions associated to this quest.

        Return a list of a list of missions.
        """
        def visible(mission):
            """
            A method that return True if the mission will be display in the main_view
            or in list_missions. You normaly needn't use it.
            """
            return (not mission.previous_mission or mission.previous_mission.completed)\
                and (not mission.quest or (not mission.quest.hide and not mission.quest.completed\
                and ((mission.quest.tickler == None) or (mission.quest.tickler < datetime.now()))))

        return [i for i in _Mission.select(sqlobject.AND(_Mission.q.completed == False,
                sqlobject.OR(_Mission.q.tickler == None, _Mission.q.tickler < datetime.now()),\
                _Mission.q.quest == self)) if visible(i)]\
                if not all_missions\
                else [i for i in _Mission.select(_Mission.q.quest == self)]

    def due_for(self, due):
        """
        Change the due date.

        Argument:
            * the *datetime* for witch the mission is due.
        """
        self.due = due

    def remove(self):
        """
        Remove this quest.
        """
        for i in _Mission.select(_Mission.q.quest == self):
            i.quest = None
        self.destroySelf()

    def rename(self, new_description):
        """
        Change the description of this quest.

        Argument:
            * the new_description as a string
        """
        self.description = new_description

    def tickle(self, tickler):
        """
        Change the quest tickler. If the tickler of this quest is superior
        to now, this quest and it's mission won't be show.

        Argument:
            * the tickle in *datetime*
        """
        self.tickler = tickler

    def set_default_realm(self, realm_id):
        """
        Set the default realm for this quest. A mission or a mission add to this
        quest without a specified realm will take the default realm of
        the quest.

        Argument:
            * the new default realm *id*
        """
        self.default_realm = realm_id

    def toggle(self):
        """
        Toggle the completed state of this quest.

        Missions or mission from a completed quest won't appear anymore but won't be
        set to completed.
        """
        self.completed = not self.completed
        self.completed_at = datetime.now() if self.completed else None

    def toggle_hide(self):
        """
        Toggle the hidden state of a quest.

        Missions or mission from an hidden quest won't appears anymore.
        """
        self.hide = not self.hide


class Grail(object):

    def __init__(self, database_uri=None):
        """
        The main object, it's the interface with the mission database.

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
        if not ((not _Mission.tableExists() and not _Quest.tableExists() and not _Realm.tableExists()) or (_Mission.tableExists() and _Quest.tableExists() and _Realm.tableExists())):
            print "Grail: WARNING: database in a non conform state, will probably bug. Do you need to launch a migration script ?"
        elif not _Mission.tableExists() and not _Quest.tableExists() and not _Realm.tableExists():
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
            _Realm.dropTable(ifExists=True)
            _Quest.dropTable(ifExists=True)
            _Mission.dropTable(ifExists=True)
            _TagMission.dropTable(ifExists=True)


            _Realm.createTable()
            _Quest.createTable()
            _Mission.createTable()
            _TagMission.createTable()

            # always have a realm
            _Realm(description="default realm", default_realm = True, position=0)
        else:
            print "You aren't sure, so I won't reset it"

    def add_mission(self, new_description, tickler=None, due=None, quest=None, realm=None, wait_for=None, unique=False):
        """
        Add a new mission then return it

        Arguments:
            * new_description, the description of the mission
            * unique, don't add the mission if it's already exist AND ISN'T COMPLETED, return -1 if the mission already exist
            * tickler, a datetime object the tickle the mission, default to None
            * due, a datetime for when the mission is due, default to None
            * quest, the ID of the quest link to this new mission, default to None
            * realm, the ID of the realm link to this new mission, default is the default realm
            * wait_for, the ID of mission that this new mission wait to be completed to appears, default to None
        """
        if not realm:
            if not quest or not self.get_quest(quest).default_realm:
                realm = self.get_default_realm().id
            else:
                realm = self.get_quest(quest).default_realm.id
        if unique and _Mission.select(sqlobject.AND(_Mission.q.description == new_description, _Mission.q.completed == False)).count() != 0:
            return -1
        return _Mission(description=new_description, tickler=tickler, _due=due, quest=quest, realm=realm, previous_mission=wait_for)

    def add_quest(self, description, default_realm=None, tickler=None, due=None, hide=False):
        """
        Add a new quest then return it

        Arguments:
            * description, the quest description
            * default_realm, the default realm of this quest
            * tickler, the tickler of this quest in *datetime*
        """
        return _Quest(description=description, default_realm=default_realm, due=due, tickler=tickler, hide=hide)

    def add_realm(self, description, hide=False, default=False):
        """
        Add a new realm then return it

        Arguments:
            * description, the quest description
            * hide, if the quest is hide
            * default, if the quest is now the default realm
        """
        new_realm = _Realm(position=_Realm.select().count(), description=description, hide=hide)
        if default:
            new_realm.set_default()
        return new_realm

    def get_mission(self, mission_id):
        """
        Receive the id of a mission, return the mission
        Raise an exception if the mission doesn't exist

        Argument:
            * the mission description
        """
        try:
            return _Mission.get(mission_id)
        except sqlobject.SQLObjectNotFound:
            raise MissionDoesntExist(mission_id)

    def get_mission_by_desc(self, description):
        """
        Receive the description of a mission, return it
        Raise an exception if the mission doesn't exist

        Argument:
            * mission description
        """
        query = _Mission.select(_Mission.q.description == description)
        if query.count() == 0:
            raise MissionDoesntExist(description)
        return [i for i in query]

    def get_quest(self, quest_id):
        """
        Receive the id of a quest, return the quest
        Raise an exception if the quest doesn't exist

        Argument:
            * quest description
        """
        try:
            return _Quest.get(quest_id)
        except sqlobject.SQLObjectNotFound:
            raise QuestDoesntExist(quest_id)

    def get_quest_by_desc(self, description):
        """
        Receive the description of an quest, return it
        Raise an exception if the quest doesn't exist

        Arguments:
            * quest description
        """
        return [i for i in _Quest.select(_Quest.q.description == description)]

    def get_realm(self, realm_id):
        """
        Receive the id of a realm, return the realm
        Raise an exception if the realm doesn't exist

        Argument:
            * realm description
        """
        try:
            return _Realm.get(realm_id)
        except sqlobject.SQLObjectNotFound:
            raise RealmDoesntExist(realm_id)

    def get_realm_by_desc(self, description):
        """
        Receive the description of an realm, return it
        Raise an exception if the realm doesn't exist

        Arguments:
            * realm description
        """
        query = _Realm.select(_Realm.q.description == description)
        if query.count() == 0:
            raise RealmDoesntExist(description)
        return [i for i in query]

    def get_default_realm(self):
        """
        Return the default realm.
        """
        assert _Realm.select(_Realm.q.default_realm == True).count() == 1
        return _Realm.select(_Realm.q.default_realm == True)[0]

    def get_missions_from_tag(self, tag):
        return [i.mission_id for i in _TagMission.select(_TagMission.q.description == tag)]

    def list_missions(self, all_missions=False):
        """
        Return a generator of visible missions.

        Arguments:
            * all_missions=False by default, if True return all the missions.
        """
        if not all_missions:
            for i in _Mission.select(sqlobject.AND(_Mission.q.completed == False, sqlobject.AND(_Mission.q.realm == _Realm.q.id, _Realm.q.hide == False), sqlobject.OR(_Mission.q.tickler == None, _Mission.q.tickler < datetime.now()))):
                if i.visible():
                    yield i
        else:
            for i in _Mission.select():
                yield i

    def list_quests(self, all_quests=False):
        """
        Return a generator of visible quests.

        Arguments:
            * all_quests=False by default, if True return all the quests.
        """
        if not all_quests:
            for i in _Quest.select(sqlobject.AND(_Quest.q.hide == False, sqlobject.OR(_Quest.q.tickler == None, _Quest.q.tickler < datetime.now()))):
                yield i
        else:
            for i in _Quest.select():
                yield i

    def list_realms(self, all_realms=False):
        """
        Return a generator of visible realms.

        Arguments:
            * all_realms=False by default, if True return all the realms.
        """
        if not all_realms:
            for i in _Realm.select(_Realm.q.hide == False).orderBy("position"):
                yield i
        else:
            for i in _Realm.select().orderBy("position"):
                yield i

    def last_completed_missions(self, number=5):
        """
        Return a generator that contain the 5 last completed missions order in a reverse chronological order.

        Arguments:
            * number: the maximum number of missions returned
        """
        for i in _Mission.select(_Mission.q.completed == True).orderBy("-completed_at")[:number]:
            yield i

    def main_view(self):
        """
        Return the main view.

        The main view is a generator of lists of:
            - visible realm
            - generator of visible missions of this realm

        Order by the realm position.
        """
        def empty(a):
            try:
                a().next()
                return False
            except StopIteration:
                return True

        for i in self.list_realms():
            if not empty(i.get_missions):
                yield [i, i.get_missions()]

    def super_main_view(self):
        """
        Return the super main view.

        The main view is a list of lists of:
            - todo for today and late todo
            - todo for in 3 days
            - todo for this week
            - visible realm
            - list of visible missions of this realm

        Order by the realm position.
        """
        def list_missions():
            for i in _Mission.select(sqlobject.AND(_Mission.q.completed == False, _Mission.q._due < datetime.now() + timedelta(8), sqlobject.AND(_Mission.q.realm == _Realm.q.id, _Realm.q.hide == False), sqlobject.OR(_Mission.q.tickler == None, _Mission.q.tickler < datetime.now()))):
                if i.visible():
                    yield i

        def create_row(description, time_delta_value):
            row = [i for i in list_missions() if i.id not in removed and i.due and i.due < datetime.now() + timedelta(time_delta_value)]
            if not row:
                return
            row = sorted(row, key=lambda mission: mission._due)
            main_view.append([description, row])
            for i in row:
                removed.add(i.id)

        main_view = []
        removed = set()
        create_row("For today", 1)
        create_row("For in 3 days", 4)
        create_row("For this week", 8)

        main_view += filter(lambda item: item[1], [[realm, [i for i in realm.get_missions() if i.id not in removed]] for realm in self.list_realms()])

        return main_view

    def search_for_mission(self, description):
        """
        Receive a string, return all the mission that match that string

        Argument:
            * a string
        """
        return [i for i in _Mission.select(_Mission.q.description.contains(description))]


if __name__ == "__main__":
    pass
