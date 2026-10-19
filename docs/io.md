# Entrada e saída — execuções reais

Gerado por `python -m scripts.demonstrar`; dados fictícios.

## caso_simples

Commit: `8a081b3c8efb40532df566d24685943208f256f8`. Data: 2026-10-19T23:53:37.875987+00:00. Log: `logs/parte2/caso_simples.json`.

Entrada exata: Não consigo entrar no meu e-mail corporativo. Quando coloco minha senha, aparece que ela está incorreta.

```json
{
  "resultado": "Falha individual de acesso ao e-mail corporativo devido à senha incorreta.",
  "fontes": [
    {
      "id": "KB-ACESSO",
      "trecho": "Falha individual de senha ou conta: Acesso / Conta, prioridade Média, Suporte N1. Não pedir a senha. Exceção: suspeita de comprometimento de conta deve ser encaminhada ao Suporte N2 com prioridade Alta; nunca redefinir credenciais automaticamente."
    }
  ],
  "suficiente": true,
  "categoria": "Acesso / Conta",
  "prioridade": "Média",
  "encaminhamento": "Suporte N1",
  "perguntas": [],
  "registrar": true,
  "motivo_termino": "registrado",
  "thread_id": "demo:1792454013396141800:caso_simples",
  "registro_id": 1,
  "ja_existia": false,
  "pendencia": null
}
```

O que ler: `motivo_termino`, `suficiente`, fontes e ausência/presença de `registro_id` explicitam o caminho tomado.

## caso_ambiguo

Commit: `8a081b3c8efb40532df566d24685943208f256f8`. Data: 2026-10-19T23:53:51.095444+00:00. Log: `logs/parte2/caso_ambiguo.json`.

Entrada exata: O sistema não está funcionando e preciso resolver isso urgente porque tenho coisa para entregar hoje.

```json
{
  "resultado": "Preciso de informações adicionais. Qual sistema ou aplicação está apresentando o problema?",
  "fontes": [],
  "suficiente": false,
  "categoria": null,
  "prioridade": null,
  "encaminhamento": null,
  "perguntas": [
    "Qual sistema ou aplicação está apresentando o problema?"
  ],
  "registrar": false,
  "motivo_termino": "ambiguo",
  "thread_id": "demo:1792454013396141800:caso_ambiguo",
  "registro_id": null,
  "ja_existia": false,
  "pendencia": null
}
```

O que ler: `motivo_termino`, `suficiente`, fontes e ausência/presença de `registro_id` explicitam o caminho tomado.

## caso_divergencia

Commit: `8a081b3c8efb40532df566d24685943208f256f8`. Data: 2026-10-19T23:53:42.484330+00:00. Log: `logs/parte2/caso_divergencia.json`.

Entrada exata: Estou no Andar 3 e minha internet caiu. Acho que meu notebook está com problema.

```json
{
  "resultado": "Falha de rede coletiva no Andar 3 (incidente:1) com 35 usuários afetados. Suspeita de notebook não prevalece sobre evidência de indisponibilidade de rede no local. Não há registro de equipamento associado ao relato.",
  "fontes": [
    {
      "id": "KB-REDE",
      "trecho": "Falha de rede em local com incidente ativo correspondente: Rede / Conectividade, prioridade Alta, Infraestrutura. Sem correspondência de local não associar o incidente. A hipótese de notebook quebrado não prevalece sobre evidência de falha coletiva; não declarar diagnóstico definitivo."
    },
    {
      "id": "incidente:1",
      "trecho": "id: 1; titulo: Indisponibilidade de rede no andar 3; categoria: Rede / Conectividade; localizacao: Andar 3; usuarios_afetados: 35"
    }
  ],
  "suficiente": true,
  "categoria": "Rede / Conectividade",
  "prioridade": "Alta",
  "encaminhamento": "Infraestrutura",
  "perguntas": [
    "Confirmação do patrimônio do notebook mencionado (se aplicável)"
  ],
  "registrar": true,
  "motivo_termino": "registrado",
  "thread_id": "demo:1792454013396141800:caso_divergencia",
  "registro_id": 2,
  "ja_existia": false,
  "pendencia": null
}
```

