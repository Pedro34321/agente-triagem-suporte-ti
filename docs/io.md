# Contrato e exemplos — estado de execução

Entrada: texto livre, 1–2000 caracteres. Usuário, sessão e caso são metadados da CLI;
não são extraídos de formulário de triagem. O texto é interpretado pelo modelo.

Saída: `src/contracts.py::Output`, exportada em `schema-saida.json` por
`python -m scripts.avaliar_local`. Sempre inclui resultado, fontes, suficiente,
categoria, prioridade, encaminhamento, perguntas, registrar, motivo_termino,
thread_id, registro_id, ja_existia e pendencia (inclusive null/vazios).

Exemplos da Parte 2 devem ser **gerados**, não escritos à mão:

```powershell
python -m scripts.demonstrar
```

O comando executa os cinco casos existentes e acrescenta fora do corpus, humano,
incompleto e fora do escopo. Salva entrada exata, saída completa, commit, data,
modelo, hashes de prompts, eventos, aprovação e duplicata. Atualiza esta página
com os nove exemplos e repete o principal no README.

No desenvolvimento, a API retornou `429 credit_balance_exhausted / insufficient_quota`.
Assim, os logs reais de sucesso e os exemplos gerados estão **pendentes de créditos**.
Logs da Parte 1 não foram rebatizados como evidência da Parte 2. Testes locais usam
double explícito e não demonstram a qualidade das respostas do modelo real.
