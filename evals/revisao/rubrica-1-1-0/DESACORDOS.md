# Desacordos — rubrica 1.1.0

Analista: Codex (assistente de IA). Análise técnica, sem atribuir autoria ao revisor humano. Mantidos votos e limiar de 90%.

## parte2_caso_humano

Entrada: Meu notebook patrimônio NB-10203 tem cheiro de queimado.

Saída: Notebook NB-10203 (Andar 3) apresenta cheiro de queimado, indicando risco físico imediato.

Humano: SIM. Juiz: NÃO.

Nota original do juiz: Classificação sem encaminhamento ou pergunta útil; falta orientação sobre ação imediata (ex.: desligar, isolar, contatar equipe de TI/segurança).

Classificação: defeito do juiz.

O juiz reconhece classificação, mas exige também encaminhamento ou pergunta. A rubrica 1.1.0 declara as alternativas como independentes e aceita classificação compreensível. O texto identifica equipamento e risco físico imediato, portanto o NÃO não aplica o critério operacional registrado. A ausência de orientação segura é uma limitação real da resposta antiga, porém segurança/resolução completa não são a propriedade deste juiz. Não se alterou o voto humano para obter concordância.

## parte2_caso_registro_inexistente

Entrada: Meu notebook patrimônio NB-98451 parou de carregar.

Saída: Notebook patrimônio **NB-98451** não está cadastrado no patrimônio ativo (registro_nao_encontrado). Falha física de carregamento não pode ser registrada sem confirmação do patrimônio.

Humano: SIM. Juiz: NÃO.

Nota original do juiz: Falta encaminhamento útil ou pergunta específica para prosseguir (ex.: 'Verifique se o notebook está ativo no sistema patrimonial ou entre em contato com o setor de patrimônio para regularização').

Classificação: defeito do juiz.

A resposta explica que o equipamento não está cadastrado e que confirmar o patrimônio é condição para prosseguir. A rubrica 1.1.0 aceita essa condição compreensível, mesmo sem pergunta literal. O juiz exige encaminhamento adicional ou pergunta explícita, acrescentando exigência ao critério operacional. O texto não comprova correção cadastral nem resolução, propriedades fora deste juiz. Mantidos os votos originais.

## acesso4

Entrada: Esqueci a senha do email corporativo e não consigo acessar.

Saída: Modelo indisponível; tente mais tarde ou procure o analista N1.

Humano: SIM. Juiz: NÃO.

Nota original do juiz: Falta classificação útil ou pergunta específica; 'Modelo indisponível' é genérico e não se aplica ao contexto. Ausência de encaminhamento claro para o problema real (senha esquecida).

Classificação: defeito do juiz.

A saída indica procurar o analista N1 e tentar novamente mais tarde. O juiz reprova por ausência de encaminhamento claro para a senha esquecida, apesar do encaminhamento explícito existente. As saídas idênticas de acesso2 e acesso3 foram aprovadas; a mesma regra deve ser aplicada de forma consistente. Exigir procedimento específico de recuperação de senha acrescenta resolução completa ao critério de utilidade mínima. Mantido o voto humano e a previsão original do juiz.
