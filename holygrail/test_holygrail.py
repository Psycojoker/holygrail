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

import unittest, time

from datetime import date, datetime, timedelta

from holygrail import Grail, MissionDoesntExist, CanRemoveTheDefaultRealm, RealmDoesntExist, RealmStillHasElems, _Realm, QuestDoesntExist, _Mission, _Quest, WaitForError

def _to_list(sequence):
    return map(lambda x: [x[0], list(x[1])], list(sequence))

def comp_datetime(a, b):
    if a.year != b.year:
        return False
    if a.month != b.month:
        return False
    if a.day != b.day:
        return False
    if a.hour != b.hour:
        return False
    if a.second - b.second > 2:
        return False
    return True

class Test_Main(unittest.TestCase):

    def setUp(self):
        self.grail = self.reinitialise()

    def tearDown(self):
        self.grail.list_missions()
        self.grail.list_realms()
        self.grail.list_quests()

    def test_connect_to_another_database(self):
        Grail("sqlite:/:memory:")

    def reinitialise(self):
        """
        Reinitialise the db to make test with a clean one
        Use a sqlite db in memory to avoid losing user/dev data
        """
        grail = Grail('sqlite:/:memory:')
        grail.reset_db("yes")
        return grail

    def test_add_a_mission(self):
        """
        You should be able to add a new mission.
        This should inscrease the number of missions by one
        """
        was = len(list(self.grail.list_missions()))
        mission = self.grail.add_mission("This is a new mission")
        self.assertEqual(was + 1, len(list(self.grail.list_missions())))
        self.assertTrue(mission in self.grail.list_missions())

        # check if we can add two time a mission with the same description
        mission2 = self.grail.add_mission("This is a new mission")
        self.assertEqual(was + 2, len(list(self.grail.list_missions())))
        self.assertTrue(mission in self.grail.list_missions())
        self.assertTrue(mission2 in self.grail.list_missions())

    def test_add_mission_unique(self):
        mission = self.grail.add_mission("This is a new mission")
        self.assertEqual(-1, self.grail.add_mission("This is a new mission", unique=True))

    def test_add_mission_unique_toggle(self):
        mission = self.grail.add_mission("This is a new mission")
        mission.toggle()
        self.assertNotEqual(-1, self.grail.add_mission("This is a new mission", unique=True))

    def test_get_mission_by_desc(self):

        t1 = self.grail.add_mission("This is a new mission")
        t2 = self.grail.add_mission("This is a new mission 2")

        self.assertEqual(t1.id, self.grail.get_mission_by_desc("This is a new mission")[0].id)
        self.assertEqual(t2.id, self.grail.get_mission_by_desc("This is a new mission 2")[0].id)

    def test_get_mission_by_desc_mutiple(self):

        t1 = self.grail.add_mission("This is a new mission")
        t2 = self.grail.add_mission("This is a new mission")

        self.assertTrue(t1 in self.grail.get_mission_by_desc("This is a new mission"))
        self.assertTrue(t2 in self.grail.get_mission_by_desc("This is a new mission"))

    def test_get_mission_by_desc_should_raise_an_exection_if_mission_doesnt_exist(self):
        self.assertRaises(MissionDoesntExist, self.grail.get_mission_by_desc, "mission")

    def test_remove_mission(self):

        was = len(list(self.grail.list_missions()))
        mission = self.grail.add_mission("This is a new mission")

        self.assertEqual(was + 1, len(list(self.grail.list_missions())))

        id = mission.id
        mission.remove()

        self.assertEqual(was, len(list(self.grail.list_missions())))
        self.assertRaises(MissionDoesntExist, self.grail.get_mission, id)

    def test_seach_for_mission(self):

        mission_to_add = ("new mission", "another mission", "yet a mission", "missiondo", "missionmission")
        mission_to_add_that_doesnt_match = ("blabla", "foo", "bar")

        true = [self.grail.add_mission(i) for i in mission_to_add]
        false = [self.grail.add_mission(i) for i in mission_to_add_that_doesnt_match]
        result = self.grail.search_for_mission("mission")

        self.assertEqual(len(mission_to_add), len(result))

        for i in result:
            self.assertTrue(i.description in mission_to_add)
            self.assertTrue(i in true)
            self.assertFalse(i.description in mission_to_add_that_doesnt_match)
            self.assertFalse(i in false)

    def test_get_mission(self):
        mission = self.grail.add_mission("mission")
        self.assertTrue(mission is self.grail.get_mission(mission.id))
        self.assertEqual(mission.description, "mission")

    def test_get_mission_throw_except_if_doesnt_exist(self):
        self.assertRaises(MissionDoesntExist, self.grail.get_mission, 1337)

    def test_rename_mission(self):
        mission = self.grail.add_mission("first name")
        mission.rename("second name")
        self.assertEqual(mission.description, "second name")

    def test_toggle_mission(self):

        t = self.grail.add_mission("prout")

        self.assertFalse(t.completed)
        t.toggle()
        self.assertTrue(t.completed)
        t.toggle()
        self.assertFalse(t.completed)

    def test_list_missions(self):
        # empty
        self.assertEqual(0, len(list(self.grail.list_missions())))
        t = self.grail.add_mission("mission")
        # one mission
        self.assertEqual(1, len(list(self.grail.list_missions())))
        self.assertTrue(t in self.grail.list_missions())
        # two mission
        t2 = self.grail.add_mission("mission 2")
        self.assertEqual(2, len(list(self.grail.list_missions())))
        self.assertTrue(t in self.grail.list_missions())
        self.assertTrue(t2 in self.grail.list_missions())
        # only uncompleted
        t2.toggle()
        self.assertEqual(1, len(list(self.grail.list_missions())))
        self.assertTrue(t in self.grail.list_missions())
        self.assertTrue(t2 not in self.grail.list_missions())
        # everything
        self.assertEqual(2, len(list(self.grail.list_missions(all_missions=True))))
        self.assertTrue(t in self.grail.list_missions(all_missions=True))
        self.assertTrue(t2 in self.grail.list_missions(all_missions=True))

    def test_mission_should_be_created_today(self):
        mission = self.grail.add_mission("this is a mission")
        self.assertEqual(mission.created_at, date.today())

    def test_mission_completion_date(self):
        mission = self.grail.add_mission("this is a mission")
        self.assertEqual(mission.completed_at, None)
        mission.toggle()
        self.assertTrue(comp_datetime(mission.completed_at, datetime.now()))
        mission.toggle()
        self.assertEqual(mission.completed_at, None)
        mission.toggle()
        self.assertTrue(comp_datetime(mission.completed_at, datetime.now()))
        mission.toggle()
        self.assertEqual(mission.completed_at, None)

    def test_new_mission_shouldnt_have_tickler_by_default(self):
        mission = self.grail.add_mission("new mission")
        self.assertEquals(None, mission.tickler)

    def test_tickler_at_creation(self):
        tickler = datetime(2010, 06, 25)
        mission = self.grail.add_mission("new mission", tickler=tickler)
        self.assertEqual(tickler, mission.tickler)

    def test_add_tickle(self):
        tickler = datetime(2010, 06, 25)
        mission = self.grail.add_mission("new mission")
        mission.tickle(tickler)
        self.assertEqual(tickler, mission.tickler)

    def test_list_dont_show_tickle_task(self):
        # for tomorrow
        tickler = datetime.now() + timedelta(1)
        mission = self.grail.add_mission("new mission", tickler)
        self.assertTrue(mission not in self.grail.list_missions())

    def test_list_all_show_tickle_task(self):
        # for tomorrow
        tickler = datetime.now() + timedelta(1)
        mission = self.grail.add_mission("new mission", tickler)
        self.assertTrue(mission in self.grail.list_missions(all_missions=True))

    def test_due_date_at_creation(self):
        due = datetime(2010, 06, 25)
        mission = self.grail.add_mission("new mission", due=due)
        self.assertEqual(due, mission.due)

    def test_add_due(self):
        due = datetime(2010, 06, 25)
        mission = self.grail.add_mission("new mission")
        mission.due_for(due)
        self.assertEqual(due, mission.due)

    def test_tdd_should_have_a_realm_at_creation(self):
        self.assertEqual("default realm", _Realm.get(1).description)
        self.assertEqual(1, _Realm.select().count())

    def test_add_realm(self):
        realm = self.grail.add_realm("new realm")
        self.assertEqual(realm.description, "new realm")
        self.assertEqual(2, _Realm.select().count())

    def test_rename_realm(self):
        _Realm.get(1).rename("new description")
        self.assertEqual("new description", _Realm.get(1).description)

    def test_remove_realm(self):
        self.assertEqual(1, _Realm.select().count())
        realm = self.grail.add_realm("new realm")
        self.assertEqual(2, _Realm.select().count())
        realm.remove()
        self.assertEqual(1, _Realm.select().count())

    def test_remove_realm_conserve_order(self):
        default_realm = _Realm.select()[0]
        self.assertEqual(0, default_realm.position)
        realm2 = self.grail.add_realm("new realm")
        self.assertEqual(1, realm2.position)
        realm3 = self.grail.add_realm("other new realm")
        self.assertEqual(2, realm3.position)
        realm2.remove()
        self.assertEqual(0, default_realm.position)
        self.assertEqual(1, realm3.position)

    def test_default_realm_at_init(self):
        realm = self.grail.get_default_realm()
        self.assertEqual(1, realm.id)
        self.assertEqual(True, realm.default_realm)

    def test_change_default_realm(self):
        realm = self.grail.add_realm("new realm")
        realm.set_default()
        self.assertEqual(realm.default_realm, True)

    def test_their_should_only_be_one_default_realm(self):
        previous = self.grail.get_default_realm()
        realm = self.grail.add_realm("new realm")
        realm.set_default()
        self.assertEqual(False, previous.default_realm)
        self.assertEqual(realm, self.grail.get_default_realm())
        self.assertEqual(1, _Realm.select(_Realm.q.default_realm == True).count())

    def test_cant_remove_default_realm(self):
        # to avoid having the exception NeedAtLeastOneRealm if the exception we are waiting isn't raised
        # yes it will crash anyway
        self.grail.add_realm("prout")
        self.assertRaises(CanRemoveTheDefaultRealm, self.grail.get_default_realm().remove)

    def test_a_mission_should_have_the_default_realm(self):
        mission = self.grail.add_mission("a mission")
        self.assertEqual(mission.realm, self.grail.get_default_realm())
        mission = self.grail.add_mission("another mission")
        self.assertEqual(mission.realm, self.grail.get_default_realm())

    def test_get_realm_by_desc(self):
        realm = self.grail.add_realm("youpla")
        self.assertEqual(realm, self.grail.get_realm_by_desc("youpla")[0])

    def test_get_realm_by_desc_raise_if_dont_exist(self):
        self.assertRaises(RealmDoesntExist, self.grail.get_realm_by_desc, "I don't exist")

    def test_get_realm(self):
        realm = self.grail.add_realm("zoubiboulba suce mon zob")
        self.assertEqual(realm, self.grail.get_realm(realm.id))

    def test_get_realm_raise_if_dont_exist(self):
        self.assertRaises(RealmDoesntExist, self.grail.get_realm, 1337)

    def test_add_mission_with_special_realm(self):
        realm = self.grail.add_realm("je devrais aller dormir")
        mission = self.grail.add_mission("mouhaha", realm=realm.id)
        self.assertEqual(realm, mission.realm)

    def test_change_mission_realm(self):
        realm = self.grail.add_realm("je vais encore me coucher à pas d'heure ...")
        mission = self.grail.add_mission("aller dormir")
        mission.change_realm(realm.id)
        self.assertEqual(realm, mission.realm)

    def test_cant_delete_realm_with_missions(self):
        realm = self.grail.add_realm("TDD rosk")
        mission = self.grail.add_mission("HAHAHA I'M USING TEH INTERNETZ", realm=realm)
        self.assertRaises(RealmStillHasElems, realm.remove)

    def test_list_realms(self):
        self.assertTrue(self.grail.get_default_realm() in self.grail.list_realms())
        self.assertEqual(len(list(self.grail.list_realms())), 1)
        realm = self.grail.add_realm("foobar")
        self.assertEqual(len(list(self.grail.list_realms())), 2)
        realm.remove()
        self.assertEqual(len(list(self.grail.list_realms())), 1)

    def test_list_realms_positio(self):
        default = self.grail.get_default_realm()
        realm = self.grail.add_realm("foobar")
        realm2 = self.grail.add_realm("foofoobarbar")
        realms = list(self.grail.list_realms(all_realms=True))
        self.assertEqual(realms[0], default)
        self.assertEqual(realms[1], realm)
        self.assertEqual(realms[2], realm2)
        realm.change_position(2)
        realms = list(self.grail.list_realms(all_realms=True))
        self.assertEqual(realms[0], default)
        self.assertEqual(realms[2], realm)
        self.assertEqual(realms[1], realm2)

    def test_add_Realm_default(self):
        realm = self.grail.add_realm("zomg, ils ont osé faire un flim sur les schtroumphs", default=True)
        self.assertEqual(realm, self.grail.get_default_realm())
        self.assertTrue(realm.default_realm)

    def test_realm_should_have_a_creation_date(self):
        realm = self.grail.add_realm("les fils de teuphu c'est super")
        self.assertEqual(date.today(), realm.created_at)

    def test_add_quest(self):
        quest = self.grail.add_quest("quest apocalypse")
        self.assertEqual("quest apocalypse", quest.description)

    def test_get_quest(self):
        quest = self.grail.add_quest("quest manatan")
        self.assertEqual(quest, self.grail.get_quest(quest.id))

    def test_get_quest_raise_if_dont_exist(self):
        self.assertRaises(QuestDoesntExist, self.grail.get_quest, 42)

    def test_get_quest_by_desc(self):
        quest = self.grail.add_quest("acheter du saucisson")
        self.assertEqual(self.grail.get_quest_by_desc("acheter du saucisson")[0], quest)
        self.assertEqual(len(self.grail.get_quest_by_desc("acheter du saucisson")), 1)
        self.grail.add_quest("acheter du saucisson")
        self.assertEqual(len(self.grail.get_quest_by_desc("acheter du saucisson")), 2)
        self.assertEqual(len(self.grail.get_quest_by_desc("acheter des cornichons")), 0)

    def test_rename_quest(self):
        quest = self.grail.add_quest("j'ai envie de chocolat")
        quest.rename("the cake is a lie")
        self.assertEqual(quest.description, "the cake is a lie")

    def test_list_quests(self):
        self.assertEqual(0, len(list(self.grail.list_quests())))
        quest = self.grail.add_quest("ce truc a l'air super http://smarterware.org/6172/hilary-mason-how-to-replace-yourself-with-a-small-shell-script")
        self.assertTrue(quest in self.grail.list_quests())
        self.assertEqual(1, len(list(self.grail.list_quests())))

    def test_remove_quest(self):
        self.assertEqual(0, len(list(self.grail.list_quests())))
        quest = self.grail.add_quest("lovely code vortex")
        self.assertEqual(1, len(list(self.grail.list_quests())))
        old_id = quest.id
        quest.remove()
        self.assertRaises(QuestDoesntExist, self.grail.get_quest, old_id)
        self.assertEqual(0, len(list(self.grail.list_quests())))

    def test_change_mission_quest(self):
        quest = self.grail.add_quest("manger une pomme")
        mission = self.grail.add_mission("le nouveau leak d'ACTA est dégeulasse")
        mission.change_quest(quest.id)
        self.assertEqual(mission.quest, quest)

    def test_next_mission(self):
        mission1 = self.grail.add_mission("first mission")
        mission2 = self.grail.add_mission("second mission")
        mission2.wait_for(mission1)
        self.assertEqual(mission1, mission2.previous_mission)

    def test_list_mission_with_previous_mission(self):
        mission1 = self.grail.add_mission("first mission")
        mission2 = self.grail.add_mission("second mission")
        mission2.wait_for(mission1)
        self.assertTrue(mission2 not in self.grail.list_missions())

    def test_list_mission_with_previous_mission_with_completed(self):
        mission1 = self.grail.add_mission("first mission")
        mission2 = self.grail.add_mission("second mission")
        mission2.wait_for(mission1)
        mission1.toggle()
        self.assertTrue(mission2 in self.grail.list_missions())

    def test_add_mission_wait_for(self):
        mission1 = self.grail.add_mission("first mission")
        mission2 = self.grail.add_mission("second mission", wait_for=mission1.id)
        self.assertEqual(mission1, mission2.previous_mission)

    def test_add_mission_with_a_quest(self):
        quest = self.grail.add_quest("gare a Gallo")
        mission = self.grail.add_mission("first mission", quest=quest.id)
        self.assertEqual(quest, mission.quest)

    def test_quest_should_have_a_creation_date(self):
        quest = self.grail.add_quest("youplaboum")
        self.assertEqual(quest.created_at, date.today())

    def test_set_default_realm_to_quest(self):
        quest = self.grail.add_quest("youmi, I love chocolate")
        realm = self.grail.add_realm("pc")
        quest.set_default_realm(realm.id)
        self.assertEqual(realm, quest.default_realm)

    def test_set_default_realm_to_quest_at_creation(self):
        realm = self.grail.add_realm("pc")
        quest = self.grail.add_quest("youmi, I love chocolate", default_realm=realm.id)
        self.assertEqual(realm, quest.default_realm)

    def test_new_mission_with_quest_with_default_realm(self):
        realm = self.grail.add_realm("pc")
        quest = self.grail.add_quest("youmi, I love chocolate", default_realm=realm.id)
        mission = self.grail.add_mission("pataplouf", quest=quest.id)
        self.assertEqual(mission.realm, realm)

    def test_new_mission_with_quest_with_default_realm_and_realm(self):
        realm = self.grail.add_realm("pc")
        other_realm = self.grail.add_realm("mouhaha")
        quest = self.grail.add_quest("youmi, I love chocolate", default_realm=realm.id)
        mission = self.grail.add_mission("pataplouf", realm=other_realm, quest=quest.id)
        self.assertEqual(mission.realm, other_realm)

    def test_set_hide_realm(self):
        realm = self.grail.add_realm("pc")
        self.assertFalse(realm.hide)
        realm.toggle_hide()
        self.assertTrue(realm.hide)
        realm.toggle_hide()
        self.assertFalse(realm.hide)
        realm.toggle_hide()
        self.assertTrue(realm.hide)

    def test_hide_realm_in_list_realm(self):
        realm = self.grail.add_realm("pc")
        self.assertTrue(realm in self.grail.list_realms())
        realm.toggle_hide()
        self.assertFalse(realm in self.grail.list_realms())

    def test_list_all_realms(self):
        realm = self.grail.add_realm("pc", hide=True)
        self.assertFalse(realm in self.grail.list_realms())
        self.assertTrue(realm in self.grail.list_realms(all_realms=True))

    def test_realm_hide_at_creation(self):
        realm = self.grail.add_realm("pc", hide=True)
        self.assertTrue(realm.hide)

    def test_hide_realm_in_list_mission(self):
        realm = self.grail.add_realm("pc", hide=True)
        mission = self.grail.add_mission("atchoum", realm=realm)
        self.assertFalse(mission in self.grail.list_missions())
        self.assertTrue(mission in self.grail.list_missions(all_missions=True))

    def test_list_mission_with_previous_mission_with_deleted(self):
        mission1 = self.grail.add_mission("first mission")
        mission2 = self.grail.add_mission("second mission")
        mission2.wait_for(mission1)
        mission1.remove()
        self.assertTrue(mission2 in self.grail.list_missions())
        self.assertEqual(None, mission2.previous_mission)

    def test_remove_quest_with_missions(self):
        quest = self.grail.add_quest("tchikaboum")
        mission = self.grail.add_mission("arakiri", quest=quest.id)
        mission2 = self.grail.add_mission("arakirikiki", quest=quest.id)
        quest.remove()
        self.assertEqual(None, mission.quest)
        self.assertEqual(None, mission2.quest)

    def test_auto_create_tables(self):
        Grail('sqlite:/:memory:')
        _Realm.dropTable(ifExists=True)
        _Quest.dropTable(ifExists=True)
        _Mission.dropTable(ifExists=True)
        Grail('sqlite:/:memory:')
        self.assertTrue(_Mission.tableExists())
        self.assertTrue(_Realm.tableExists())
        self.assertTrue(_Quest.tableExists())

    def test_realm_position(self):
        realm = self.grail.get_default_realm()
        self.assertEqual(0, realm.position)

    def test_new_realm_position(self):
        realm = self.grail.add_realm("In Dublin fair city ...")
        self.assertEqual(1, realm.position)
        realm = self.grail.add_realm("where the girl are so pretty ...")
        self.assertEqual(2, realm.position)

    def test_change_realm_position_alone_default_to_max(self):
        realm1 = self.grail.get_default_realm()
        realm1.change_position(4)
        self.assertEqual(0, realm1.position)

    def test_change_realm_position_2_realms_no_change(self):
        realm1 = self.grail.get_default_realm()
        realm2 = self.grail.add_realm("realm2")
        realm1.change_position(0)
        self.assertEqual(0, realm1.position)
        self.assertEqual(1, realm2.position)

    def test_change_realm_position_2_realms(self):
        realm1 = self.grail.get_default_realm()
        realm2 = self.grail.add_realm("realm2")
        realm1.change_position(1)
        self.assertEqual(1, realm1.position)
        self.assertEqual(0, realm2.position)

    def test_change_realm_position_2_realms_default_to_max(self):
        realm1 = self.grail.get_default_realm()
        realm2 = self.grail.add_realm("realm2")
        realm1.change_position(4)
        self.assertEqual(1, realm1.position)
        self.assertEqual(0, realm2.position)

    def test_change_realm_position_2_realms_swap(self):
        realm1 = self.grail.get_default_realm()
        realm2 = self.grail.add_realm("realm2")
        realm2.change_position(0)
        self.assertEqual(0, realm2.position)
        self.assertEqual(1, realm1.position)

    def test_change_realm_position_2_realms_swap_reverse(self):
        realm1 = self.grail.get_default_realm()
        realm2 = self.grail.add_realm("realm2")
        realm1.change_position(1)
        self.assertEqual(0, realm2.position)
        self.assertEqual(1, realm1.position)

    def test_change_realm_position_2_realms_swap_reverse_default_to_max(self):
        realm1 = self.grail.get_default_realm()
        realm2 = self.grail.add_realm("realm2")
        realm1.change_position(6)
        self.assertEqual(0, realm2.position)
        self.assertEqual(1, realm1.position)

    def test_change_realm_position_3_realms(self):
        realm1 = self.grail.get_default_realm()
        realm2 = self.grail.add_realm("realm2")
        realm3 = self.grail.add_realm("realm3")
        realm1.change_position(6)
        self.assertEqual(1, realm3.position)
        self.assertEqual(0, realm2.position)
        self.assertEqual(2, realm1.position)

    def test_change_realm_position_3_realms_full(self):
        realm1 = self.grail.get_default_realm()
        realm2 = self.grail.add_realm("realm2")
        realm3 = self.grail.add_realm("realm3")
        realm2.change_position(6)
        self.assertEqual(1, realm3.position)
        self.assertEqual(2, realm2.position)
        self.assertEqual(0, realm1.position)
        realm1.change_position(6)
        self.assertEqual(0, realm3.position)
        self.assertEqual(1, realm2.position)
        self.assertEqual(2, realm1.position)
        realm3.change_position(6)
        self.assertEqual(2, realm3.position)
        self.assertEqual(0, realm2.position)
        self.assertEqual(1, realm1.position)
        realm3.change_position(0)
        self.assertEqual(0, realm3.position)
        self.assertEqual(1, realm2.position)
        self.assertEqual(2, realm1.position)
        realm2.change_position(1)
        self.assertEqual(0, realm3.position)
        self.assertEqual(1, realm2.position)
        self.assertEqual(2, realm1.position)

    def test_change_realm_position_6_realms(self):
        realm1 = self.grail.get_default_realm()
        realm1.rename("realm1")
        realm2 = self.grail.add_realm("realm2")
        realm3 = self.grail.add_realm("realm3")
        realm4 = self.grail.add_realm("realm4")
        realm5 = self.grail.add_realm("realm5")
        realm6 = self.grail.add_realm("realm6")
        realm1.change_position(4)
        self.assertEqual(4, realm1.position)
        self.assertEqual(0, realm2.position)
        self.assertEqual(1, realm3.position)
        self.assertEqual(2, realm4.position)
        self.assertEqual(3, realm5.position)
        self.assertEqual(5, realm6.position)

    def test_list_quest_by_position(self):
        realm1 = self.grail.get_default_realm()
        realm1.rename("realm1")
        realm2 = self.grail.add_realm("realm2")
        realm3 = self.grail.add_realm("realm3")
        realm4 = self.grail.add_realm("realm4")
        realm5 = self.grail.add_realm("realm5")
        realm6 = self.grail.add_realm("realm6")
        realm1.change_position(4)
        realms = list(self.grail.list_realms())
        self.assertEqual(realms[4], realm1)
        self.assertEqual(realms[0], realm2)
        self.assertEqual(realms[1], realm3)
        self.assertEqual(realms[2], realm4)
        self.assertEqual(realms[3], realm5)
        self.assertEqual(realms[5], realm6)

    def test_quest_hide(self):
        quest = self.grail.add_quest("lalala")
        self.assertFalse(quest.hide)
        quest.toggle_hide()
        self.assertTrue(quest.hide)
        quest.toggle_hide()
        self.assertFalse(quest.hide)

    def test_quest_hide_at_creation(self):
        quest = self.grail.add_quest("lalala", hide=True)
        self.assertTrue(quest.hide)

    def test_list_mission_with_quest_hide(self):
        quest = self.grail.add_quest("qsd")
        quest.toggle_hide()
        mission = self.grail.add_mission("toto", quest=quest.id)
        self.assertFalse(mission in self.grail.list_missions())
        self.assertTrue(mission in self.grail.list_missions(all_missions=True))

    def test_list_quest_and_quest_hide(self):
        quest = self.grail.add_quest("huhu")
        quest.toggle_hide()
        self.assertFalse(quest in self.grail.list_quests())

    def test_list_all_quests(self):
        quest = self.grail.add_quest("huhu")
        self.assertTrue(quest in self.grail.list_quests())
        self.assertTrue(quest in self.grail.list_quests(all_quests=True))
        quest.toggle_hide()
        self.assertFalse(quest in self.grail.list_quests())
        self.assertTrue(quest in self.grail.list_quests(all_quests=True))

    #def test_next_mission_for_item(self):
        #mission = self.grail.add_mission("mission")
        #item = self.grail.add_item("item")
        #item.wait_for(mission)
        #self.assertEqual(mission, item.previous_mission)

    #def test_list_item_with_previous_mission(self):
        #mission = self.grail.add_mission("mission")
        #item = self.grail.add_item("item")
        #item.wait_for(mission)
        #self.assertTrue(item not in self.grail.list_items())

    #def test_list_item_with_previous_mission_with_completed(self):
        #mission = self.grail.add_mission("first mission")
        #item = self.grail.add_item("second mission")
        #item.wait_for(mission)
        #mission.toggle()
        #self.assertTrue(item in self.grail.list_items())

    #def test_add_item_wait_for(self):
        #mission = self.grail.add_mission("first mission")
        #item = self.grail.add_item("second item", wait_for=mission.id)
        #self.assertEqual(mission, item.previous_mission)

    def test_quest_completion(self):
        quest = self.grail.add_quest("bah")
        self.assertFalse(quest.completed)
        quest.toggle()
        self.assertTrue(quest.completed)
        quest.toggle()
        self.assertFalse(quest.completed)

    def test_quest_completion_date(self):
        quest = self.grail.add_quest("yamakasi")
        quest.toggle()
        self.assertTrue(comp_datetime(datetime.now(), quest.completed_at))
        quest.toggle()
        self.assertEqual(None, quest.completed_at)

    def test_mission_with_quest_completion(self):
        quest = self.grail.add_quest("the wild rover")
        mission = self.grail.add_mission("s", quest=quest.id)
        quest.toggle()
        self.assertFalse(mission in self.grail.list_missions())

    def test_quest_tickler(self):
        quest = self.grail.add_quest("j'ai faim")
        tickler = datetime(2010, 06, 25)
        quest.tickle(tickler)
        self.assertEqual(tickler, quest.tickler)

    def test_quest_tickler_at_creation(self):
        tickler = datetime(2010, 06, 25)
        quest = self.grail.add_quest("j'ai faim", tickler=tickler)
        self.assertEqual(tickler, quest.tickler)

    def test_list_quest_tickler(self):
        # for tomorrow
        tickler = datetime.now() + timedelta(1)
        quest = self.grail.add_quest("haha, j'ai visité LA brasserie de Guiness", tickler=tickler)
        self.assertFalse(quest in self.grail.list_quests())
        self.assertTrue(quest in self.grail.list_quests(all_quests=True))

    def test_mission_with_quest_tickler(self):
        tickler = datetime.now() + timedelta(1)
        quest = self.grail.add_quest("j'avais pas réalisé que c'était eux qui avaient inventé le guiness world record book", tickler=tickler)
        mission = self.grail.add_mission("chier, il pleut", quest=quest.id)
        self.assertFalse(mission in self.grail.list_missions())
        self.assertTrue(mission in self.grail.list_missions(all_missions=True))

    def test_main_view(self):
        # empty since the only realm is empty
        self.assertEqual([], list(self.grail.main_view()))

    def test_main_view_one_mission(self):
        mission = self.grail.add_mission("kropotkine")
        self.assertEqual([[self.grail.get_default_realm(), [mission]]], _to_list(self.grail.main_view()))

    def test_main_view_one_mission_one_empty_realm(self):
        mission = self.grail.add_mission("kropotkikine")
        self.grail.add_realm("empty realm")
        self.assertEqual([[self.grail.get_default_realm(), [mission]]], _to_list(self.grail.main_view()))

    def test_main_view_one_mission_one_non_empty_realm(self):
        mission = self.grail.add_mission("kropotkikine")
        realm = self.grail.add_realm("realm")
        other_mission = self.grail.add_mission("James Joyce a l'air terrible", realm=realm)
        self.assertEqual([[self.grail.get_default_realm(), [mission]],
                          [realm, [other_mission]]], _to_list(self.grail.main_view()))
        self.assertEqual([[self.grail.get_default_realm(), [mission]],
                          [realm, [other_mission]]], _to_list(self.grail.main_view()))

    def test_last_completed_missions_empty(self):
        last_completed_missions = self.grail.last_completed_missions()
        self.assertEqual([], list(last_completed_missions))

    def test_last_completed_missions_one_mission(self):
        mission = self.grail.add_mission("pouet")
        mission.toggle()
        last_completed_missions = self.grail.last_completed_missions()
        self.assertEqual([mission], list(last_completed_missions))

    def test_last_completed_missions_multiple_missions(self):
        mission1 = self.grail.add_mission("pouet")
        mission2 = self.grail.add_mission("pouet pouet")
        mission3 = self.grail.add_mission("taratata pouet pouet")
        mission1.toggle()
        time.sleep(1)
        mission3.toggle()
        time.sleep(1)
        mission2.toggle()
        last_completed_missions = self.grail.last_completed_missions()
        self.assertEqual([mission2, mission3, mission1], list(last_completed_missions))

    def test_last_completed_missions_max_multiple_missions(self):
        for i in xrange(10):
            self.grail.add_mission("pouet").toggle()
        last_completed_missions = self.grail.last_completed_missions()
        self.assertEqual(5, len(list(last_completed_missions)))

    def test_last_completed_optionnal_argument(self):
        for i in xrange(10):
            self.grail.add_mission("pouet").toggle()
        last_completed_missions = self.grail.last_completed_missions(10)
        self.assertEqual(10, len(list(last_completed_missions)))

    def test_quest_due(self):
        quest = self.grail.add_quest("je code dans un avion qui revient d'irlande")
        due = datetime.now()
        quest.due_for(due)
        self.assertEqual(quest.due, due)

    def test_quest_due_at_creation(self):
        due = datetime.now()
        quest = self.grail.add_quest("je code dans un avion qui revient d'irlande", due=due)
        self.assertTrue(comp_datetime(quest.due, due))

    def test_quest_due_date_on_a_mission(self):
        due = datetime.now()
        quest = self.grail.add_quest("je code dans un avion qui revient d'irlande", due=due)
        mission = self.grail.add_mission("la gamine qui est dans le siège devant moi arrête pas de faire plein de conneries", quest=quest.id)
        self.assertTrue(comp_datetime(mission.due, due))

    def test_quest_due_date_on_a_mission_with_earlier_mission(self):
        due = datetime.now()
        quest = self.grail.add_quest("je code dans un avion qui revient d'irlande", due=(due + timedelta(1)))
        mission = self.grail.add_mission("la gamine qui est dans le siège devant moi arrête pas de faire plein de conneries", quest=quest.id, due=due)
        self.assertTrue(comp_datetime(mission.due, due))

    def test_quest_due_date_on_a_mission_with_later_mission(self):
        due = datetime.now()
        quest = self.grail.add_quest("je code dans un avion qui revient d'irlande", due=due)
        mission = self.grail.add_mission("la gamine qui est dans le siège devant moi arrête pas de faire plein de conneries", quest=quest.id, due=(due + timedelta(1)))
        self.assertTrue(comp_datetime(mission.due, due))

    def test_get_missions_on_realm_empty(self):
        realm = self.grail.add_realm("regardcitoyens ça déchire")
        self.assertEqual([], list(realm.get_missions()))

    def test_get_missions_on_realm_mission(self):
        realm = self.grail.add_realm("regardcitoyens ça déchire")
        mission = self.grail.add_mission("youplaboum", realm=realm.id)
        self.assertTrue(mission in realm.get_missions())

    def test_get_missions_on_quest_empty(self):
        quest = self.grail.add_quest("regardcitoyens ça déchire")
        self.assertEqual([], quest.get_missions())

    def test_get_missions_on_quest_mission(self):
        quest = self.grail.add_quest("regardcitoyens ça déchire")
        mission = self.grail.add_mission("youplaboum", quest=quest.id)
        self.assertTrue(mission in quest.get_missions())

    def test_cant_wait_for_a_mission_that_wait_for_you(self):
        mission1 = self.grail.add_mission("youplaboum")
        mission2 = self.grail.add_mission("tien, zimmermann se fait draguer sur twitter", wait_for=mission1)
        self.assertRaises(WaitForError, mission1.wait_for, mission2)

    def test_mission_cant_wait_for_self(self):
        mission = self.grail.add_mission("ima new mission")
        self.assertRaises(WaitForError, mission.wait_for, mission)

    def test_super_main_view_empty(self):
        self.assertEqual(self.grail.super_main_view(), [])

    def test_super_main_view_one_mission(self):
        mission = self.grail.add_mission("prout")
        default = self.grail.get_default_realm()
        self.assertEqual(self.grail.super_main_view(), [[default, [mission]]])

    def test_super_main_view_two_mission(self):
        mission = self.grail.add_mission("prout")
        mission2 = self.grail.add_mission("pouet")
        default = self.grail.get_default_realm()
        self.assertEqual(self.grail.super_main_view(), [[default, [mission, mission2]]])

    def test_super_main_view_two_realm_one_mission(self):
        mission = self.grail.add_mission("prout")
        realm = self.grail.add_realm("pouet")
        default = self.grail.get_default_realm()
        self.assertEqual(self.grail.super_main_view(), [[default, [mission]]])

    def test_super_main_view_two_realm_two_mission(self):
        mission = self.grail.add_mission("prout")
        realm = self.grail.add_realm("pouet")
        mission2 = self.grail.add_mission("pouet", realm=realm)
        default = self.grail.get_default_realm()
        self.assertEqual(self.grail.super_main_view(), [[default, [mission]], [realm, [mission2]]])

    def test_super_main_view_two_realm_for_mission(self):
        mission = self.grail.add_mission("prout")
        mission3 = self.grail.add_mission("prout")
        realm = self.grail.add_realm("pouet")
        mission2 = self.grail.add_mission("pouet", realm=realm)
        mission4 = self.grail.add_mission("pouet", realm=realm)
        default = self.grail.get_default_realm()
        self.assertEqual(self.grail.super_main_view(), [[default, [mission, mission3]], [realm, [mission2, mission4]]])

    def test_super_main_view_one_due_today(self):
        mission = self.grail.add_mission("prout", due=datetime.now())
        self.assertEqual(self.grail.super_main_view(), [["For today", [mission]]])

    def test_super_main_view_one_due_today_order(self):
        mission = self.grail.add_mission("prout", due=datetime.now() + timedelta(seconds=50))
        mission2 = self.grail.add_mission("prout", due=datetime.now())
        self.assertEqual(self.grail.super_main_view(), [["For today", [mission2, mission]]])

    def test_super_main_view_one_due_today_order_3_missions(self):
        mission = self.grail.add_mission("prout", due=datetime.now() + timedelta(seconds=50))
        mission2 = self.grail.add_mission("prout", due=datetime.now())
        mission3 = self.grail.add_mission("prout", due=datetime.now() + timedelta(seconds=20))
        self.assertEqual(self.grail.super_main_view(), [["For today", [mission2, mission3, mission]]])

    def test_super_main_view_one_due_3_days(self):
        mission = self.grail.add_mission("prout", due=(datetime.now() + timedelta(days=3)))
        self.assertEqual(self.grail.super_main_view(), [["For in 3 days", [mission]]])

    def test_super_main_view_one_due_in_3_days_order(self):
        mission = self.grail.add_mission("prout", due=datetime.now() + timedelta(days=3, seconds=100))
        mission2 = self.grail.add_mission("prout", due=datetime.now() + timedelta(days=3))
        self.assertEqual(self.grail.super_main_view(), [["For in 3 days", [mission2, mission]]])

    def test_super_main_view_one_due_this_week(self):
        mission = self.grail.add_mission("prout", due=(datetime.now() + timedelta(days=7)))
        self.assertEqual(self.grail.super_main_view(), [["For this week", [mission]]])

    def test_super_main_view_one_due_this_week_order(self):
        mission = self.grail.add_mission("prout", due=datetime.now() + timedelta(days=7, seconds=100))
        mission2 = self.grail.add_mission("prout", due=datetime.now() + timedelta(days=7))
        self.assertEqual(self.grail.super_main_view(), [["For this week", [mission2, mission]]])

    def test_super_main_view_one_due_today_3_days(self):
        mission = self.grail.add_mission("prout", due=datetime.now())
        mission2 = self.grail.add_mission("prout", due=(datetime.now() + timedelta(days=3)))
        self.assertEqual(self.grail.super_main_view(), [["For today", [mission]], ["For in 3 days", [mission2]]])

    def test_super_main_view_one_due_today_3_days_wee(self):
        mission = self.grail.add_mission("prout", due=datetime.now())
        mission2 = self.grail.add_mission("prout", due=(datetime.now() + timedelta(days=3)))
        mission3 = self.grail.add_mission("prout", due=(datetime.now() + timedelta(days=7)))
        self.assertEqual(self.grail.super_main_view(), [["For today", [mission]], ["For in 3 days", [mission2]], ["For this week", [mission3]]])

    def test_super_main_view_a_bit_of_everything(self):
        mission = self.grail.add_mission("prout", due=datetime.now())
        mission2 = self.grail.add_mission("prout", due=(datetime.now() + timedelta(days=3)))
        mission3 = self.grail.add_mission("prout", due=(datetime.now() + timedelta(days=7)))
        mimission = self.grail.add_mission("prout")
        mimission3 = self.grail.add_mission("prout")
        realm = self.grail.add_realm("pouet")
        mimission2 = self.grail.add_mission("pouet", realm=realm)
        mimission4 = self.grail.add_mission("pouet", realm=realm)
        default = self.grail.get_default_realm()
        self.assertEqual(self.grail.super_main_view(), [["For today", [mission]], ["For in 3 days", [mission2]], ["For this week", [mission3]] , [default, [mimission, mimission3]], [realm, [mimission2, mimission4]]])

    def test_super_late_missions(self):
        mission = self.grail.add_mission("prout", due=datetime.now() - timedelta(days=100))
        self.assertEqual(self.grail.super_main_view(), [["For today", [mission]]])

    def test_get_realm_missions(self):
        default = self.grail.get_default_realm()
        # empty
        self.assertEqual(0, len(list(default.get_missions())))
        t = self.grail.add_mission("mission")
        # one mission
        self.assertEqual(1, len(list(default.get_missions())))
        self.assertTrue(t in default.get_missions())
        # two mission
        t2 = self.grail.add_mission("mission 2")
        self.assertEqual(2, len(list(default.get_missions())))
        self.assertTrue(t in default.get_missions())
        self.assertTrue(t2 in default.get_missions())
        # only uncompleted
        t2.toggle()
        self.assertEqual(1, len(list(default.get_missions())))
        self.assertTrue(t in default.get_missions())
        self.assertTrue(t2 not in default.get_missions())
        # everything
        self.assertEqual(2, len(list(default.get_missions(all_missions=True))))
        self.assertTrue(t in default.get_missions(all_missions=True))
        self.assertTrue(t2 in default.get_missions(all_missions=True))

    def test_get_realm_missions_with_other_realm(self):
        default = self.grail.get_default_realm()
        realm = self.grail.add_realm("pouet pouet")
        # empty
        self.grail.add_mission("pwet pwet", realm=realm.id)
        self.assertEqual(0, len(list(default.get_missions())))
        t = self.grail.add_mission("mission")
        # one mission
        self.grail.add_mission("pwet pwet", realm=realm.id)
        self.assertEqual(1, len(list(default.get_missions())))
        self.assertTrue(t in default.get_missions())
        # two mission
        t2 = self.grail.add_mission("mission 2")
        self.grail.add_mission("pwet pwet", realm=realm.id)
        self.assertEqual(2, len(list(default.get_missions())))
        self.assertTrue(t in default.get_missions())
        self.grail.add_mission("pwet pwet", realm=realm.id)
        self.assertTrue(t2 in default.get_missions())
        # only uncompleted
        t2.toggle()
        self.grail.add_mission("pwet pwet", realm=realm.id)
        self.assertEqual(1, len(list(default.get_missions())))
        self.assertTrue(t in default.get_missions())
        self.grail.add_mission("pwet pwet", realm=realm.id)
        self.assertTrue(t2 not in default.get_missions())
        # everything
        self.grail.add_mission("pwet pwet", realm=realm.id)
        self.assertEqual(2, len(list(default.get_missions(all_missions=True))))
        self.assertTrue(t in default.get_missions(all_missions=True))
        self.grail.add_mission("pwet pwet", realm=realm.id)
        self.assertTrue(t2 in default.get_missions(all_missions=True))

    def test_get_realm_missions_dont_show_tickle_task(self):
        default = self.grail.get_default_realm()
        # for tomorrow
        tickler = datetime.now() + timedelta(1)
        mission = self.grail.add_mission("new mission", tickler)
        self.assertTrue(mission not in default.get_missions())

    def test_get_realm_missions_all_show_tickle_task(self):
        default = self.grail.get_default_realm()
        # for tomorrow
        tickler = datetime.now() + timedelta(1)
        mission = self.grail.add_mission("new mission", tickler)
        self.assertTrue(mission in default.get_missions(all_missions=True))

    def test_get_quest_missions(self):
        quest = self.grail.add_quest("pipapou")
        # empty
        self.assertEqual(0, len(list(quest.get_missions())))
        t = self.grail.add_mission("mission", quest=quest.id)
        # one mission
        self.assertEqual(1, len(list(quest.get_missions())))
        self.assertTrue(t in quest.get_missions())
        # two mission
        t2 = self.grail.add_mission("mission 2", quest=quest.id)
        self.assertEqual(2, len(list(quest.get_missions())))
        self.assertTrue(t in quest.get_missions())
        self.assertTrue(t2 in quest.get_missions())
        # only uncompleted
        t2.toggle()
        self.assertEqual(1, len(list(quest.get_missions())))
        self.assertTrue(t in quest.get_missions())
        self.assertTrue(t2 not in quest.get_missions())
        # everything
        self.assertEqual(2, len(list(quest.get_missions(all_missions=True))))
        self.assertTrue(t in quest.get_missions(all_missions=True))
        self.assertTrue(t2 in quest.get_missions(all_missions=True))

    def test_get_quest_missions_with_other_quest(self):
        quest = self.grail.add_quest("toto tata")
        other_quest = self.grail.add_quest("pouet pouet")
        # empty
        self.grail.add_mission("pwet pwet", quest=other_quest.id)
        self.assertEqual(0, len(list(quest.get_missions())))
        t = self.grail.add_mission("mission", quest=quest.id)
        # one mission
        self.grail.add_mission("pwet pwet", quest=other_quest.id)
        self.assertEqual(1, len(list(quest.get_missions())))
        self.assertTrue(t in quest.get_missions())
        # two mission
        t2 = self.grail.add_mission("mission 2", quest=quest.id)
        self.grail.add_mission("pwet pwet", quest=other_quest.id)
        self.assertEqual(2, len(list(quest.get_missions())))
        self.assertTrue(t in quest.get_missions())
        self.grail.add_mission("pwet pwet", quest=other_quest.id)
        self.assertTrue(t2 in quest.get_missions())
        # only uncompleted
        t2.toggle()
        self.grail.add_mission("pwet pwet", quest=other_quest.id)
        self.assertEqual(1, len(list(quest.get_missions())))
        self.assertTrue(t in quest.get_missions())
        self.grail.add_mission("pwet pwet", quest=other_quest.id)
        self.assertTrue(t2 not in quest.get_missions())
        # everything
        self.grail.add_mission("pwet pwet", quest=other_quest.id)
        self.assertEqual(2, len(list(quest.get_missions(all_missions=True))))
        self.assertTrue(t in quest.get_missions(all_missions=True))
        self.grail.add_mission("pwet pwet", quest=other_quest.id)
        self.assertTrue(t2 in quest.get_missions(all_missions=True))

    def test_get_quest_missions_dont_show_tickle_task(self):
        quest = self.grail.add_quest("yohoho !")
        # for tomorrow
        tickler = datetime.now() + timedelta(1)
        mission = self.grail.add_mission("new mission", tickler, quest=quest.id)
        self.assertTrue(mission not in quest.get_missions())

    def test_get_quest_missions_all_show_tickle_task(self):
        quest = self.grail.add_quest("flagada")
        # for tomorrow
        tickler = datetime.now() + timedelta(1)
        mission = self.grail.add_mission("new mission", tickler, quest=quest.id)
        self.assertTrue(mission in quest.get_missions(all_missions=True))

