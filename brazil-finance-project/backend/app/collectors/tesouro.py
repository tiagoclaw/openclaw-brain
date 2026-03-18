"""
Collector: Tesouro Direto
Fonte: https://www.tesourotransparente.gov.br/ckan/dataset/taxas-dos-titulos-ofertados-pelo-tesouro-direto
CSV: https://www.tesourotransparente.gov.br/ckan/dataset/.../download/PressosTesouroDisponiveis.csv

NOTA: A URL do CSV pode mudar. Alternativas:
- Scrape da página https://www.tesourodireto.com.br/titulos/precos-e-taxas.htm
- API CKAN: https://www.tesourotransparente.gov.br/ckan/api/3/action/package_show?id=...
"""

import httpx
import csv
import io
import logging
from datetime import datetime
from typing import Dict, List, Optional
import re

logger = logging.getLogger(__name__)

# URL do CSV do Tesouro Transparente (pode mudar)
TESOURO_CSV_URL = "https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecosTaxasTesouroDireto.csv"

# URL alternativa/backup
TESOURO_BACKUP_URL = "https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PressosTesouroDisponiveis.csv"

def parse_decimal(value: str) -> Optional[float]:
    """
    Converte string com formato brasileiro (vírgula decimal) para float.
    Ex: "10,75" -> 10.75
    """
    if not value or value.strip() == "" or value.strip() == "-":
        return None
    
    try:
        # Remover espaços e trocar vírgula por ponto
        cleaned = value.strip().replace(".", "").replace(",", ".")
        return float(cleaned)
    except (ValueError, AttributeError):
        return None

def normalize_titulo_name(nome: str) -> str:
    """
    Normaliza nome do título para facilitar busca.
    Ex: "Tesouro IPCA+ 2035" -> "ipca+ 2035"
    """
    if not nome:
        return ""
    
    # Remover "Tesouro" do início
    normalized = re.sub(r'^Tesouro\s+', '', nome, flags=re.IGNORECASE)
    
    # Converter para minúsculas e remover espaços extras
    normalized = re.sub(r'\s+', ' ', normalized.lower().strip())
    
    return normalized

async def fetch_tesouro_data() -> List[Dict]:
    """
    Busca dados atuais de todos os títulos do Tesouro Direto do CSV oficial.
    
    Returns:
        Lista de dicts com dados de cada título
    """
    urls_to_try = [TESOURO_CSV_URL, TESOURO_BACKUP_URL]
    
    for url in urls_to_try:
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # CSV do governo brasileiro geralmente usa encoding latin-1 ou utf-8
                try:
                    content = response.content.decode('utf-8')
                except UnicodeDecodeError:
                    content = response.content.decode('latin-1')
                
                return parse_tesouro_csv(content)
                
        except Exception as e:
            logger.warning(f"Falha ao buscar {url}: {e}")
            continue
    
    # Se todas as URLs falharam
    raise Exception("Não foi possível acessar dados do Tesouro Direto")

def parse_tesouro_csv(csv_content: str) -> List[Dict]:
    """
    Parse do CSV do Tesouro Direto.
    
    Args:
        csv_content: Conteúdo do arquivo CSV
    
    Returns:
        Lista de títulos com dados normalizados
    """
    titulos = []
    
    # Detectar delimitador (pode ser ; ou ,)
    delimiter = ';' if ';' in csv_content[:1000] else ','
    
    reader = csv.DictReader(io.StringIO(csv_content), delimiter=delimiter)
    
    for row in reader:
        # Mapear colunas (nomes podem variar)
        titulo_data = {}
        
        # Buscar nome do título (várias possibilidades)
        nome = (row.get("Tipo Titulo") or 
                row.get("Nome") or 
                row.get("Título") or 
                row.get("Tipo_Titulo") or "")
        
        vencimento = (row.get("Data Vencimento") or 
                     row.get("Vencimento") or 
                     row.get("Data_Vencimento") or "")
        
        # Taxas e preços
        taxa_compra = parse_decimal(row.get("Taxa Compra Manha") or row.get("Taxa_Compra"))
        taxa_venda = parse_decimal(row.get("Taxa Venda Manha") or row.get("Taxa_Venda"))
        
        preco_compra = parse_decimal(row.get("PU Compra Manha") or row.get("PU_Compra"))
        preco_venda = parse_decimal(row.get("PU Venda Manha") or row.get("PU_Venda"))
        
        data_base = (row.get("Data Base") or 
                    row.get("Data_Base") or 
                    row.get("DataBase") or "")
        
        if nome:  # Só incluir se tem nome do título
            titulos.append({
                "nome": nome.strip(),
                "nome_normalizado": normalize_titulo_name(nome),
                "vencimento": vencimento.strip(),
                "taxa_compra": taxa_compra,
                "taxa_venda": taxa_venda,
                "preco_compra": preco_compra,
                "preco_venda": preco_venda,
                "data_base": data_base.strip(),
                "tipo": classify_titulo_type(nome)
            })
    
    logger.info(f"Parseados {len(titulos)} títulos do Tesouro Direto")
    return titulos

def classify_titulo_type(nome: str) -> str:
    """
    Classifica tipo do título baseado no nome.
    """
    nome_lower = nome.lower()
    
    if "ipca" in nome_lower:
        return "IPCA+"
    elif "prefixado" in nome_lower:
        return "Prefixado"
    elif "selic" in nome_lower:
        return "Selic"
    elif "igp-m" in nome_lower:
        return "IGP-M+"
    else:
        return "Outros"

