# requires: pymongo dnspython
# Забейте
import asyncio
import pymongo

import logging
logger = logging.getLogger(__name__)
from .. import loader, utils

class Student:
    def __init__(self, id: int, last_name: str, first_name: str, 
                    patronymic: str, grade: int, region: str, academ: bool):
        self.last_name = last_name
        self.first_name = first_name
        self.patronymic = patronymic
        self.grade = int(grade)
        self.region = region
        self.academ = bool(academ)
        self.approved = None
        self.id = int(id)
    
    def __str__(self):
        p = 'Академ' if self.academ else 'Отбор'
        # a = f'Уже вроде бы добавлен в чат (tg://user?id={self.approved})' if self.approved else 'Еще нет в чате'
        return f'[{p}.{self.id}] {self.last_name} {self.first_name} {self.patronymic}, '\
        '{self.grade} класс, из {self.region}s'

class SiriusMod(loader.Module):
    """Ищем поступивших на ИЮ2020"""
    def __init__(self):
        self.config = loader.ModuleConfig(
            # name - default - description
            "db_uri", None, "Database URI, if you dont know where to take it - nevermind",
            "db_db", None, "database",
            "db_coll", None, "collection"
        )
        self.name = 'sirius'
        self.db = None
    
    def config_complete(self):
        self.db = pymongo.MongoClient(self.config['db_uri'])\
            .get_database(self.config['db_db']).get_collection(self.config['db_coll'])

    async def findcmd(self, message):
        arg = ' '.join(utils.get_args_raw(message)).strip()
        if not arg:
            await utils.answer(message, 'Только 1 аргумент - номер в списке или фамилия/имя')
        if arg.isdigit():
            arg = int(arg)
            users = list(self.db.find({"id": arg}))
        elif ' ' in arg or arg.lower() == 'янао': # Костыли костыли
            _users = list(self.db.find())
            users = []
            for user in _users:
                if user['region'].lower() == arg.lower():
                    users.append(user)
        else:
            users = list(self.db.find({'$or': [{"last_name": arg}, {"first_name": arg}, {"patronymic": arg}]))

        msg = [f'{len(users)} всего', '==']
        for user in users:
            s = Student(**user)
            msg += [str(s), '==']
        msg = msg[:-1]
        msg = '\n'.join(msg)
        await utils.answer(message, msg)



