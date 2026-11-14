# Roteiro curto para apresentar a Parte 2

1. **Problema:** o usuário descreve a falha em linguagem natural; o sistema classifica,
   consulta política/cadastro e propõe encaminhamento. Não faz diagnóstico definitivo.
2. **Contrato:** abra `docs/io.md`. Mostre um JSON com resultado, fontes e suficiente,
   depois a recusa fora do corpus e a pergunta para relato ambíguo.
3. **Grafo:** rode `python conferir_grafo.py` e compare com o ASCII da arquitetura.
   Modelo interpreta e propõe; código valida, controla orçamento e faz a escrita.
4. **RAG:** abra `dados/perguntas_rag.json` e `logs/parte2/avaliacao-local.json`.
   Explique texto para política e SQL para registro. Mostre documento revogado excluído.
5. **Humano:** abra `logs/parte2/caso_humano.json`. Mostre proposta pausada, equipe antes
   e depois da edição, segunda aprovação com ja_existia e contagem de registros igual a um.
6. **Memória:** explique checkpoint para retomar, episódios por similaridade, fatos por
   chave/tempo e procedural no prompt. Mostre os testes de remoção e contradição.
7. **Decisões medidas:** 3B teve falhas de interpretação/citação; 8B + seleção de ids
   passou nos nove casos. A ablação teve 5/5 nos dois tratamentos; não prova redundância
   da frase porque o conjunto é pequeno.

Para demonstrar ao vivo, use novo `--caso` e somente texto fictício:

```powershell
python -m src.main iniciar "Meu notebook patrimônio NB-10203 tem cheiro de queimado." --caso apresentacao1
python -m src.main retomar demo:principal:apresentacao1 editar --equipe Infraestrutura
python -m src.main retomar demo:principal:apresentacao1 aprovar
```


