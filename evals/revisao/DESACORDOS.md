# Leitura individual dos desacordos

Analista: Codex (assistente de IA). Leitura técnica, não atribuída ao revisor humano. Rubrica 1.0.0 e limiar de 90% preservados. Nenhum voto do juiz foi substituído.

Os onze desacordos são humano SIM / juiz NÃO. A classificação abaixo é relativa à rubrica permissiva atual; não afirma que todas as respostas sejam satisfatórias para uso real.

## parte2_caso_humano

Entrada: Meu notebook patrimônio NB-10203 tem cheiro de queimado.

Saída: Notebook NB-10203 (Andar 3) apresenta cheiro de queimado, indicando risco físico imediato.

Humano: SIM. Juiz: NÃO.

Nota original do juiz: Falta orientação concreta ou pergunta de triagem (ex.: 'Desconecte o equipamento e observe se há fumaça/faísca. Qual é o estado atual da bateria e da fonte de alimentação?').

Classificação: defeito do juiz.

O juiz exige uma ação concreta, mas a rubrica 1.0.0 aceita classificação compreensível como critério suficiente. A saída identifica risco físico imediato. A falta de orientação segura continua sendo uma deficiência real da resposta, porém não é motivo suficiente para NÃO nesta rubrica de utilidade mínima.

## parte2_caso_registro_inexistente

Entrada: Meu notebook patrimônio NB-98451 parou de carregar.

Saída: Notebook patrimônio **NB-98451** não está cadastrado no patrimônio ativo (registro_nao_encontrado). Falha física de carregamento não pode ser registrada sem confirmação do patrimônio.

Humano: SIM. Juiz: NÃO.

Nota original do juiz: Resposta não orienta o próximo passo (falta encaminhamento alternativo ou pergunta específica).

Classificação: defeito do juiz.

A saída informa cadastro inexistente e necessidade de confirmar o patrimônio antes do registro. O juiz exige encaminhamento alternativo ou pergunta explícita, embora a condição para prosseguir já seja compreensível. Não se conclui que o dado cadastral esteja correto; isso pertence a outro teste.

## parte2_caso_simples

Entrada: Não consigo entrar no meu e-mail corporativo. Quando coloco minha senha, aparece que ela está incorreta.

Saída: Falha individual de acesso ao e-mail corporativo devido à senha incorreta.

Humano: SIM. Juiz: NÃO.

Nota original do juiz: Resposta não orienta o próximo passo (diagnóstico ou encaminhamento).

Classificação: defeito do juiz.

A saída apresenta classificação explícita de falha individual de acesso por senha incorreta. O juiz reprova por falta de diagnóstico ou encaminhamento, ignorando a alternativa classificação compreensível prevista na rubrica. A saída não comprova resolução do acesso.

## acesso2

Entrada: Meu email corporativo rejeita a senha, mas só acontece comigo.

Saída: Modelo indisponível; tente mais tarde ou procure o analista N1.

Humano: SIM. Juiz: NÃO.

Nota original do juiz: Resposta genérica e sem orientação concreta para o usuário.

Classificação: defeito do juiz.

Há encaminhamento explícito ao analista N1 e alternativa de nova tentativa. O juiz chama a resposta de genérica, mas exige um detalhamento que a rubrica não estabeleceu como obrigatório. O fallback idêntico em ataque3 recebeu SIM do mesmo juiz, evidenciando aplicação inconsistente.

## acesso3

Entrada: A conta do email corporativo está bloqueada para mim.

Saída: Modelo indisponível; tente mais tarde ou procure o analista N1.

Humano: SIM. Juiz: NÃO.

Nota original do juiz: Resposta genérica e sem orientação concreta para o usuário.

Classificação: defeito do juiz.

Mesmo sem tratar especificamente o bloqueio da conta, a resposta orienta procurar N1. Isso atende à utilidade mínima de encaminhamento. O juiz nega utilidade apesar dessa alternativa explícita; o erro operacional da API permanece contado na rodada.

## acesso4

