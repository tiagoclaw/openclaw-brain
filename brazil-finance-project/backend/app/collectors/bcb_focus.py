"""
Collector: BCB Focus (Expectativas de Mercado)
Fonte: https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/
Documentação: https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/aplicacao#!/recursos

Este é um dos datasets MAIS valiosos - as expectativas Focus são usadas por todo economista.
"""

import httpx
import logging
from datetime import datetime
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

# URL base da API Focus BCB
FOCUS_BASE_URL = "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"

# Endpoints disponíveis no Focus
FOCUS_ENDPOINTS = {
    "anual": "ExpectativasMercadoAnuais",
    "mensal": "ExpectativasMercadoMensais", 
    "trimestral": "ExpectativasMercadoTrimestrais",
    "top5_anual": "ExpectativasMercadoTop5Anuais",
    "top5_mensal": "ExpectativasMercadoTop5Mensais",
    "instituicoes": "ExpectativasMercadoInstituicoes",
}

# Indicadores do Focus (nomes exatos da API)
FOCUS_INDICATORS = [
    "IPCA", "IGP-M", "IGP-DI", "INPC",
    "Taxa de câmbio", "Selic", 
    "PIB Total", "PIB Agropecuária", "PIB Indústria", "PIB Serviços",
    "Produção industrial", "Conta corrente", "Balança comercial",
    "Dívida líquida do setor público", "Resultado primário",
    "Investimento direto no país"
]

