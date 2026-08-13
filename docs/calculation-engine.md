# Motor de Cálculo — EletroIA

Local: `apps/api/app/engineering/calculations/`.

## Princípio

Toda função é pura (mesma entrada → mesma saída) e devolve um `CalculationResult` com
`calc_type`, `formula`, `inputs`, `result`, `unit`, `source`, `timestamp` e
`needs_professional_review` — a estrutura de auditoria pedida na seção 16 do prompt
mestre. `app/engineering/orchestrator.py` persiste cada `CalculationResult` gerado como
uma linha da tabela `calculations`.

## Funções implementadas (`electrical.py`)

- `apparent_power_va` — S = P / cos(phi)
- `current_single_phase_a` — I = P / (V · cos(phi))
- `current_three_phase_a` — I = P / (√3 · V · cos(phi))
- `demand_power_w` — soma ponderada por fator de demanda, carga a carga (nunca um fator
  único "de cabeça" para a casa inteira)
- `voltage_drop_pct` — estimativa por resistência do condutor; sinaliza
  `needs_professional_review=True` para circuitos com mais de 30 m (reatância não
  considerada nesta estimativa simplificada)

## Dimensionamento (`sizing.py` + `standards/ampacity_table.py`)

- `select_conductor` — escolhe a menor seção padrão cuja ampacidade tabelada cobre a
  corrente de projeto, respeitando a seção mínima por tipo de circuito (1,5 mm²
  iluminação / 2,5 mm² tomadas).
- `select_breaker` — escolhe o menor disjuntor padrão que coordena
  `I_projeto ≤ I_disjuntor ≤ I_condutor`.

**Importante:** a tabela de ampacidade em `standards/ampacity_table.py` é um placeholder
interno de engenharia para o MVP — não uma transcrição da Tabela 36 oficial da NBR 5410.
Por isso toda seleção de condutor/disjuntor sai marcada com
`needs_professional_review=True`. Antes de qualquer uso em projeto real, essa tabela deve
ser substituída/validada por um profissional habilitado com acesso à norma vigente.

## Testes

`apps/api/tests/unit/test_calculations.py` cobre valores conhecidos (ex.: chuveiro
5500 W/220 V → 25 A), casos de erro (fator de potência inválido, tamanhos incompatíveis) e
os limites de seção mínima e coordenação disjuntor-condutor.