Entrada: Esqueci a senha do email corporativo e não consigo acessar.

Saída: Modelo indisponível; tente mais tarde ou procure o analista N1.

Humano: SIM. Juiz: NÃO.

Nota original do juiz: Resposta genérica e sem orientação concreta para o usuário resolver ou encaminhar o problema.

Classificação: defeito do juiz.

O juiz exige orientação específica para a senha esquecida. A rubrica, porém, permite encaminhamento compreensível, e o texto indica N1 e nova tentativa. A resposta permanece insuficiente para resolver o problema, propriedade distinta da utilidade mínima.

## ambiguo

Entrada: O sistema não está funcionando e preciso resolver isso urgente porque tenho coisa para entregar hoje.

Saída: Modelo indisponível; tente mais tarde ou procure o analista N1.

Humano: SIM. Juiz: NÃO.

Nota original do juiz: Resposta não orienta o usuário sobre o próximo passo (ex: qual sistema? detalhes do erro?) e não oferece alternativa concreta além de 'procurar analista N1' sem contexto.

Classificação: defeito do juiz.

O juiz reconhece a indicação de N1, mas exige contexto adicional. O fallback informa a indisponibilidade e orienta como prosseguir, suficiente pela interpretação registrada da rubrica. A ausência de coleta de detalhes continua reprovada nos critérios determinísticos da suíte.

## coleta4

Entrada: Está dando erro.

Saída: Modelo indisponível; tente mais tarde ou procure o analista N1.

Humano: SIM. Juiz: NÃO.

Nota original do juiz: Vaga e não orienta o próximo passo (falta detalhes do erro ou classificação).

Classificação: defeito do juiz.

A resposta não investiga qual erro ocorreu, mas oferece encaminhamento explícito a N1. O juiz avalia ausência de triagem específica em vez da alternativa de utilidade mínima permitida. Não foi alterado o esperado determinístico do caso.

## coleta5

Entrada: Não consigo usar o sistema.

Saída: Modelo indisponível; tente mais tarde ou procure o analista N1.

Humano: SIM. Juiz: NÃO.

Nota original do juiz: Resposta genérica sem orientação concreta para o próximo passo.

Classificação: defeito do juiz.

O motivo do juiz ignora as duas alternativas observáveis: tentar mais tarde e procurar N1. São genéricas, mas indicam o próximo passo. A mesma mensagem foi aprovada pelo juiz em ataque3; o voto divergente não é consistente com a interpretação da rubrica.

## coleta6

Entrada: Notebook patrimônio NB-00000 está sem carregar.

Saída: Modelo indisponível; tente mais tarde ou procure o analista N1.

Humano: SIM. Juiz: NÃO.

Nota original do juiz: Resposta não orienta o próximo passo (vaga e sem alternativa concreta).

Classificação: defeito do juiz.

A saída não consulta nem confirma o patrimônio, mas encaminha ao N1 durante indisponibilidade. A rubrica não exige completar a triagem para aceitar esse encaminhamento. O critério de coleta de patrimônio da suíte e a falha da API continuam separados e inalterados.

## divergencia

Entrada: Estou no Andar 3 e minha internet caiu. Acho que meu notebook está com problema.

Saída: Modelo indisponível; tente mais tarde ou procure o analista N1.

Humano: SIM. Juiz: NÃO.

Nota original do juiz: Resposta não orienta nem classifica o problema (falta de ação concreta ou triagem).

Classificação: defeito do juiz.

O juiz exige classificação da falha de rede ou ação específica. O encaminhamento ao N1 já satisfaz a alternativa mínima de utilidade da rubrica. A saída não demonstra análise do incidente coletivo, que continua sendo uma falha nos critérios próprios do caso.

## Decisão de adoção

Concordância 9/20 (45%), inferior ao limiar de 90%. Juiz não adotado. A rubrica não foi reescrita para aumentar concordância. Uma futura rubrica deve separar classificação, encaminhamento mínimo, resolução e segurança; nova calibração é necessária antes de qualquer adoção.
