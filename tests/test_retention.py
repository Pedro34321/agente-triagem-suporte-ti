import os
import time
from src.graph import App
from test_graph import FakeLLM
from scripts.retencao import purge


def test_trace_retention_removes_checkpoint(tmp_path):
    app=App(tmp_path,FakeLLM());out=app.run('senha incorreta')
    for path in (tmp_path/'traces').glob('*.jsonl'):os.utime(path,(1,1))
    result=purge(app,30,now=time.time())
    assert result['traces_removidos']>=1
    assert not app.graph.get_state(app.config(out['thread_id'])).values
    app.close()
