from marshmallow_dataclass import dataclass
from marshmallow import EXCLUDE, Schema
from typing import ClassVar, List, Any, Type

@dataclass
class TitleInfo:
    language: str
    languageDisplayName: str
    title: str
    isOriginal: bool
    class Meta:
        unknown = EXCLUDE
@dataclass
class TagInfo:
    key: str
    isMeta: bool
    bojTagId: int
    problemCount: int
    class Meta:
        unknown = EXCLUDE

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
    class Meta:
        unknown = EXCLUDE

    def problemLink(self):
        return f'https://acmicpc.net/problem/{self.problemId}'

    def problemMarkDown(self):
        return f'[**{self.problemId}** {self.titleKo}]({self.problemLink()})'

@dataclass
class SolvedacApiResult:
    count: int
    items: List[SolvedacProblem]
    class Meta:
        unknown = EXCLUDE
