import datetime
import pysqlite3 as sqlite3
from typing import List, Optional, Tuple

con = sqlite3.connect("qry.db")
cur = con.cursor()


def init():
    cur.execute('''
    CREATE TABLE IF NOT EXISTS "Messages" (
        "id"	INTEGER UNIQUE,
        "messageid"	TEXT NOT NULL UNIQUE,
        "timestamp" INTEGER,
        PRIMARY KEY("id" AUTOINCREMENT)
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS "Queries" (
        "id"	INTEGER NOT NULL,
        "solvedquery"	TEXT NOT NULL UNIQUE,
        PRIMARY KEY("id" AUTOINCREMENT)
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS "MessageProblems" (
        "id"	INTEGER UNIQUE,
        "messageid"	INTEGER NOT NULL,
        "userid"	INTEGER NOT NULL,
        "problemid"	INTEGER NOT NULL,
        "problemname" TEXT NOT NULL,
        "solved"	INTEGER NOT NULL,
    	"rolled"	INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY("id" AUTOINCREMENT),
        FOREIGN KEY("messageid") REFERENCES "Messages"(id),
        FOREIGN KEY("userid") REFERENCES "Users"(id)
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS "Users" (
        "id"	INTEGER UNIQUE,
        "icpcid"	TEXT NOT NULL UNIQUE,
        "discordid"	TEXT NOT NULL UNIQUE,
        "queryid"	INTEGER,
        PRIMARY KEY("id" AUTOINCREMENT),
        FOREIGN KEY("queryid") REFERENCES "Queries"(id)
    )
    ''')
    con.commit()


def findOrInsertQuery(query: str) -> int:
    cur.execute('''
    INSERT INTO "Queries"(solvedquery) VALUES (?) ON CONFLICT(solvedquery) DO NOTHING;
    ''', [query])
    con.commit()
    res = cur.execute('''
    SELECT id FROM "Queries" where solvedquery = ?
    ''', [query])
    return res.fetchone()[0]

# Returns u.id, u.icpcid, q.solvedquery


def fetchAllUser() -> List[Tuple[int, str, str]]:
    cur.execute('''
        SELECT u.id, u.icpcid, q.solvedquery FROM "Users" u
        INNER JOIN "Queries" q on q.id=u.queryid;
    ''')
    return cur.fetchall()


# Returns icpcid, solvedquery
def getQueryOfUser(discordid: int) -> Optional[Tuple[str, str]]:
    cur.execute('''
        SELECT u.icpcid, q.solvedquery FROM "Users" u
        INNER JOIN "Queries" q on q.id=u.queryid
        WHERE u.discordid = ?
    ''', [discordid])
    x = cur.fetchall()
    if len(x) == 0:
        return None
    return x[0]


# Returns u.discordid, u.icpcid, q.solvedquery
def fetchAllUserWithDiscordId() -> List[Tuple[str, str, str]]:
    cur.execute('''
        SELECT u.discordid, u.icpcid, q.solvedquery FROM "Users" u
        INNER JOIN "Queries" q on q.id=u.queryid
        ORDER BY q.solvedquery DESC, u.icpcid ASC;
    ''')
    return cur.fetchall()


def upsertUser(discordid: str, icpcid: str, query: str) -> None:
    queryId = findOrInsertQuery(query)
    cur.execute('''
        INSERT INTO "Users"(icpcid, discordid, queryid) VALUES (?, ?, ?)
        ON CONFLICT(discordid) DO UPDATE SET
        icpcid = excluded.icpcid,
        queryid = excluded.queryid
    ''', [icpcid, discordid, queryId])
    con.commit()

def loadSolvedStatusFromDiscordMessageId(discordmessageid: int) -> List[Tuple[str, int, str, int, int]]:
    """
    Returns icpcid, problemid, problemname, solved, rolled
    """
    res = cur.execute('''
        SELECT icpcid, problemid, problemname, solved, rolled from "Messages" m
        JOIN "MessageProblems" mp ON m.id = mp.messageid
        JOIN "Users" u ON u.id = mp.userid
        WHERE m.messageid = ?
    ''', [discordmessageid])
    return res.fetchall()