O que ler: `motivo_termino`, `suficiente`, fontes e ausência/presença de `registro_id` explicitam o caminho tomado.

## caso_fora_corpus

Commit: `8a081b3c8efb40532df566d24685943208f256f8`. Data: 2026-10-19T23:53:52.536268+00:00. Log: `logs/parte2/caso_fora_corpus.json`.

Entrada exata: Como restaurar um cluster Kubernetes com etcd corrompido?

```json
{
  "resultado": "O corpus de suporte não contém informação para responder a este pedido. Consulte o Suporte N1 para obter o procedimento autorizado.",
  "fontes": [],
  "suficiente": false,
  "categoria": null,
  "prioridade": null,
  "encaminhamento": null,
  "perguntas": [],
  "registrar": false,
  "motivo_termino": "base_insuficiente",
  "thread_id": "demo:1792454013396141800:caso_fora_corpus",
  "registro_id": null,
  "ja_existia": false,
  "pendencia": null
}
```

O que ler: `motivo_termino`, `suficiente`, fontes e ausência/presença de `registro_id` explicitam o caminho tomado.

## caso_fora_escopo

Commit: `8a081b3c8efb40532df566d24685943208f256f8`. Data: 2026-10-19T23:53:58.527613+00:00. Log: `logs/parte2/caso_fora_escopo.json`.

Entrada exata: Escreva uma receita de bolo.

```json
{
  "resultado": "Atendo triagem de suporte de TI. ",
  "fontes": [],
  "suficiente": false,
  "categoria": null,
  "prioridade": null,
  "encaminhamento": null,
  "perguntas": [],
  "registrar": false,
  "motivo_termino": "fora_escopo",
  "thread_id": "demo:1792454013396141800:caso_fora_escopo",
  "registro_id": null,
  "ja_existia": false,
  "pendencia": null
}
```

O que ler: `motivo_termino`, `suficiente`, fontes e ausência/presença de `registro_id` explicitam o caminho tomado.

## caso_humano

Commit: `4752f6ba1bc14a76fef0ad0bf04ea52191462f19`. Data: 2026-10-19T23:55:11.172656+00:00. Log: `logs/parte2/caso_humano.json`.

Entrada exata: Meu notebook patrimônio NB-10203 tem cheiro de queimado.

```json
{
  "resultado": "Notebook NB-10203 (Andar 3) apresenta cheiro de queimado, indicando risco físico imediato.",
  "fontes": [
    {
      "id": "KB-HARDWARE",
      "trecho": "Falha física de equipamento: Hardware / Equipamento, prioridade Média, Suporte N2. Se o patrimônio informado não existir, pedir confirmação e não registrar. Exceção: cheiro de queimado ou risco elétrico exige prioridade Crítica e avaliação humana; orientar a interromper o uso com segurança, sem instruir reparo."
    },
    {
      "id": "equipamento:NB-10203",
      "trecho": "patrimonio: NB-10203; tipo: Notebook; status: Ativo; localizacao: Andar 3"
    }
  ],
  "suficiente": true,
  "categoria": "Hardware / Equipamento",
  "prioridade": "Crítica",
  "encaminhamento": "Infraestrutura",
  "perguntas": [],
  "registrar": true,
  "motivo_termino": "registrado",
  "thread_id": "demo:1792454107100680200:caso_humano",
  "registro_id": 1,
  "ja_existia": false,
  "pendencia": null
}
```

O que ler: `motivo_termino`, `suficiente`, fontes e ausência/presença de `registro_id` explicitam o caminho tomado.

## caso_incompleto

