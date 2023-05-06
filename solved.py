import asyncio
from dataclasses import dataclass
import aiohttp
import json
from typing import Optional, Tuple, List, Mapping

sess = aiohttp.ClientSession()


@dataclass
class ICPCProblem:
    problemId: int
    problemName: str

    def problemLink(self):
        return f'https://acmicpc.net/problem/{self.problemId}'


async def returnJson(qry: str) -> any:

    r = 1
    while True:
        resp = await sess.get('https://solved.ac/api/v3/search/problem', params={
            'query': qry,
            'sort': 'random',
            'direction': 'asc',
        })

        T = await resp.read()
        if resp.status == 200:
            return json.loads(T)
        print('Status Code: ', resp.status)
        print('Response: ', T[:70])
        print(f'Retry after {r} second(s)...')
        await asyncio.sleep(r)
        r = min(1.5*r, 60)


async def selectProblemNo(qry: str) -> Optional[ICPCProblem]:
    J = await returnJson(qry)
    if J['count'] == 0:
        return None
    return ICPCProblem(J['items'][0]['problemId'], J['items'][0]['titleKo'])


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
