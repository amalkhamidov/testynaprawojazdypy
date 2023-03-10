from dataclasses import dataclass

from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class User:
    uuid: str
    id: int
    userName: str
    userType: str
    userSource: str
    lastAccessed: datetime
    phoneNumber: str
    internal: bool
    startPage: Optional[str]
    willBeBlockedAt: Optional[datetime]


@dataclass
class CourseModule:
    id: int
    moduleNumber: int
    name: str
    subjectsNumber: int


@dataclass
class Slide:
    id: int
    content: str


@dataclass
class Subject:
    id: int
    name: str
    slaidsNumber: int


@dataclass
class Slaid:
    id: int
    subjectId: int
    courseModuleId: int
    lessonNumber: int
    name: str
    content: str
    module: Optional[str]
    subject: Optional[str]
    attachements: Optional[str]
