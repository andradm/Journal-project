import datetime
from datetime import date
import sys

from flask import Flask
from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *


DATABASE = SqliteDatabase('journal.db')

class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=20)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)

    def get_entries(self):
        return Entry.select().where(Entry.user == self)

    def get_stream(self):
        return Entry.select().where(Entry.user == self)

    @classmethod
    def create_user(cls, username, email, password, admin=False):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=admin
                )
        except IntegrityError:
            raise ValueError("User already exists.")


class Entry(Model):
    user = ForeignKeyField(
        model=User,
        related_name='entries'
    )
   
    title = CharField(max_length=200)
    time_spent = IntegerField()
    content = TextField()
    resources = TextField()
    date = DateField(default=datetime.datetime.now)
    created_date = DateTimeField(default=datetime.datetime.now)
    class Meta:
        database = DATABASE
        order_by = ('-created_date',)


def initialize():
    """Create the database and the table if they don't exist"""
    DATABASE.connect()
    DATABASE.create_tables([User, Entry], safe=True)
    DATABASE.close()