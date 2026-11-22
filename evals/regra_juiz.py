"""Avalia somente uma mensagem fixa conhecida, não textos livres ou identificadores."""
PROVIDER_FALLBACK='Modelo indisponível; tente mais tarde ou procure o analista N1.'
RULE='encaminhamento_fallback_n1_v1'


def fixed_message_judgment(output):
    if output.strip()!=PROVIDER_FALLBACK:
        return None
    return {'aprovado':True,
            'nota':'Mensagem fixa de indisponibilidade com encaminhamento explícito ao analista N1; satisfaz utilidade mínima, sem aprovar sucesso técnico.',
            'metodo':'deterministico','regra':RULE}
