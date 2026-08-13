# Fontes Normativas — EletroIA

## Princípio

A plataforma nunca copia o texto protegido de uma norma. `NormativeReference` (modelo em
`apps/api/app/models/engineering.py`) armazena apenas um apontamento estruturado:
`standard`, `version`, `section`, `title`, `internal_summary` (resumo interno, não a
transcrição), `source`.

## Status nesta entrega

A tabela `normative_references` foi criada no schema (migração `0001_initial.py`), mas
ainda **não está populada** com registros reais apontando para seções específicas da
NBR 5410 — isso requer acesso legítimo ao texto vigente da norma e revisão de um
profissional habilitado, fora do escopo desta entrega de código.

As regras em `engineering/rules/nbr5410.py` estão marcadas com `version: "MVP-interno-v1"`
justamente para deixar claro que são uma interpretação interna provisória, não uma
citação oficial — ver `docs/engineering-rules.md`.

## Referências consideradas (não incorporadas como texto) no prompt mestre original

- ABNT NBR 5410 (instalações elétricas de baixa tensão) — referência principal
- NR-10
- Regulamentações da ANEEL e requisitos de concessionária
- Normas complementares (proteção contra surtos, aterramento, DR)

## Próximo passo recomendado

Antes de uso em projetos reais: contratar/consultar um profissional habilitado (ou
licenciar acesso oficial à norma) para popular `normative_references` e revisar cada
`ElectricalRule` contra o texto vigente.
