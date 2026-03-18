"""
Collector: B3 Stocks (Ações, FIIs, ETFs)
Fonte: Yahoo Finance API (não-oficial mas estável e gratuita)
URL: https://query1.finance.yahoo.com/v8/finance/chart/{ticker}

Para MVP usamos Yahoo Finance. Migrar para fonte B3 oficial depois se necessário.
Tickers B3 no Yahoo Finance terminam com .SA (ex: PETR4.SA)
"""

import httpx
import logging
from datetime import datetime, timezone
from typing import Dict, Optional, List
import json

logger = logging.getLogger(__name__)

# Yahoo Finance API URLs
YAHOO_QUOTE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
YAHOO_SUMMARY_URL = "https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"

def format_ticker(ticker: str) -> str:
    """
    Formata ticker para Yahoo Finance.
    PETR4 -> PETR4.SA
    """
    ticker = ticker.upper().strip()
    if not ticker.endswith(".SA"):
        ticker = f"{ticker}.SA"
    return ticker

def clean_ticker(ticker: str) -> str:
    """Remove .SA do ticker para retorno limpo."""
    return ticker.upper().replace(".SA", "")

async def get_quote(ticker: str) -> Dict:
    """
    Busca cotação atual de ação/FII/ETF da B3.
    
    Args:
        ticker: Código do ativo (ex: "PETR4", "VALE3", "HGLG11", "BOVA11")
    
    Returns:
        dict com preço, variação, volume, etc.
    """
    yahoo_ticker = format_ticker(ticker)
    
    params = {
        "interval": "1d",
        "range": "5d",  # Últimos 5 dias para ter contexto
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                YAHOO_QUOTE_URL.format(ticker=yahoo_ticker),
                params=params,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
        
        # Verificar se resposta tem dados válidos
        if "chart" not in data or not data["chart"]["result"]:
            return {"erro": f"Ticker '{ticker}' não encontrado ou sem dados"}
        
        result = data["chart"]["result"][0]
        meta = result["meta"]
        
        # Dados básicos
        preco_atual = meta.get("regularMarketPrice", 0)
        preco_anterior = meta.get("previousClose", 0) or meta.get("chartPreviousClose", 0)
        
        # Calcular variação percentual
        variacao_pct = 0
        if preco_anterior and preco_anterior > 0:
            variacao_pct = ((preco_atual - preco_anterior) / preco_anterior) * 100
        
        variacao_abs = preco_atual - preco_anterior if preco_anterior else 0
        
        # Timestamp da cotação
        market_time = meta.get("regularMarketTime", 0)
        timestamp = datetime.fromtimestamp(market_time, tz=timezone.utc) if market_time else datetime.now(tz=timezone.utc)
        
        # Informações do pregão
        volume = meta.get("regularMarketVolume", 0)
        high = meta.get("regularMarketDayHigh", 0)
        low = meta.get("regularMarketDayLow", 0)
        
        # Informações adicionais
        currency = meta.get("currency", "BRL")
        exchange = meta.get("exchangeName", "SAO")
        market_state = meta.get("marketState", "UNKNOWN")
        
        return {
            "ticker": clean_ticker(ticker),
            "preco": round(preco_atual, 2) if preco_atual else None,
            "preco_anterior": round(preco_anterior, 2) if preco_anterior else None,
            "variacao_absoluta": round(variacao_abs, 2) if variacao_abs else None,
            "variacao_percentual": round(variacao_pct, 2),
            "maxima_dia": round(high, 2) if high else None,
            "minima_dia": round(low, 2) if low else None,
            "volume": volume,
            "moeda": currency,
            "pregao": exchange,
            "status_mercado": market_state,
            "timestamp": timestamp.isoformat(),
            "data_referencia": timestamp.strftime("%d/%m/%Y"),
            "hora_referencia": timestamp.strftime("%H:%M:%S")
        }
        
    except httpx.RequestError as e:
        logger.error(f"Erro de rede ao buscar {ticker}: {e}")
        return {"erro": f"Erro de conexão: {str(e)}"}
    except httpx.HTTPStatusError as e:
        logger.error(f"Erro HTTP ao buscar {ticker}: {e}")
        return {"erro": f"Erro HTTP {e.response.status_code}"}
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar resposta para {ticker}: {e}")
        return {"erro": "Erro ao processar dados do Yahoo Finance"}
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar {ticker}: {e}")
        return {"erro": f"Erro interno: {str(e)}"}

async def get_stock_field(ticker: str, field: str) -> Dict:
    """
    Busca campo específico de uma ação.
    
    Args:
        ticker: Código do ativo
        field: Campo desejado:
            - "preco": Preço atual
            - "variacao": Variação percentual
            - "variacao_abs": Variação absoluta
            - "fechamento_anterior": Preço fechamento anterior
            - "volume": Volume negociado
            - "maxima": Máxima do dia
            - "minima": Mínima do dia
    
    Returns:
        dict com valor do campo solicitado
    """
    quote = await get_quote(ticker)
    
    if "erro" in quote:
        return quote
    
    # Mapear campo solicitado para chave na resposta
    field_map = {
        "preco": "preco",
        "price": "preco", 
        "cotacao": "preco",
        "variacao": "variacao_percentual",
        "var": "variacao_percentual",
        "change": "variacao_percentual",
        "variacao_pct": "variacao_percentual",
        "variacao_abs": "variacao_absoluta",
        "fechamento_anterior": "preco_anterior",
        "anterior": "preco_anterior",
        "previous": "preco_anterior",
        "volume": "volume",
        "vol": "volume",
        "maxima": "maxima_dia",
        "max": "maxima_dia",
        "high": "maxima_dia",
        "minima": "minima_dia", 
        "min": "minima_dia",
        "low": "minima_dia",
        "moeda": "moeda",
        "currency": "moeda",
    }
    
    mapped_field = field_map.get(field.lower())
    if not mapped_field:
        available = list(field_map.keys())[:10]
        return {
            "erro": f"Campo '{field}' não disponível",
            "campos_disponíveis": available,
            "ticker": clean_ticker(ticker)
        }
    
    if mapped_field not in quote:
        return {
            "erro": f"Campo '{field}' não encontrado nos dados",
            "ticker": clean_ticker(ticker)
        }
    
    return {
        "valor": quote[mapped_field],
        "ticker": quote["ticker"],
        "campo": field,
        "timestamp": quote["timestamp"],
        "contexto": {
            "preco": quote.get("preco"),
            "variacao_pct": quote.get("variacao_percentual")
        }
    }

async def get_multiple_quotes(tickers: List[str]) -> Dict:
    """
    Busca cotações de múltiplos ativos.
    Útil para portfolios e comparações.
    
    Args:
        tickers: Lista de códigos dos ativos
    
    Returns:
        dict com cotações de todos os ativos
    """
    results = {}
    
    for ticker in tickers[:10]:  # Limitar a 10 para evitar sobrecarga
        try:
            quote = await get_quote(ticker)
            results[clean_ticker(ticker)] = quote
        except Exception as e:
            results[clean_ticker(ticker)] = {"erro": str(e)}
    
    return {
        "cotacoes": results,
        "total_ativos": len(tickers),
        "processados": len(results),
        "timestamp": datetime.now().isoformat()
    }

def classify_ticker(ticker: str) -> str:
    """
    Classifica tipo do ativo baseado no ticker.
    Heurística simples baseada em padrões comuns.
    """
    ticker = ticker.upper()
    
    if ticker.endswith("11"):
        return "FII"  # Fundos Imobiliários terminam em 11
    elif ticker.endswith("3") or ticker.endswith("4"):
        return "ACAO"  # Ações terminam em 3 ou 4
    elif ticker.startswith("HASH") or ticker.startswith("QBTC"):
        return "CRYPTO_ETF"  # ETFs de crypto
    elif ticker.startswith("BOVA") or ticker.startswith("SMAL") or ticker.startswith("PIBB"):
        return "ETF"  # ETFs de índices
    else:
        return "OUTROS"

async def get_stock_summary(ticker: str) -> Dict:
    """
    Busca resumo completo do ativo incluindo dados fundamentalistas.
    Usa endpoint quoteSummary do Yahoo Finance.
    """
    yahoo_ticker = format_ticker(ticker)
    
    params = {
        "modules": "price,summaryDetail,defaultKeyStatistics",
        "formatted": "false"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                YAHOO_SUMMARY_URL.format(ticker=yahoo_ticker),
                params=params,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
        
        if "quoteSummary" not in data or not data["quoteSummary"]["result"]:
            return {"erro": f"Dados detalhados não disponíveis para {ticker}"}
        
        result = data["quoteSummary"]["result"][0]
        
        # Extrair informações relevantes
        summary = {
            "ticker": clean_ticker(ticker),
            "tipo": classify_ticker(ticker),
            "resumo": {}
        }
        
        # Dados de preço
        if "price" in result:
            price = result["price"]
            summary["resumo"]["preco"] = price.get("regularMarketPrice", {}).get("raw")
            summary["resumo"]["variacao_52_semanas"] = {
                "minima": price.get("fiftyTwoWeekLow", {}).get("raw"),
                "maxima": price.get("fiftyTwoWeekHigh", {}).get("raw")
            }
        
        # Dados de mercado
        if "summaryDetail" in result:
            detail = result["summaryDetail"] 
            summary["resumo"]["valor_mercado"] = detail.get("marketCap", {}).get("raw")
            summary["resumo"]["volume_medio"] = detail.get("averageVolume", {}).get("raw")
        
        return summary
        
    except Exception as e:
        logger.error(f"Erro ao buscar resumo de {ticker}: {e}")
        return {"erro": f"Erro ao buscar resumo: {str(e)}"}