import asyncio
from collections import defaultdict
import json
import aiohttp
from typing import Optional, Tuple, List, Mapping
from marshmallow import EXCLUDE

import marshmallow_dataclass

from api.types import SolvedacApiResult, SolvedacProblem

async def solvedacQuery(query: str, maxRetry: int = 5) -> SolvedacApiResult:
    sess = aiohttp.ClientSession()
    async def returnJson() -> str:
        nonlocal maxRetry
        timeout = 1
        while True:
            try:
                resp = await sess.get('https://solved.ac/api/v3/search/problem', params = {
                    'query': query,
                    'sort': 'random',
                    'direction': 'asc',
                })
                assert resp.status == 200
                return await resp.read()
            except Exception as e:
                maxRetry -= 1
                if maxRetry <= 0:
                    raise e
                await asyncio.sleep(timeout)
                timeout = min(1.5*timeout, 60)

    schema = marshmallow_dataclass.class_schema(SolvedacApiResult)()
    return schema.loads(await returnJson())

async def selectRandomProblem(qry: str) -> Optional[SolvedacProblem]:
    res = await solvedacQuery(qry)
    return res.items[0] if res.items else None

async def CheckSolved(queries: List[Tuple[int, str]]) -> Mapping[Tuple[int, str], bool]:
    problemIdToUserIds: Mapping[int, List[str]] = defaultdict(list)
    returnMapping:  Mapping[Tuple[int, str], bool] = {}
    for problemId, userId in queries:
        problemIdToUserIds[problemId].append(userId)

    while True:
        queryBuilder: List[Tuple[int, str]] = []
        for problemId, userIds in problemIdToUserIds.items():
            if userIds:
                queryBuilder.append((problemId, userIds.pop()))
        if not queryBuilder:
            break

        queryString = '|'.join(f'(id:{problemId} @{userId})' for problemId, userId in queryBuilder)
        remoteResult = await solvedacQuery(queryString)
        solvedSet = set(problem.problemId for problem in  remoteResult.items)
        for problemId, userId in queryBuilder:
            returnMapping[(problemId, userId)] = problemId in solvedSet

    return returnMapping
