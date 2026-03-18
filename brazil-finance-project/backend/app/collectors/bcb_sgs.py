"""
Collector: BCB SGS (Sistema Gerenciador de Séries Temporais)
Fonte: https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados
Documentação: https://dadosabertos.bcb.gov.br/
"""

import httpx
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

# URL base da API BCB SGS
BCB_SGS_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados"

# Mapeamento de nomes amigáveis para códigos SGS
SERIES_MAP = {
    # Taxas de juros
    "selic": 432,           # Taxa Selic Meta
    "selic_over": 1178,     # Taxa Selic Over
    "cdi": 12,              # CDI
    "tr": 226,              # Taxa Referencial
    
    # Inflação
    "ipca": 433,            # IPCA mensal
    "ipca_acum12m": 13522,  # IPCA acumulado 12 meses
    "igpm": 189,            # IGP-M mensal
    "igpm_acum12m": 28655,  # IGP-M acumulado 12 meses
    "inpc": 188,            # INPC mensal
    
    # Câmbio
    "dolar": 1,             # Dólar PTAX venda
    "euro": 21619,          # Euro PTAX venda
    
    # Atividade econômica
    "pib_mensal": 4380,     # PIB mensal (proxy BCB)
    "ibc_br": 24364,        # IBC-Br (proxy PIB mensal)
    "producao_industrial": 21859,  # Produção industrial
    
    # Crédito e monetário
    "credito_pf": 20539,    # Saldo crédito Pessoa Física
    "credito_pj": 20541,    # Saldo crédito Pessoa Jurídica
    "m1": 27788,            # Base monetária M1
    
    # Setor fiscal
    "divida_liquida_pib": 4513,   # Dívida líquida/PIB
    "resultado_primario": 5793,   # Resultado primário
    
    # Mercado de trabalho
    "desemprego": 24369,    # PNAD taxa desocupação
    
    # Setor externo
    "reservas": 3546,       # Reservas internacionais
    "conta_corrente": 23462, # Conta corrente
}

async def fetch_series(code: int, start_date: str = None, end_date: str = None) -> Dict:
    """
    Busca série temporal do BCB SGS.
    
    Args:
        code: Código da série no SGS
        start_date: Data início formato DD/MM/YYYY (opcional)
        end_date: Data fim formato DD/MM/YYYY (opcional)
    
    Returns:
        dict com 'ultimo_valor', 'data', 'serie' (lista completa se solicitada)
    """
    params = {"formato": "json"}
    
    if start_date:
        params["dataInicial"] = start_date
    if end_date:
        params["dataFinal"] = end_date
    
    # Se não especificou datas, pegar últimos 60 dias para garantir dados recentes
    if not start_date and not end_date:
        end = datetime.now()
        start = end - timedelta(days=60)
        params["dataInicial"] = start.strftime("%d/%m/%Y")
        params["dataFinal"] = end.strftime("%d/%m/%Y")
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                BCB_SGS_URL.format(code=code),
                params=params
            )
            response.raise_for_status()
            data = response.json()
        
        if not data:
            return {"valor": None, "data": None, "erro": "Sem dados disponíveis"}
        
        # Último valor disponível
        ultimo = data[-1]
        
        # Converter valor para float, tratando possíveis formatos
        try:
            valor = float(ultimo["valor"]) if ultimo["valor"] else None
        except (ValueError, TypeError):
            valor = None
            
        return {
            "valor": valor,
            "data": ultimo["data"],
            "codigo_sgs": code,
            "total_registros": len(data),
            "serie": data[-10:]  # Últimos 10 registros para contexto
        }
        
    except httpx.RequestError as e:
        logger.error(f"Erro de rede ao buscar série {code}: {e}")
        return {"erro": f"Erro de conexão com BCB: {str(e)}"}
    except httpx.HTTPStatusError as e:
        logger.error(f"Erro HTTP ao buscar série {code}: {e}")
        return {"erro": f"Erro HTTP {e.response.status_code} do BCB"}
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar série {code}: {e}")
        return {"erro": f"Erro interno: {str(e)}"}

