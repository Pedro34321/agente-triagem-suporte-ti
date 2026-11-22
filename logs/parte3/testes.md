# Testes locais da Parte 3

Execução final em 22/11/2026. Comando: python -m pytest -q --tb=short

..........................                                               [100%]
26 passed in 3.92s

As rodadas com API real ficam em evals/resultados. Estes testes usam doubles onde indicado.

Inclui três testes da consolidação: limiar e leitura obrigatória dos desacordos;
rejeição de amostra incompleta/rótulos ausentes; rejeição de análise antiga quando
texto ou voto muda. A consolidação real dos vinte casos reutiliza as previsões já
coletadas, sem novas chamadas pagas.

