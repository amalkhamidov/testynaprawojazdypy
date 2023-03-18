
from sqlalchemy import Column, ForeignKey
from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import DeclarativeBase, relationship, declarative_base
from sqlalchemy.testing.schema import Table

Base = declarative_base()
metadata = Base.metadata


class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    moduleNumber = Column(Integer, index=True)
    name = Column(String, index=True)
    subjectsNumber = Column(Integer)

    slides = relationship("Slide")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String)
    type = Column(String)
    file = Column(String)
    autostart = Column(Boolean)

    slide_id = Column(Integer, ForeignKey("slides.id"))

    def __repr__(self):
        return '<Attachment {}:{}>'.format(self.id, self.file)


class Slide(Base):
    __tablename__ = "slides"

    id = Column(Integer, primary_key=True, index=True)
    subjectId = Column(Integer, index=True)
    lessonNumber = Column(Integer, index=True)
    name = Column(String)
    content = Column(String)
    formatted_content = Column(String)

    module_id = Column(Integer, ForeignKey("modules.id"))
    attachments = relationship("Attachment")
    audios = relationship("AudioDubbing")


class AudioDubbing(Base):
    __tablename__ = "audio_dubbings"

    id = Column(Integer, primary_key=True, index=True)
    audio = Column(String)

    slide_id = Column(Integer, ForeignKey("slides.id"))

    def __repr__(self):
        return '<AudioDubbing {}:{}>'.format(self.id, self.file)