async def get_titulo(nome_busca: str, campo: str = "taxa_compra") -> Dict:
    """
    Busca dados de um título específico do Tesouro Direto.
    
    Args:
        nome_busca: Nome parcial do título (ex: "IPCA+ 2035", "Prefixado 2029", "Selic 2029")
        campo: Campo desejado:
            - "taxa" ou "taxa_compra": Taxa de compra (padrão)
            - "taxa_venda": Taxa de venda
            - "preco" ou "preco_compra": Preço unitário de compra
            - "preco_venda": Preço unitário de venda
    
    Returns:
        dict com valor do campo solicitado e metadados
    """
    try:
        titulos = await fetch_tesouro_data()
        
        if not titulos:
            return {"erro": "Nenhum título encontrado nos dados do Tesouro"}
        
        # Busca fuzzy por nome
        nome_busca_clean = nome_busca.lower().strip()
        
        # Tentar match exato primeiro
        matches = [
            t for t in titulos 
            if nome_busca_clean in t["nome_normalizado"]
        ]
        
        # Se não achou, tentar busca mais flexível
        if not matches:
            # Remover caracteres especiais e espaços para busca mais ampla
            search_terms = re.findall(r'\w+', nome_busca_clean)
            matches = [
                t for t in titulos
                if all(term in t["nome_normalizado"] for term in search_terms if len(term) > 2)
            ]
        
        # Se ainda não achou, tentar por ano de vencimento
        if not matches and nome_busca.isdigit() and len(nome_busca) == 4:
            ano = nome_busca
            matches = [t for t in titulos if ano in t["vencimento"]]
        
        if not matches:
            # Sugerir títulos similares
            suggestions = []
            for titulo in titulos[:10]:  # Primeiros 10 títulos
                suggestions.append(f"{titulo['nome']} ({titulo['vencimento']})")
            
            return {
                "erro": f"Título '{nome_busca}' não encontrado",
                "sugestoes": suggestions,
                "total_titulos_disponiveis": len(titulos)
            }
        
        # Pegar o primeiro match (pode haver múltiplos títulos similares)
        titulo = matches[0]
        
        # Mapear campo solicitado
        campo_map = {
            "taxa": "taxa_compra",
            "taxa_compra": "taxa_compra",
            "taxa_venda": "taxa_venda",
            "preco": "preco_compra",
            "preco_compra": "preco_compra", 
            "preco_venda": "preco_venda",
            "pu": "preco_compra",
            "pu_compra": "preco_compra",
            "pu_venda": "preco_venda"
        }
        
        campo_real = campo_map.get(campo.lower(), "taxa_compra")
        valor = titulo.get(campo_real)
        
        if valor is None:
            return {
                "erro": f"Campo '{campo}' não disponível para este título",
                "titulo": titulo["nome"],
                "campos_disponiveis": [k for k, v in titulo.items() if v is not None and k.startswith(("taxa", "preco"))]
            }
        
        return {
            "valor": valor,
            "titulo": titulo["nome"],
            "vencimento": titulo["vencimento"],
            "tipo": titulo["tipo"],
            "campo_solicitado": campo,
            "data_base": titulo["data_base"],
            "dados_completos": {
                "taxa_compra": titulo["taxa_compra"],
                "taxa_venda": titulo["taxa_venda"],
                "preco_compra": titulo["preco_compra"],
                "preco_venda": titulo["preco_venda"]
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar título {nome_busca}: {e}")
        return {"erro": f"Erro ao buscar título: {str(e)}"}

async def get_tesouro_summary() -> Dict:
    """
    Retorna resumo de todos os títulos disponíveis no Tesouro Direto.
    Útil para análise de curva de juros.
    """
    try:
        titulos = await fetch_tesouro_data()
        
        if not titulos:
            return {"erro": "Nenhum título disponível"}
        
        # Agrupar por tipo
        by_type = {}
        for titulo in titulos:
            tipo = titulo["tipo"]
            if tipo not in by_type:
                by_type[tipo] = []
            
            by_type[tipo].append({
                "nome": titulo["nome"],
                "vencimento": titulo["vencimento"],
                "taxa_compra": titulo["taxa_compra"],
                "preco_compra": titulo["preco_compra"]
            })
        
        # Ordenar por vencimento dentro de cada tipo
        for tipo in by_type:
            by_type[tipo] = sorted(by_type[tipo], key=lambda x: x["vencimento"])
        
        return {
            "total_titulos": len(titulos),
            "data_base": titulos[0]["data_base"] if titulos else None,
            "tipos": list(by_type.keys()),
            "titulos_por_tipo": by_type,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar resumo Tesouro: {e}")
        return {"erro": f"Erro ao buscar resumo: {str(e)}"}

async def get_curva_juros(tipo: str = "IPCA+") -> Dict:
    """
    Monta curva de juros para um tipo específico de título.
    
    Args:
        tipo: Tipo do título ("IPCA+", "Prefixado", "Selic")
    
    Returns:
        dict com curva de taxas por vencimento
    """
    try:
        titulos = await fetch_tesouro_data()
        
        # Filtrar por tipo
        titulos_tipo = [t for t in titulos if t["tipo"] == tipo and t["taxa_compra"]]
        
        if not titulos_tipo:
            return {"erro": f"Nenhum título do tipo '{tipo}' encontrado"}
        
        # Ordenar por vencimento
        curva = sorted(titulos_tipo, key=lambda x: x["vencimento"])
        
        pontos_curva = []
        for titulo in curva:
            pontos_curva.append({
                "vencimento": titulo["vencimento"],
                "taxa": titulo["taxa_compra"],
                "nome": titulo["nome"]
            })
        
        return {
            "tipo": tipo,
            "total_pontos": len(pontos_curva),
            "curva": pontos_curva,
            "data_base": curva[0]["data_base"] if curva else None
        }
        
    except Exception as e:
        logger.error(f"Erro ao montar curva {tipo}: {e}")
        return {"erro": f"Erro ao montar curva: {str(e)}"}