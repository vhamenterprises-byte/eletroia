# AI Safety — EletroIA

Princípio máximo (seção 61 do prompt mestre): **segurança > experiência > velocidade**.
Este documento descreve como isso é aplicado em código, não apenas em intenção.

## 1. A IA nunca calcula, nunca decide conformidade

- Todo número técnico exibido ao usuário vem de `app/engineering/calculations` (funções
  puras, testadas em `apps/api/tests/unit/test_calculations.py`).
- Todo veredito de conformidade vem de `app/engineering/rules` (`RulesEngine`, testado em
  `test_rules_engine.py`) e usa apenas os níveis VERDE/AMARELO/VERMELHO/AZUL — nunca
  "aprovado pela ABNT" (ver `STATUS_LABELS` em `app/documents/pdf_report.py` e o texto
  fixo em `GET /projects/{id}/compliance-summary`).
- O prompt de sistema da IA (`app/ai/safety.py::SYSTEM_PROMPT_GUARDRAILS`) proíbe
  explicitamente inventar números ou declarar aprovação genérica.

## 2. Defesa em profundidade contra jailbreak (seção 48 — Red Team)

`app/ai/safety.py::check_user_message()` intercepta padrões conhecidos de tentativa de
contornar segurança ("ignore a norma", "não precisa calcular", "coloque a assinatura do
engenheiro" etc.) **antes** de qualquer chamada ao modelo de linguagem — a recusa não
depende do LLM "decidir" recusar. Testado em `test_red_team.py` com os exemplos literais
da seção 48 do prompt mestre.

Isso é uma primeira camada, não a única: o prompt de sistema também instrui o modelo a
recusar esses pedidos, para os casos que o filtro de padrões não cobre.

## 3. Rastreabilidade

`app/ai/explain.py::build_explanation()` monta, para qualquer resposta técnica do chat, a
lista de `rule_codes` e `calculation_types` que a sustentam — devolvidos junto da resposta
em `ChatResponse` (`rule_codes_cited`, `calculation_types_cited`), permitindo ao frontend
(ou a uma auditoria futura) verificar que nenhuma afirmação técnica veio "do nada".

## 4. Provider-agnostic

`app/ai/provider.py::AIProvider` é uma interface abstrata; `claude_provider.py` implementa
Claude, `mock_provider.py` um stub determinístico usado em testes e quando não há
`ANTHROPIC_API_KEY` configurada. Trocar de fornecedor não deve exigir mudanças fora de
`app/ai/`.

## Pendências conhecidas (não implementadas nesta entrega)

- Guarda estrutural que valide se cada número citado pelo modelo realmente aparece nos
  fatos fornecidos (hoje a garantia é apenas via prompt de sistema + fatos injetados).
  Recomendado antes de produção.
- Fluxo formal de encaminhamento para revisão profissional (seção 30/31).