async def get_indicator(name: str, period: str = "ultimo") -> Dict:
    """
    Interface amigável para buscar indicadores econômicos.
    
    Args:
        name: Nome amigável do indicador (ex: "selic", "ipca", "dolar")
        period: Período desejado
            - "ultimo": último valor disponível
            - "12m": últimos 12 meses
            - "ytd": ano corrente
            - "DD/MM/YYYY:DD/MM/YYYY": período específico
    
    Returns:
        dict com valor do indicador e metadados
    """
    # Verificar se indicador existe
    code = SERIES_MAP.get(name.lower())
    if not code:
        available = list(SERIES_MAP.keys())[:10]  # Primeiros 10 para não sobrecarregar
        return {
            "erro": f"Indicador '{name}' não encontrado. Disponíveis: {available}... (total: {len(SERIES_MAP)})"
        }
    
    try:
        # Processar período
        start_date, end_date = None, None
        
        if period == "ultimo":
            # Fetch_series já pega últimos 60 dias por padrão
            result = await fetch_series(code)
            
        elif period == "12m":
            end = datetime.now()
            start = end - timedelta(days=365)
            start_date = start.strftime("%d/%m/%Y")
            end_date = end.strftime("%d/%m/%Y")
            result = await fetch_series(code, start_date, end_date)
            
        elif period == "ytd":
            start = datetime(datetime.now().year, 1, 1)
            end = datetime.now()
            start_date = start.strftime("%d/%m/%Y")
            end_date = end.strftime("%d/%m/%Y")
            result = await fetch_series(code, start_date, end_date)
            
        elif ":" in period:
            # Período customizado "DD/MM/YYYY:DD/MM/YYYY"
            try:
                start_str, end_str = period.split(":")
                # Validar formato das datas
                datetime.strptime(start_str.strip(), "%d/%m/%Y")
                datetime.strptime(end_str.strip(), "%d/%m/%Y")
                result = await fetch_series(code, start_str.strip(), end_str.strip())
            except ValueError:
                return {"erro": "Formato de período inválido. Use DD/MM/YYYY:DD/MM/YYYY"}
                
        else:
            return {"erro": f"Período '{period}' não suportado. Use: ultimo, 12m, ytd, ou DD/MM/YYYY:DD/MM/YYYY"}
        
        # Adicionar metadados do indicador
        if "erro" not in result:
            result["indicador"] = name.upper()
            result["nome_completo"] = get_indicator_name(name)
            result["periodo_solicitado"] = period
            
        return result
        
    except Exception as e:
        logger.error(f"Erro ao processar indicador {name}: {e}")
        return {"erro": f"Erro ao processar indicador: {str(e)}"}

def get_indicator_name(name: str) -> str:
    """Retorna nome completo do indicador."""
    names = {
        "selic": "Taxa Selic Meta",
        "selic_over": "Taxa Selic Over",
        "cdi": "Certificado de Depósito Interbancário",
        "tr": "Taxa Referencial",
        "ipca": "IPCA Mensal",
        "ipca_acum12m": "IPCA Acumulado 12 Meses",
        "igpm": "IGP-M Mensal",
        "igpm_acum12m": "IGP-M Acumulado 12 Meses",
        "inpc": "INPC Mensal",
        "dolar": "Taxa de Câmbio USD/BRL PTAX",
        "euro": "Taxa de Câmbio EUR/BRL PTAX",
        "pib_mensal": "PIB Mensal",
        "ibc_br": "Índice de Atividade Econômica (IBC-Br)",
        "producao_industrial": "Produção Industrial",
        "credito_pf": "Operações de Crédito - Pessoa Física",
        "credito_pj": "Operações de Crédito - Pessoa Jurídica",
        "m1": "Base Monetária M1",
        "divida_liquida_pib": "Dívida Líquida do Setor Público / PIB",
        "resultado_primario": "Resultado Primário do Governo Central",
        "desemprego": "Taxa de Desocupação (PNAD)",
        "reservas": "Reservas Internacionais",
        "conta_corrente": "Transações Correntes",
    }
    return names.get(name.lower(), name.upper())

# Função auxiliar para listar todos os indicadores
def list_available_indicators() -> Dict[str, Dict]:
    """Lista todos os indicadores disponíveis com metadados."""
    indicators = {}
    for name, code in SERIES_MAP.items():
        indicators[name] = {
            "codigo_sgs": code,
            "nome_completo": get_indicator_name(name),
            "categoria": get_indicator_category(name)
        }
    return indicators

def get_indicator_category(name: str) -> str:
    """Retorna categoria do indicador."""
    categories = {
        "selic": "Juros", "selic_over": "Juros", "cdi": "Juros", "tr": "Juros",
        "ipca": "Inflação", "ipca_acum12m": "Inflação", "igpm": "Inflação", 
        "igpm_acum12m": "Inflação", "inpc": "Inflação",
        "dolar": "Câmbio", "euro": "Câmbio",
        "pib_mensal": "Atividade", "ibc_br": "Atividade", "producao_industrial": "Atividade",
        "credito_pf": "Crédito", "credito_pj": "Crédito", "m1": "Monetário",
        "divida_liquida_pib": "Fiscal", "resultado_primario": "Fiscal",
        "desemprego": "Trabalho",
        "reservas": "Externo", "conta_corrente": "Externo",
    }
    return categories.get(name.lower(), "Outros")