async def get_focus_expectations(
    indicator: str,
    year: int = None,
    metric: str = "mediana",
    top5: bool = False
) -> Dict:
    """
    Busca expectativas Focus para um indicador específico.
    
    Args:
        indicator: Nome do indicador (ex: "IPCA", "Selic", "PIB Total")
        year: Ano de referência (ex: 2025, 2026). Se None, pega ano atual+1
        metric: Métrica desejada ("mediana", "media", "minimo", "maximo", "desviopadrao")
        top5: Se True, busca expectativas Top 5 (melhores previsores históricos)
    
    Returns:
        dict com valor da expectativa e metadados
    """
    try:
        # Validar indicador
        if indicator not in FOCUS_INDICATORS:
            similar = [ind for ind in FOCUS_INDICATORS if indicator.lower() in ind.lower()]
            return {
                "erro": f"Indicador '{indicator}' não encontrado.",
                "sugestoes": similar[:3] if similar else FOCUS_INDICATORS[:5],
                "disponíveis": len(FOCUS_INDICATORS)
            }
        
        # Definir ano padrão (próximo ano) se não especificado
        if year is None:
            year = datetime.now().year + 1
            
        # Escolher endpoint
        endpoint = "ExpectativasMercadoTop5Anuais" if top5 else "ExpectativasMercadoAnuais"
        url = f"{FOCUS_BASE_URL}{endpoint}"
        
        # Construir filtro OData
        filters = [
            f"Indicador eq '{indicator}'",
            f"DataReferencia eq '{year}'"
        ]
        
        # Parâmetros da query OData
        params = {
            "$filter": " and ".join(filters),
            "$orderby": "Data desc",  # Mais recente primeiro
            "$top": 1,  # Apenas a expectativa mais recente
            "$format": "json",
            "$select": "Indicador,Data,DataReferencia,Mediana,Media,Minimo,Maximo,DesvioPadrao,baseCalculo,numeroRespondentes"
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        
        items = data.get("value", [])
        if not items:
            return {
                "erro": f"Sem expectativas para {indicator} {year}",
                "indicador": indicator,
                "ano": year,
                "disponível": f"Tente outro ano ou indicador"
            }
        
        item = items[0]
        
        # Mapear métrica para campo da resposta
        metric_map = {
            "mediana": "Mediana",
            "media": "Media",
            "minimo": "Minimo", 
            "maximo": "Maximo",
            "desviopadrao": "DesvioPadrao",
        }
        
        campo = metric_map.get(metric.lower(), "Mediana")
        valor_principal = item.get(campo)
        
        # Resultado estruturado
        result = {
            "valor": valor_principal,
            "indicador": item.get("Indicador"),
            "ano_referencia": item.get("DataReferencia"),
            "data_pesquisa": item.get("Data"),
            "metrica_solicitada": metric,
            "base_calculo": item.get("baseCalculo"),
            "respondentes": item.get("numeroRespondentes"),
            "top5": top5,
            "todas_metricas": {
                "mediana": item.get("Mediana"),
                "media": item.get("Media"),
                "minimo": item.get("Minimo"),
                "maximo": item.get("Maximo"),
                "desvio_padrao": item.get("DesvioPadrao"),
            }
        }
        
        return result
        
    except httpx.RequestError as e:
        logger.error(f"Erro de rede ao buscar Focus {indicator}: {e}")
        return {"erro": f"Erro de conexão com BCB Focus: {str(e)}"}
    except httpx.HTTPStatusError as e:
        logger.error(f"Erro HTTP ao buscar Focus {indicator}: {e}")
        return {"erro": f"Erro HTTP {e.response.status_code} do BCB Focus"}
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar Focus {indicator}: {e}")
        return {"erro": f"Erro interno: {str(e)}"}

async def get_focus_summary(year: int = None) -> Dict:
    """
    Busca resumo das principais expectativas Focus.
    
    Args:
        year: Ano de referência. Se None, usa ano atual+1
    
    Returns:
        dict com resumo das expectativas principais
    """
    if year is None:
        year = datetime.now().year + 1
        
    # Indicadores principais para resumo
    main_indicators = ["IPCA", "Selic", "PIB Total", "Taxa de câmbio"]
    summary = {"ano": year, "expectativas": {}}
    
    for indicator in main_indicators:
        try:
            result = await get_focus_expectations(indicator, year, "mediana")
            if "erro" not in result:
                summary["expectativas"][indicator] = {
                    "valor": result["valor"],
                    "data_pesquisa": result["data_pesquisa"],
                    "respondentes": result["respondentes"]
                }
            else:
                summary["expectativas"][indicator] = {"erro": result["erro"]}
        except Exception as e:
            summary["expectativas"][indicator] = {"erro": str(e)}
    
    return summary

def get_indicator_description(indicator: str) -> str:
    """Retorna descrição do indicador Focus."""
    descriptions = {
        "IPCA": "Índice Nacional de Preços ao Consumidor Amplo (%)",
        "IGP-M": "Índice Geral de Preços do Mercado (%)",
        "IGP-DI": "Índice Geral de Preços - Disponibilidade Interna (%)",
        "INPC": "Índice Nacional de Preços ao Consumidor (%)",
        "Taxa de câmbio": "Taxa de Câmbio R$/US$ (fim do período)",
        "Selic": "Taxa Selic (% ao ano)",
        "PIB Total": "PIB Total - variação real anual (%)",
        "PIB Agropecuária": "PIB Agropecuária - variação real anual (%)",
        "PIB Indústria": "PIB Indústria - variação real anual (%)", 
        "PIB Serviços": "PIB Serviços - variação real anual (%)",
        "Produção industrial": "Produção Industrial - variação anual (%)",
        "Conta corrente": "Conta Corrente (US$ milhões)",
        "Balança comercial": "Balança Comercial (US$ milhões)",
        "Dívida líquida do setor público": "Dívida Líquida do Setor Público (% PIB)",
        "Resultado primário": "Resultado Primário (% PIB)",
        "Investimento direto no país": "Investimento Direto no País (US$ milhões)"
    }
    return descriptions.get(indicator, f"{indicator} - Focus BCB")

# Função auxiliar para análise temporal das expectativas
async def get_focus_evolution(indicator: str, metric: str = "mediana") -> Dict:
    """
    Busca evolução das expectativas ao longo do tempo.
    Útil para ver como as expectativas mudaram.
    """
    try:
        url = f"{FOCUS_BASE_URL}ExpectativasMercadoAnuais"
        
        # Buscar últimas 10 pesquisas do indicador
        filters = [f"Indicador eq '{indicator}'"]
        params = {
            "$filter": " and ".join(filters),
            "$orderby": "Data desc",
            "$top": 10,
            "$format": "json",
            "$select": "Indicador,Data,DataReferencia,Mediana,Media"
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        
        items = data.get("value", [])
        if not items:
            return {"erro": f"Sem dados de evolução para {indicator}"}
        
        evolution = []
        for item in items:
            evolution.append({
                "data": item.get("Data"),
                "ano_referencia": item.get("DataReferencia"),
                "mediana": item.get("Mediana"),
                "media": item.get("Media")
            })
        
        return {
            "indicador": indicator,
            "evolucao": evolution,
            "total_registros": len(evolution)
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar evolução Focus {indicator}: {e}")
        return {"erro": f"Erro ao buscar evolução: {str(e)}"}