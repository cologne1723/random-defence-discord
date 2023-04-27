from dataclasses import dataclass
import requests
import json
from typing import Optional, Tuple, List, Mapping


@dataclass
class ICPCProblem:
    problemId: int
    problemName: str

    def problemLink(self):
        return f'https://acmicpc.net/problem/{self.problemId}'


def returnJson(qry: str) -> any:
    r = requests.get('https://solved.ac/api/v3/search/problem', params={
        'query': qry,
        'sort': 'random',
        'direction': 'asc',
    })
    assert r.status_code == 200
    J = json.loads(r.text)
    return J


def selectProblemNo(qry: str) -> Optional[ICPCProblem]:
    J = returnJson(qry)
    if J['count'] == 0:
        return None
    return ICPCProblem(J['items'][0]['problemId'], J['items'][0]['titleKo'])


def checksolved(problemid: int, icpcid: str) -> bool:
    print('Deferred.. switch to checklistsolved')
    return selectProblemNo(f'id:{problemid} s@{icpcid}') is not None


def checklistsolved(queries: List[Tuple[int, str]]) -> Mapping[Tuple[int, str], bool]:
    probmap: Mapping[int, List[str]] = {}
    ret: Mapping[Tuple[int, str], bool] = {}
    for pid, iid in queries:
        if pid not in probmap:
            probmap[pid] = []
        probmap[pid].append(iid)

    while True:
        qt = []
        print(probmap)
        for k in probmap:
            if len(probmap[k]) > 0:
                qt.append((k, probmap[k].pop()))
        if len(qt) == 0:
            break
        qs = []
        for pid, iid in qt:
            qs.append(f'(id:{pid} @{iid})')
        qry = '|'.join(qs)
        J = returnJson(qry)
        s = set()
        for v in J['items']:
            s.add(int(v['problemId']))

        print(qry, qs, s)
        for pid, iid in qt:
            print(pid, s)
            ret[(pid, iid)] = (pid in s)

    print(ret)
    return ret