# id, icpcid, problemid


def getPendingProblems(discordmessageid: int) -> List[Tuple[int, str, int]]:
    res = cur.execute('''
        SELECT mp.id, icpcid, problemid from "Messages" m
        JOIN "MessageProblems" mp ON m.id = mp.messageid
        JOIN "Users" u ON u.id = mp.userid
        WHERE m.messageid = ? AND solved=2
    ''', [discordmessageid])
    return res.fetchall()


def getUnsolvedOrPendingUsers(discordmessageid: int) -> List[str]:
    res = cur.execute('''
        SELECT u.discordid from "Messages" m
        JOIN "MessageProblems" mp ON m.id = mp.messageid
        JOIN "Users" u ON u.id = mp.userid
        WHERE m.messageid = ? AND (solved=2 OR solved=0)
    ''', [discordmessageid])
    return res.fetchall()


def updateSolvedStatus(mpid: int, solved: int):
    cur.execute('''
        UPDATE "MessageProblems" SET solved=?
        WHERE id = ?
    ''', [solved, mpid])
    con.commit()

def setLastDefenceProblem(discordid: int, problemid: int, problemname: str, rolled: int):
    res = cur.execute('''
        SELECT id FROM "Messages"
        ORDER BY timestamp DESC
        LIMIT 1;
    ''')
    lastid = res.fetchone()[0]

    res = cur.execute('''
        SELECT mp.id FROM "MessageProblems" mp
        INNER JOIN "Users" u ON u.id = mp.userid
        WHERE mp.messageid = ? AND u.discordid = ?
    ''', [lastid, discordid])
    mpids = res.fetchall()

    if len(mpids) == 0:
        res = cur.execute('''
            SELECT id FROM "Users" WHERE discordid = ?
        ''', [discordid])
        userid = res.fetchone()[0]
        cur.execute('''
            INSERT INTO "MessageProblems"
            (messageid, userid, problemid, problemname, solved, rolled)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', [lastid, userid, problemid, problemname, 0, rolled])
    else:
        mpid = mpids[0]
        cur.execute('''
            UPDATE "MessageProblems" SET
            solved = 0,
            problemid = ?,
            problemname = ?,
            rolled = ?
            WHERE id = ?
        ''', [problemid, problemname, rolled, mpid[0]])
    con.commit()        


def getLastMessageId() -> str:
    res = cur.execute('''
        SELECT messageid FROM "Messages"
        ORDER BY timestamp DESC
        LIMIT 1;
    ''')
    return res.fetchone()[0]


def MakeUnsolvedProblemPending(discordmessageid: int):
    cur.execute('''
    UPDATE "MessageProblems" SET solved=2
    WHERE id in (
        SELECT mp.id from "Messages" m
        JOIN "MessageProblems" mp ON m.id = mp.messageid
        JOIN "Users" u ON u.id = mp.userid
        WHERE m.messageid = ? AND solved=0
    );''', [discordmessageid])
    con.commit()


def postMessage(messageid: int) -> int:
    cur.execute('''
        INSERT INTO "Messages"(messageid, timestamp) VALUES (?, ?)
    ''', [messageid, int(datetime.datetime.now().timestamp())])
    con.commit()
    res = cur.execute('''
    SELECT id FROM "Messages" where messageid = ?
    ''', [messageid])
    return res.fetchone()[0]


def setSolvedStatus(messageid: int, userid: int, solved: int):
    cur.execute('''
    UPDATE "MessageProblems" SET solved = ?
    WHERE id in (
        SELECT mp.id from "Messages" m
        JOIN "MessageProblems" mp ON m.id = mp.messageid
        JOIN "Users" u ON u.id = mp.userid
        WHERE m.messageid = ? AND u.discordid = ?
    )
    ''', [solved, messageid, userid])
    con.commit()


def addProblem(messagedbid: int, userid: int, problemid: int, problemname: str) -> None:
    cur.execute('''
        INSERT INTO "MessageProblems"
        (messageid, userid, problemid, problemname, solved)
        VALUES (?, ?, ?, ?, ?)
    ''', [messagedbid, userid, problemid, problemname, 0])
    con.commit()
