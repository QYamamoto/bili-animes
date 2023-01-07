from sqlalchemy import Column, Integer, Text, create_engine, SmallInteger, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from itertools import accumulate

def average(v):
    total = sum(v)
    if total == 0:
        return 0
    return sum(accumulate(v[:0:-1])) * 2 / total

Model = declarative_base()
engine = create_engine('sqlite:///result.db?check_same_thread=False')

class Zero(Model):
    __tablename__ = 'zero'

    id = Column(Integer, primary_key=True, autoincrement=True)
    media_id = Column(Integer)
    name = Column(Text)
    uid = Column(Integer)
    content = Column(Text)

    @property
    def anime(self):
        return session.query(Anime).get(self.media_id)

    def __str__(self):
        return '''动画名: {anime}
动画ID: {media_id}
用户名: {name}
UID: {uid}
内容: {content}'''.format(anime=self.anime.title, **vars(self))

    def __repr__(self):
        return self.__str__()

class Review(Model):
    __tablename__ ='review'

    media_id = Column(Integer, primary_key=True)
    type = Column(SmallInteger, primary_key=True)
    zeros = Column(Integer)
    ones = Column(Integer)
    twos = Column(Integer)
    threes = Column(Integer)
    fours = Column(Integer)
    fives = Column(Integer)

    def __init__(self, **kwargs):
        self.zeros = 0
        self.ones = 0
        self.twos = 0
        self.threes = 0
        self.fours = 0
        self.fives = 0
        for k, v in kwargs.items():
            self.__setattr__(k, v)
    
    def add(self, stars):
        match stars:
            case 0:
                self.zeros += 1
            case 2:
                self.ones += 1
            case 4:
                self.twos += 1
            case 6:
                self.threes += 1
            case 8:
                self.fours += 1
            case 10:
                self.fives += 1

    def as_list(self):
        return [self.zeros, self.ones, self.twos, self.threes, self.fours, self.fives]

    @property
    def total(self):
        return sum(self.as_list())

    @property
    def average(self):
        return average(self.as_list())

    def __str__(self):
        return '''{}评:
0星    1星    2星    3星    4星    5星    总数   平均  
{:<7d}{:<7d}{:<7d}{:<7d}{:<7d}{:<7d}{:<7d}{}'''.format('长' if self.type else '短', *self.as_list(), self.total, self.average)

    def __repr__(self):
        return self.__str__()

class Anime(Model):
    __tablename__ = 'anime'

    media_id = Column(Integer, primary_key=True)
    chinese = Column(SmallInteger)
    title = Column(Text)
    score = Column(String(4))

    @property
    def short(self):
        return session.query(Review).filter_by(media_id=self.media_id, type=0).first()

    @property
    def long(self):
        return session.query(Review).filter_by(media_id=self.media_id, type=1).first()

    @property
    def short_and_long(self):
        return [a + b for a, b in zip(self.short.as_list(), self.long.as_list())]

    @property
    def average(self):
        return average(self.short_and_long)

    @property
    def total(self):
        return sum(self.short_and_long)

    @property
    def zeros(self):
        return session.query(Zero).filter_by(media_id=self.media_id)

    def __str__(self):
        return '''{} {}
ID: {}
分数: {}
实际分数: {}
人数: {}
{}
{}'''.format(
        '国创' if self.chinese else '番剧',
        self.title,
        self.media_id,
        self.score,
        self.average,
        self.total,
        self.short,
        self.long
    )

    def __repr__(self):
        return self.__str__()

def get_session():
    return sessionmaker(bind=engine)()

Model.metadata.create_all(engine)
session = sessionmaker(bind=engine)()