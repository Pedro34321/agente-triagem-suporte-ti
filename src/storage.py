import json
import sqlite3
import time
from .common import canonical, digest, tokens


class Store:
    def __init__(self, directory):
        self.directory = directory
        directory.mkdir(parents=True, exist_ok=True)
        self.path = directory / 'memoria.sqlite'
        with self.connect() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS triagens(id INTEGER PRIMARY KEY, key TEXT UNIQUE, owner TEXT, payload TEXT);
            CREATE TABLE IF NOT EXISTS episodios(key TEXT PRIMARY KEY, owner TEXT, payload TEXT, created REAL);
            CREATE TABLE IF NOT EXISTS fatos(key TEXT PRIMARY KEY, owner TEXT, name TEXT, value TEXT, stamp REAL);
            CREATE INDEX IF NOT EXISTS fatos_entidade ON fatos(owner,name,stamp);
            CREATE TABLE IF NOT EXISTS termos(termo TEXT, episode_key TEXT, PRIMARY KEY(termo,episode_key));
            CREATE TABLE IF NOT EXISTS threads(thread TEXT PRIMARY KEY, owner TEXT);
            ''')

    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA secure_delete=ON')
        return db

    def track(self, thread, owner):
        with self.connect() as db:
            row = db.execute('SELECT owner FROM threads WHERE thread=?', (thread,)).fetchone()
            if row and row['owner'] != owner:
                raise ValueError('Conversa pertence a outro usuário.')
            db.execute('INSERT OR IGNORE INTO threads VALUES(?,?)', (thread, owner))

    def fact(self, owner, name, value, stamp):
        key = digest([owner, name, value, stamp])
        with self.connect() as db:
            cur = db.execute('INSERT OR IGNORE INTO fatos VALUES(?,?,?,?,?)', (key, owner, name, canonical(value), stamp))
            return {'key': key, 'ja_existia': cur.rowcount == 0}

    def latest(self, owner, name):
        with self.connect() as db:
            rows = db.execute('SELECT * FROM fatos WHERE owner=? AND name=? ORDER BY stamp DESC,key DESC', (owner, name)).fetchall()
        return {'atual': dict(rows[0]) if rows else None, 'descartados': [dict(x) for x in rows[1:]]}

    def remember(self, owner, payload, created=None):
        key = digest([owner, payload])
        with self.connect() as db:
            cur = db.execute('INSERT OR IGNORE INTO episodios VALUES(?,?,?,?)', (key, owner, canonical(payload), created or time.time()))
            existed = cur.rowcount == 0
            for word in tokens(canonical(payload)):
                db.execute('INSERT OR IGNORE INTO termos VALUES(?,?)', (word, key))
        return {'key': key, 'ja_existia': existed, 'bytes': len(canonical(payload).encode())}

    def recall(self, owner, query, now=None):
        terms = sorted(tokens(query))
        if not terms:
            return []
        placeholders = ','.join('?' for _ in terms)
        with self.connect() as db:
            rows = db.execute(f'SELECT DISTINCT e.* FROM episodios e JOIN termos t ON e.key=t.episode_key WHERE e.owner=? AND t.termo IN ({placeholders})', [owner, *terms]).fetchall()
        ranked = []
        for row in rows:
            doc = tokens(row['payload'])
            score = len(set(terms) & doc) / max(1, len(set(terms) | doc))
            if (now or time.time()) - row['created'] > 90 * 86400:
                score *= 0.25
            ranked.append({'key': row['key'], 'payload': json.loads(row['payload']), 'score': round(score, 4)})
        return sorted(ranked, key=lambda x: (-x['score'], x['key']))[:2]

    def register(self, owner, case, decision):
        # Identidade inclui o caso e o conteúdo aprovado. Mesmo retry -> mesma chave.
        payload = {'case': case, 'decision': decision}
        key = digest([owner, payload])
        with self.connect() as db:
            cur = db.execute('INSERT OR IGNORE INTO triagens(key,owner,payload) VALUES(?,?,?)', (key, owner, canonical(payload)))
            existed = cur.rowcount == 0
            row = db.execute('SELECT id FROM triagens WHERE key=?', (key,)).fetchone()
        return {'registro_id': row['id'], 'ja_existia': existed, 'key': key}

    def forget(self, owner, checkpointer):
        with self.connect() as db:
            threads = [r['thread'] for r in db.execute('SELECT thread FROM threads WHERE owner=?', (owner,))]
            db.execute('DELETE FROM termos WHERE episode_key IN (SELECT key FROM episodios WHERE owner=?)', (owner,))
            for table in ('episodios', 'fatos', 'triagens', 'threads'):
                db.execute(f'DELETE FROM {table} WHERE owner=?', (owner,))
        for thread in threads:
            checkpointer.delete_thread(thread)
            log = self.directory / 'logs' / (digest(thread) + '.jsonl')
            log.unlink(missing_ok=True)
        # Não há cache persistente nem índice vetorial separado.
        with self.connect() as db:
            db.execute('VACUUM')
        return {'conversas_removidas': len(threads)}
