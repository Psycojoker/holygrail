HolyGrail
==========

http://worlddomination.be/holygrail

HolyGrail aims to be a base library to interact with a todo (missions)
database. It provides a simple interface allowing you to interact with your
todo in several ways. It's a GTD (getting things done) oriented approach.

This means that you can create and use whatever client you like (on the same
db) and even use multiple interfaces on the same database (ie: cli, mail, web
application etc).

Yes, this is nerdy and I like it.

My main inspiration is Tracks (getontracks.org).

This database handle:
 - missions (todos)
 - quests (projects)
 - realms (contexts)

and all operations on them via one main class: Grail.

I found the todo/project/context vocabulary boring and non motivating so I've
chose to use the medieval one.

If you like tracks main view, I have written a main_view method that recreate this behavior.

For the moment their isn't any released client but I'm working on a ncurse one
(I have also a really dirty cli client).

Installation
------------
::

    (sudo) python setup.py install

Create a ~/.holygrailrc file and add:

::

    [holygrail]
    uri=value # according to http://www.sqlobject.org/SQLObject.html#declaring-a-connection

For example for sqlite:

::

    uri=sqlite:/home/user/.holygrail.db

or for mysql (don't forget to create the username/database etc ...):

::

    uri=mysql://username:password@localhost/database

If you have questions, bugs etc ... ping me on irc.freenode.net, nick Bram,
or mail me at <cortex@worlddomination.be>

Tests
-----

::

    cd holygrail && python test_holygrail.py

Or use nosetests/py.test.

Changelog
---------
- 0.2.1 Perceval
    - Various doc updates and rehosting of the project on github
    - also: wheels

- 0.2 Perceval
    - API change: now every list_* methods return a generator, not a list. This increase the performances.
    - API change: last_completed_missions return only 5 missions by default, an argument can increase this number
    - fix a bug with quest and realm "get_missions" method that won't return any missions if the quest/realm is hidden
    - refactoring and various tests

- 0.1.2
    - fix fail import on privates class

- 0.1.1
    - get_missions() of realm and project now respect missions visibility and have an "all_mission attribute"
    - due missions in the super main view are now correctly sorted
    - unittests and refactoring for the super main view
    - when the database isn't specify in the config file, give an url who point to some help
    - update the remove method of realm description
    - remove method of a realm update the positions of the realms
    - list_realms(all_realms=True) now respect realms positions

- 0.1 Galahad
    - first release
