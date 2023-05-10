from marshmallow_dataclass import dataclass
from marshmallow import Schema
from typing import ClassVar, List, Any, Type

@dataclass
class TitleInfo:
    language: str
    languageDisplayName: str
    title: str
    isOriginal: bool
    Schema: ClassVar[Type[Schema]] = Schema

@dataclass
class TagInfo:
    key: str
    isMeta: bool
    bojTagId: int
    problemCount: int
    Schema: ClassVar[Type[Schema]] = Schema

@dataclass
class SolvedacProblem:
    problemId: int
    titleKo: str
    titles: List[TitleInfo]
    isSolvable: bool
    isPartial: bool
    acceptedUserCount: int
    level: int
    votedUserCount: int
    sprout: bool
    givesNoRating: bool
    isLevelLocked: bool
    averageTries: float
    official: bool
    tags: List[TagInfo]
    metadata: Any
    Schema: ClassVar[Type[Schema]] = Schema

@dataclass
class SolvedacApiResult:
    count: int
    items: List[SolvedacProblem]
    Schema: ClassVar[Type[Schema]] = Schema