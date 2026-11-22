from types import SimpleNamespace
from src import model
from evals.juiz import Judgment


def test_separate_judge_model_does_not_replace_agent_model(monkeypatch):
    monkeypatch.setenv('LLM_MIN_INTERVAL_SECONDS','0')
    monkeypatch.setattr(model,'PROVIDER','mistral')
    calls=[]
    def create(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='{"aprovado":true,"nota":"Encaminhamento claro."}'))],
                               usage=SimpleNamespace(prompt_tokens=10,completion_tokens=8,total_tokens=18))
    judge=model.LLM(model='modelo-juiz-teste')
    judge.client=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    result,_=judge.call('juiz',Judgment,{'entrada':'Exemplo','saida':'Procure o suporte.'})
    assert result['aprovado'] and calls[0]['model']=='modelo-juiz-teste'
    assert model.LLM().model==model.MODEL
    assert 'Procedimento aprovado' not in calls[0]['messages'][0]['content']
