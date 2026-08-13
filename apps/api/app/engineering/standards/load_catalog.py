"""Catálogo inicial de cargas residenciais (seção 12 do prompt mestre).

Potências são valores típicos de mercado apresentados ao usuário como ESTIMATIVA — a
plataforma nunca assume silenciosamente a potência real de um equipamento específico do
usuário quando isso pode alterar o dimensionamento; ver `confidence` e `source`.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LoadCatalogEntry:
    code: str
    category: str
    name: str
    typical_power_w: float
    voltage_v: float
    demand_factor: float
    requires_dedicated_circuit: bool
    confidence: float  # 0..1 — confiança na potência típica listada
    source: str = "catalogo_interno_estimativa"


LOAD_CATALOG: list[LoadCatalogEntry] = [
    # Cozinha
    LoadCatalogEntry("geladeira", "cozinha", "Geladeira", 150, 127, 1.0, False, 0.6),
    LoadCatalogEntry("freezer", "cozinha", "Freezer", 200, 127, 1.0, False, 0.6),
    LoadCatalogEntry("microondas", "cozinha", "Micro-ondas", 1400, 127, 0.8, False, 0.7),
    LoadCatalogEntry("forno_eletrico", "cozinha", "Forno elétrico", 3000, 220, 0.8, True, 0.6),
    LoadCatalogEntry("cooktop", "cozinha", "Cooktop elétrico", 6000, 220, 0.7, True, 0.6),
    LoadCatalogEntry("lava_loucas", "cozinha", "Máquina de lavar louça", 2000, 220, 0.8, True, 0.6),
    LoadCatalogEntry("coifa", "cozinha", "Coifa", 200, 127, 1.0, False, 0.6),
    LoadCatalogEntry("air_fryer", "cozinha", "Air fryer", 1500, 127, 0.6, False, 0.6),
    LoadCatalogEntry("cafeteira", "cozinha", "Cafeteira", 800, 127, 0.4, False, 0.6),
    LoadCatalogEntry("liquidificador", "cozinha", "Liquidificador", 500, 127, 0.3, False, 0.6),
    # Banheiro
    LoadCatalogEntry("chuveiro", "banheiro", "Chuveiro elétrico", 5500, 220, 1.0, True, 0.7),
    LoadCatalogEntry("torneira_eletrica", "banheiro", "Torneira elétrica", 4400, 220, 1.0, True, 0.6),
    LoadCatalogEntry("secador_cabelo", "banheiro", "Secador de cabelo", 1800, 127, 0.3, False, 0.6),
    # Área de serviço
    LoadCatalogEntry("maquina_lavar", "area_servico", "Máquina de lavar roupa", 1500, 127, 0.6, True, 0.6),
    LoadCatalogEntry("secadora", "area_servico", "Secadora de roupa", 3000, 220, 0.6, True, 0.6),
    LoadCatalogEntry("ferro_passar", "area_servico", "Ferro de passar", 1200, 127, 0.4, False, 0.6),
    # Sala / Quartos
    LoadCatalogEntry("ar_condicionado_split_9k", "climatizacao", "Ar-condicionado split 9.000 BTU", 900, 220, 0.8, True, 0.6),
    LoadCatalogEntry("ar_condicionado_split_12k", "climatizacao", "Ar-condicionado split 12.000 BTU", 1200, 220, 0.8, True, 0.6),
    LoadCatalogEntry("tv", "eletronicos", "TV", 120, 127, 0.9, False, 0.6),
    LoadCatalogEntry("roteador", "eletronicos", "Roteador Wi-Fi", 15, 127, 1.0, False, 0.7),
    LoadCatalogEntry("videogame", "eletronicos", "Videogame", 200, 127, 0.5, False, 0.6),
    LoadCatalogEntry("computador", "eletronicos", "Computador", 300, 127, 0.6, False, 0.6),
    # Externa
    LoadCatalogEntry("bomba_agua", "externa", "Bomba d'água", 750, 220, 0.8, True, 0.6),
    LoadCatalogEntry("portao_eletrico", "externa", "Motor de portão", 500, 127, 0.3, False, 0.6),
    LoadCatalogEntry("carregador_veicular", "externa", "Carregador de veículo elétrico", 7400, 220, 1.0, True, 0.5),
]


def find_catalog_entry(code: str) -> LoadCatalogEntry | None:
    return next((e for e in LOAD_CATALOG if e.code == code), None)
