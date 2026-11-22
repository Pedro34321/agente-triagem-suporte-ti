import copy
import pytest
from evals.calibrar_juiz import case_hash, consolidate


def evidence():
    packet=[{'id':str(i),'entrada':'Entrada '+str(i),'saida':'Saída '+str(i),
             'humano':True,'nota_humana':'Encaminhamento explícito.','revisor_humano':'Revisor de teste'} for i in range(20)]
    predictions=[dict(c,juiz=i>=2,nota_juiz='Nota de teste.') for i,c in enumerate(packet)]
    reviews=[{'id':c['id'],'caso_sha256':case_hash(c),'humano':True,'juiz':False,
              'classificacao':'defeito do juiz','analise':'Ignorou o encaminhamento.',
              'analista':'Analista de teste'} for c in packet[:2]]
    return packet,predictions,reviews


def test_adoption_requires_threshold_and_analysis():
    packet,predictions,reviews=evidence()
    assert not consolidate(packet,predictions)['adotado']
    final=consolidate(packet,predictions,reviews)
    assert final['adotado'] and final['concordancia']==0.9
    assert final['matriz']['humano_sim_juiz_nao']==2
    assert consolidate(packet,predictions,reviews)==final
    predictions[2]['juiz']=False
    assert not consolidate(packet,predictions,reviews)['adotado']


def test_partial_or_missing_human_evidence_cannot_validate():
    packet,predictions,reviews=evidence()
    with pytest.raises(ValueError):consolidate(packet[:19],predictions)
    with pytest.raises(ValueError):consolidate(packet,predictions[:19])
    packet[0]['humano']=None
    result=consolidate(packet,predictions)
    assert result['matriz'] is None and not result['adotado']


def test_analysis_is_bound_to_votes_and_original_text():
    packet,predictions,reviews=evidence()
    stale=copy.deepcopy(reviews);stale[0]['humano']=False
    with pytest.raises(ValueError):consolidate(packet,predictions,stale)
    packet[0]['saida']='Outra resposta'
    with pytest.raises(ValueError):consolidate(packet,predictions,reviews)
