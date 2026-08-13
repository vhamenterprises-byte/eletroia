# Motor de Regras — EletroIA

Local: `apps/api/app/engineering/rules/`.

## Estrutura

`engine.py` define `ElectricalRule` (metadados + `applies_when` + `evaluate_fn`) e
`RulesEngine` (`evaluate_all`, `evaluate_one`). Regras nunca vivem em prompts de LLM —
são funções Python testáveis. Cada `RuleEvaluation` devolve `status` em
VERDE/AMARELO/VERMELHO/AZUL (nunca "aprovado").

## Regras implementadas nesta entrega (`nbr5410.py`)

| rule_code | Categoria | O que verifica |
|---|---|---|
| `RULE-LIGHTING-MIN-CIRCUIT` | iluminação | Todo ambiente tem ao menos um ponto de luz |
| `RULE-TUG-MIN-COUNT` | tomadas | Nº mínimo de tomadas de uso geral por perímetro |
| `RULE-DEDICATED-CIRCUIT-HIGH-POWER` | circuitos | Cargas ≥1500 W exigem circuito dedicado |
| `RULE-WET-AREA-SOCKET-CLEARANCE` | segurança | Distância mínima de tomada a fonte de água em área molhada |
| `RULE-MIN-CONDUCTOR-SECTION` | dimensionamento | Seção mínima do condutor por tipo de circuito |
| `RULE-DR-PROTECTION-REQUIRED` | proteção | Quadro possui dispositivo DR |
| `RULE-GROUNDING-REVIEW` | aterramento | Sempre AZUL — aterramento não é validável remotamente |

**Importante:** os limiares numéricos são uma interpretação interna simplificada para o
MVP (`version: "MVP-interno-v1"`), não uma transcrição do texto da NBR 5410. Antes de uso
em projeto real, um profissional habilitado deve revisar/ajustar cada regra e vincular a
`NormativeReference` correspondente (apontamento estruturado — seção, título, resumo
interno — nunca o texto protegido da norma).

## Exemplo de bloqueio de configuração insegura

`RULE-WET-AREA-SOCKET-CLEARANCE` implementa o caso da seção 14 do prompt mestre: um
pedido de tomada dentro do box do chuveiro (`distance_from_water_source_m < 0.60`) recebe
VERMELHO, e a API (`POST /projects/{id}/socket-placement-check`) devolve a mensagem
explicando o motivo — nunca aceita silenciosamente. Testado em
`test_rules_engine.py::test_socket_inside_shower_box_is_rejected`.

## Testes

`apps/api/tests/unit/test_rules_engine.py` cobre os casos VERDE/AMARELO/VERMELHO/AZUL de
cada regra, incluindo o caso de segurança acima.