Commit: `8a081b3c8efb40532df566d24685943208f256f8`. Data: 2026-10-19T23:53:57.183267+00:00. Log: `logs/parte2/caso_incompleto.json`.

Entrada exata: Preciso de ajuda.

```json
{
  "resultado": "Preciso de informações adicionais. Qual problema de TI você está enfrentando?",
  "fontes": [],
  "suficiente": false,
  "categoria": null,
  "prioridade": null,
  "encaminhamento": null,
  "perguntas": [
    "Qual problema de TI você está enfrentando?"
  ],
  "registrar": false,
  "motivo_termino": "incompleto",
  "thread_id": "demo:1792454013396141800:caso_incompleto",
  "registro_id": null,
  "ja_existia": false,
  "pendencia": null
}
```

O que ler: `motivo_termino`, `suficiente`, fontes e ausência/presença de `registro_id` explicitam o caminho tomado.

## caso_nao_dispara

Commit: `8a081b3c8efb40532df566d24685943208f256f8`. Data: 2026-10-19T23:53:49.669276+00:00. Log: `logs/parte2/caso_nao_dispara.json`.

Entrada exata: Vou trabalhar de casa amanhã. Como faço para configurar a VPN no notebook corporativo?

```json
{
  "resultado": "Configuração de VPN em notebook corporativo é procedimento informativo. Não há incidente a registrar.",
  "fontes": [
    {
      "id": "KB-VPN",
      "trecho": "Para configurar VPN no notebook corporativo, solicitar ao Suporte N1 o cliente homologado e o perfil autorizado; autenticar pelo fluxo corporativo com MFA. Não compartilhar senha. Exceção: em equipamento pessoal, não instalar o cliente corporativo sem autorização. Orientação de VPN é Solicitação Informativa, Baixa, Suporte N1 e não gera incidente."
    }
  ],
  "suficiente": true,
  "categoria": "Solicitação Informativa",
  "prioridade": "Baixa",
  "encaminhamento": "Suporte N1",
  "perguntas": [],
  "registrar": false,
  "motivo_termino": "informativo",
  "thread_id": "demo:1792454013396141800:caso_nao_dispara",
  "registro_id": null,
  "ja_existia": false,
  "pendencia": null
}
```

O que ler: `motivo_termino`, `suficiente`, fontes e ausência/presença de `registro_id` explicitam o caminho tomado.

## caso_registro_inexistente

Commit: `8a081b3c8efb40532df566d24685943208f256f8`. Data: 2026-10-19T23:53:46.440199+00:00. Log: `logs/parte2/caso_registro_inexistente.json`.

Entrada exata: Meu notebook patrimônio NB-98451 parou de carregar.

```json
{
  "resultado": "Notebook patrimônio **NB-98451** não está cadastrado no patrimônio ativo (registro_nao_encontrado). Falha física de carregamento não pode ser registrada sem confirmação do patrimônio.",
  "fontes": [
    {
      "id": "KB-HARDWARE",
      "trecho": "Falha física de equipamento: Hardware / Equipamento, prioridade Média, Suporte N2. Se o patrimônio informado não existir, pedir confirmação e não registrar. Exceção: cheiro de queimado ou risco elétrico exige prioridade Crítica e avaliação humana; orientar a interromper o uso com segurança, sem instruir reparo."
    }
  ],
  "suficiente": false,
  "categoria": null,
  "prioridade": null,
  "encaminhamento": null,
  "perguntas": [
    "Confirme se o equipamento **NB-98451** está cadastrado no patrimônio. Caso não esteja, forneça o patrimônio correto ou detalhes do notebook para verificação."
  ],
  "registrar": false,
  "motivo_termino": "base_insuficiente",
  "thread_id": "demo:1792454013396141800:caso_registro_inexistente",
  "registro_id": null,
  "ja_existia": false,
  "pendencia": null
}
```

O que ler: `motivo_termino`, `suficiente`, fontes e ausência/presença de `registro_id` explicitam o caminho tomado.
