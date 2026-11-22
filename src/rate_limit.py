"""Espaçamento local compartilhado pelas invocações da CLI, sem dados do usuário."""
import sqlite3
import time
from pathlib import Path


def wait_for_slot(path, provider, interval, timeout, clock=time.time, sleep=time.sleep):
    if not 0 <= interval <= 60:
        raise ValueError('Intervalo deve estar entre 0 e 60 segundos.')
    if interval == 0:
        return 0.0
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(path,timeout=min(5,max(0.1,timeout))) as db:
        db.execute('CREATE TABLE IF NOT EXISTS slots (provider TEXT PRIMARY KEY, next_at REAL NOT NULL)')
        db.execute('BEGIN IMMEDIATE')
        now=clock()
        row=db.execute('SELECT next_at FROM slots WHERE provider=?',(provider,)).fetchone()
        delay=max(0.0,(row[0] if row else now)-now)
        if delay >= timeout:
            raise TimeoutError('Espera do provedor excederia o orçamento da chamada.')
        db.execute('INSERT INTO slots VALUES (?,?) ON CONFLICT(provider) DO UPDATE SET next_at=excluded.next_at',
                   (provider,now+delay+interval))
    if delay:
        sleep(delay)
    return delay
