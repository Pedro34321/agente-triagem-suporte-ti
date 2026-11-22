# Coleta experimental interrompida

O teste do juiz mistral-small-2603 foi interrompido após erros HTTP 429, sem rótulos
válidos do modelo. O diagnóstico separado retornou code=1300, type=rate_limited,
message="Rate limit exceeded". Isso não demonstra saldo esgotado nem ausência de
permissão; o motivo confirmado é o limite informado pelo provedor.

As tentativas e seus erros estão preservados em predicoes-parciais.json. Não há
concordância legítima ou adoção desta coleta incompleta. O modelo do agente não
foi alterado. A solução ativa é o juiz híbrido local documentado em
evals/revisao/juiz-hibrido-1-2-0/PROTOCOLO.md, com resultado bruto separado.