class TestTags(unittest.TestCase):

    def setUp(self):
        self.grail = self.reinitialise()

    def reinitialise(self):
        """
        Reinitialise the db to make test with a clean one
        Use a sqlite db in memory to avoid losing user/dev data
        """
        grail = Grail('sqlite:/:memory:')
        grail.reset_db("yes")
        return grail

    def test_tags_on_mission_empty(self):
        mission = self.grail.add_mission("plop")
        self.assertFalse(mission.tags)

    def test_tags_mission_one(self):
        mission = self.grail.add_mission("tatatags")
        mission.add_tag("plop")
        self.assertEqual(mission.tags, ["plop",])

    def test_tags_mission_avoid_duplication(self):
        mission = self.grail.add_mission("tatatags")
        mission.add_tag("plop")
        self.assertEqual(mission.tags, ["plop",])
        mission.add_tag("plop")
        self.assertEqual(mission.tags, ["plop",])

    def test_tags_mission_multiple(self):
        mission = self.grail.add_mission("tsointsoin")
        mission.add_tag("plop")
        mission.add_tag("plup")
        self.assertTrue("plop" in mission.tags)
        self.assertTrue("plup" in mission.tags)
        self.assertEqual(len(mission.tags), 2)

    def test_tags_mission_remove_tag(self):
        mission = self.grail.add_mission("tsointsoin")
        mission.add_tag("plop")
        mission.remove_tag("plop")
        self.assertEqual([], mission.tags)

    def test_tags_mission_remove_tags(self):
        mission = self.grail.add_mission("tsointsoin")
        mission.add_tag("plop")
        mission.add_tag("yop")
        mission.remove_tag("plop")
        self.assertEqual(["yop"], mission.tags)
        mission.remove_tag("yop")
        self.assertEqual([], mission.tags)

    def test_tags_mission_remove_tag_raise(self):
        mission = self.grail.add_mission("tsointsoin")
        mission.add_tag("plop")
        self.assertRaises(ValueError, mission.remove_tag, "ploup")

    def test_tags_mission_get_mission_empty(self):
        self.assertEqual([], self.grail.get_missions_from_tag("pouet"))

    def test_tags_mission_get_one_mission(self):
        mission1 = self.grail.add_mission("tsointsoin")
        mission1.add_tag("plop")
        self.assertEqual([mission1], self.grail.get_missions_from_tag("plop"))

    def test_tags_mission_get_two_missions(self):
        mission1 = self.grail.add_mission("tsointsoin")
        mission1.add_tag("plop")
        mission2 = self.grail.add_mission("tsointsoin")
        mission2.add_tag("plop")
        missions = self.grail.get_missions_from_tag("plop")
        self.assertTrue(mission1 in missions)
        self.assertTrue(mission2 in missions)
        self.assertEqual(2, len(missions))

    def test_mission_with_quest_without_datetime(self):
        quest = self.grail.add_quest("quest")
        mission = self.grail.add_mission("prout", quest=quest.id)
        self.grail.list_missions()

    # TODO: refactorer les exceptions, favoriser un message plutôt que plein d'exceptions différentes
    # TODO: faire un utils.py et rajouter plein de petits outils dedans comme un parseur de date etc ...
    # TODO: tien et si je faisais un nouveau attribut "drop" en plus de completed
    # TODO: add other search methods
    # TODO: spliter mes tests unitaires en plusieurs classes

if __name__ == "__main__":
   unittest.main()

