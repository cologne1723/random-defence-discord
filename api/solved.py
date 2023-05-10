import asyncio
from dataclasses import dataclass
import json
import aiohttp
from typing import Optional, Tuple, List, Mapping

from api.types import SolvedacApiResult, SolvedacProblem

sess = aiohttp.ClientSession()

async def solvedAcQuery(query: str, maxRetry: int = 5) -> SolvedacApiResult: 
    async def returnJson() -> str:
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
    
    return SolvedacApiResult.Schema.from_dict(json.loads(await returnJson()))
        

async def selectProblemNo(qry: str) -> Optional[SolvedacProblem]:
    res = await solvedAcQuery(qry)
    return res.items[0] if res.items else None



async def checklistsolved(queries: List[Tuple[int, str]]) -> Mapping[Tuple[int, str], bool]:
    probmap: Mapping[int, List[str]] = {}
    ret: Mapping[Tuple[int, str], bool] = {}
    for pid, iid in queries:
        if pid not in probmap:
            probmap[pid] = []
        probmap[pid].append(iid)

    while True:
        qt = []
        for k in probmap:
            if len(probmap[k]) > 0:
                qt.append((k, probmap[k].pop()))
        if len(qt) == 0:
            break
        qs = []
        for pid, iid in qt:
            qs.append(f'(id:{pid} @{iid})')
        qry = '|'.join(qs)
        J = await returnJson(qry)
        s = set()
        for v in J['items']:
            s.add(int(v['problemId']))

        for pid, iid in qt:
            ret[(pid, iid)] = (pid in s)

    return ret
