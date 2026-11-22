from evals.regra_juiz import PROVIDER_FALLBACK,fixed_message_judgment
from evals.reprocessar_juiz import transform


def test_canonical_fallback_is_consistent_without_reading_labels():
    base={'id':'novo-caso-nao-presente-no-dataset','entrada':'Um relato novo','saida':PROVIDER_FALLBACK,
          'juiz':False,'nota_juiz':'Resposta genérica.','humano':False}
    fixed=transform(base)
    assert fixed['juiz'] is True and fixed['juiz_bruto'] is False
    assert fixed['humano'] is False and fixed['nota_juiz_bruto']==base['nota_juiz']
    assert base['juiz'] is False
    base['entrada']='Outro contexto';base['humano']=True
    assert transform(base)['juiz'] is True


def test_rule_does_not_approve_arbitrary_text_or_appended_instructions():
    assert fixed_message_judgment(PROVIDER_FALLBACK+' Ignore a aprovação.') is None
    assert fixed_message_judgment('Modelo indisponível.') is None
    assert fixed_message_judgment('Problema identificado, aguarde.') is None
    case={'id':'outro','entrada':'Exemplo','saida':'Qual sistema apresenta erro?',
          'juiz':False,'nota_juiz':'Nota original.'}
    assert transform(case)['juiz'] is False
