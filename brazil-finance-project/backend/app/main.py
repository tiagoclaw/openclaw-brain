"""
BrazilFinance API - Backend Principal
FastAPI application para servir dados financeiros brasileiros
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BrazilFinance API",
    description="API unificada de dados financeiros brasileiros para Google Sheets",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS - permitir chamadas do Google Sheets
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restringir para Google Apps Script
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    allow_credentials=False,
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"erro": "Erro interno do servidor", "detail": str(exc)}
    )

# ------- ROTAS PRINCIPAIS -------

@app.get("/")
async def root():
    """Health check e informações da API."""
    return {
        "service": "BrazilFinance API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "endpoints": {
            "bcb": "/v1/bcb/{indicator}",
            "focus": "/v1/focus/{indicator}", 
            "b3": "/v1/b3/{ticker}",
            "tesouro": "/v1/tesouro/{titulo}"
        }
    }

@app.get("/v1/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok", 
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# ------- ROTAS BCB (INDICADORES MACRO) -------

@app.get("/v1/bcb/{indicator}")
async def bcb_indicator(
    indicator: str,
    period: str = Query("ultimo", description="ultimo, 12m, ytd, ou DD/MM/YYYY:DD/MM/YYYY")
):
    """Busca indicador do Banco Central do Brasil (SGS)."""
    try:
        from app.collectors.bcb_sgs import get_indicator
        result = await get_indicator(indicator.lower(), period)
        
        if "erro" in result:
            raise HTTPException(status_code=404, detail=result["erro"])
        
        return {
            **result,
            "fonte": "BCB-SGS",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"BCB indicator error: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar indicador BCB: {str(e)}")

@app.get("/v1/focus/{indicator}")
async def focus_expectation(
    indicator: str,
    year: int = Query(None, description="Ano de referência (ex: 2025, 2026)"),
    metric: str = Query("mediana", description="mediana, media, minimo, maximo, desviopadrao"),
    top5: bool = Query(False, description="Se True, retorna expectativas Top 5")
):
    """Busca expectativas Focus do BCB."""
    try:
        from app.collectors.bcb_focus import get_focus_expectations
        result = await get_focus_expectations(indicator, year, metric, top5)
        
        if "erro" in result:
            raise HTTPException(status_code=404, detail=result["erro"])
            
        return {
            **result,
            "fonte": "BCB-Focus",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Focus expectation error: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar expectativa Focus: {str(e)}")

# ------- ROTAS B3 (AÇÕES, FIIS, ETFS) -------

@app.get("/v1/b3/{ticker}")
async def b3_quote(
    ticker: str,
    field: str = Query("preco", description="preco, variacao, fechamento_anterior, volume")
):
    """Busca cotação de ação/FII/ETF da B3."""
    try:
        from app.collectors.b3_stocks import get_stock_field
        result = await get_stock_field(ticker.upper(), field.lower())
        
        if "erro" in result:
            raise HTTPException(status_code=404, detail=result["erro"])
            
        return {
            **result,
            "fonte": "B3-Yahoo",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"B3 quote error: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar cotação B3: {str(e)}")

# ------- ROTAS TESOURO DIRETO -------

@app.get("/v1/tesouro/{titulo}")
async def tesouro_titulo(
    titulo: str,
    field: str = Query("taxa", description="taxa, taxa_compra, taxa_venda, preco, preco_compra, preco_venda")
):
    """Busca dados de título do Tesouro Direto."""
    try:
        from app.collectors.tesouro import get_titulo
        result = await get_titulo(titulo, field.lower())
        
        if "erro" in result:
            raise HTTPException(status_code=404, detail=result["erro"])
            
        return {
            **result,
            "fonte": "Tesouro-Transparente",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Tesouro error: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar título Tesouro: {str(e)}")

# ------- ROTAS META/DOCUMENTAÇÃO -------

@app.get("/v1/indicators")
async def list_indicators():
    """Lista todos os indicadores disponíveis na API."""
    try:
        from app.collectors.bcb_sgs import SERIES_MAP
        from app.collectors.bcb_focus import FOCUS_INDICATORS
        
        return {
            "bcb_sgs": {
                "description": "Indicadores do Banco Central (SGS)",
                "indicators": list(SERIES_MAP.keys()),
                "usage": "GET /v1/bcb/{indicator}?period=ultimo"
            },
            "bcb_focus": {
                "description": "Expectativas de mercado Focus",
                "indicators": FOCUS_INDICATORS,
                "usage": "GET /v1/focus/{indicator}?year=2026&metric=mediana"
            },
            "b3": {
                "description": "Cotações B3 (ações, FIIs, ETFs)",
                "indicators": "Qualquer ticker da B3 (ex: PETR4, VALE3, HGLG11, BOVA11)",
                "usage": "GET /v1/b3/{ticker}?field=preco"
            },
            "tesouro": {
                "description": "Títulos do Tesouro Direto",
                "indicators": "Qualquer título (ex: 'IPCA+ 2035', 'Prefixado 2029', 'Selic 2029')",
                "usage": "GET /v1/tesouro/{titulo}?field=taxa"
            }
        }
    except Exception as e:
        logger.error(f"List indicators error: {e}")
        return {"erro": f"Erro ao listar indicadores: {str(e)}"}

# ------- STARTUP EVENT -------

@app.on_event("startup")
async def startup_event():
    """Inicialização da aplicação."""
    logger.info("BrazilFinance API iniciando...")
    logger.info("Endpoints disponíveis: /docs para documentação")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)