# -*- coding: utf-8 -*-
'''
@author: moloch

    Copyright 2013

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
----------------------------------------------------------------------------

This file contiains the user object, used to store data related to an
indiviudal user, such as handle/account/password/etc

'''


import logging

from os import urandom
from pbkdf2 import PBKDF2
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import synonym, relationship, backref
from sqlalchemy.types import Unicode, String
from models import DBSession, Permission
from models.BaseModels import DatabaseObject



### Constants
ADMIN_PERMISSION = u'admin'
ITERATE = 0xbad


class User(DatabaseObject):
    ''' User definition '''

    name = Column(Unicode(16), unique=True, nullable=False)

    _password = Column('password', String(64))
    password = synonym('_password', descriptor=property(
        lambda self: self._password,
        lambda self, password: setattr(
                self, '_password', self.__class__._hash_password(password))
        )
    )

    permissions = relationship("Permission",
        backref=backref("user", lazy="select"),
        cascade="all, delete-orphan"
    )

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return DBSession().query(cls).all()

    @classmethod
    def all_users(cls):
        ''' Return all non-admin user objects '''
        return filter(
            lambda user: user.has_permission(ADMIN_PERMISSION) is False, cls.all()
        )

    @classmethod
    def by_id(cls, _id):
        ''' Returns a the object with id of identifier '''
        return DBSession().query(cls).filter_by(id=_id).first()

    @classmethod
    def by_name(cls, _name):
        ''' Returns a the object with name of _name '''
        return DBSession().query(cls).filter_by(name=unicode(_name)).first()

    @classmethod
    def _hash_password(cls, password):
        return PBKDF2.crypt(password, iterations=ITERATE)

    @property
    def permission_names(self):
        ''' Return a list with all permissions accounts granted to the user '''
        return [permission.name for permission in self.permissions]

    def has_permission(self, permission):
        ''' Return True if 'permission' is in permissions_names '''
        return True if permission in self.permission_names else False

    def validate_password(self, attempt):
        ''' Check the password against existing credentials '''
        if self._password is not None:
            return self.password == PBKDF2.crypt(attempt, self.password)
        else:
            return False

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<User - name: %s>' % (self.name,)
