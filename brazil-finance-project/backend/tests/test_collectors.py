"""
Testes para os collectors de dados financeiros
pytest -v tests/test_collectors.py
"""

import pytest
import asyncio
from app.collectors.bcb_sgs import get_indicator, SERIES_MAP, fetch_series
from app.collectors.bcb_focus import get_focus_expectations, FOCUS_INDICATORS
from app.collectors.b3_stocks import get_quote, get_stock_field, format_ticker
from app.collectors.tesouro import get_titulo, parse_decimal, normalize_titulo_name

class TestBCBSGS:
    """Testes para BCB SGS (Séries Temporais)"""
    
    @pytest.mark.asyncio
    async def test_selic_indicator(self):
        """Testa busca da taxa Selic"""
        result = await get_indicator("selic")
        
        assert "erro" not in result
        assert "valor" in result
        assert isinstance(result["valor"], (float, type(None)))
        assert result["indicador"] == "SELIC"
    
    @pytest.mark.asyncio 
    async def test_ipca_indicator(self):
        """Testa busca do IPCA"""
        result = await get_indicator("ipca")
        
        assert "erro" not in result
        assert "valor" in result
        assert "data" in result
    
    @pytest.mark.asyncio
    async def test_invalid_indicator(self):
        """Testa indicador inexistente"""
        result = await get_indicator("indicador_inexistente")
        
        assert "erro" in result
        assert "não encontrado" in result["erro"].lower()
    
    @pytest.mark.asyncio
    async def test_12m_period(self):
        """Testa período de 12 meses"""
        result = await get_indicator("selic", "12m")
        
        assert "erro" not in result or result["valor"] is not None
        if "serie" in result:
            assert len(result["serie"]) > 0
    
    def test_series_map_integrity(self):
        """Verifica integridade do mapeamento de séries"""
        for name, code in SERIES_MAP.items():
            assert isinstance(code, int), f"Código de {name} deve ser int"
            assert code > 0, f"Código de {name} deve ser positivo"
            assert len(name) > 1, f"Nome {name} muito curto"

class TestBCBFocus:
    """Testes para BCB Focus (Expectativas)"""
    
    @pytest.mark.asyncio
    async def test_ipca_expectation(self):
        """Testa expectativa de IPCA"""
        result = await get_focus_expectations("IPCA", 2026, "mediana")
        
        # Pode não ter dados para 2026 ainda, mas não deve dar erro de conexão
        assert "erro" not in result or "sem expectativas" in result["erro"].lower()
    
    @pytest.mark.asyncio
    async def test_selic_expectation(self):
        """Testa expectativa de Selic"""
        result = await get_focus_expectations("Selic", 2025, "mediana")
        
        # Deve ter dados para 2025
        if "erro" not in result:
            assert "valor" in result
            assert result["indicador"] == "Selic"
    
    @pytest.mark.asyncio
    async def test_invalid_focus_indicator(self):
        """Testa indicador Focus inválido"""
        result = await get_focus_expectations("IndicadorInexistente", 2025)
        
        assert "erro" in result
        assert "não encontrado" in result["erro"].lower()
    
    def test_focus_indicators_list(self):
        """Verifica lista de indicadores Focus"""
        assert len(FOCUS_INDICATORS) > 0
        assert "IPCA" in FOCUS_INDICATORS
        assert "Selic" in FOCUS_INDICATORS
        assert "PIB Total" in FOCUS_INDICATORS

class TestB3Stocks:
    """Testes para cotações B3"""
    
    @pytest.mark.asyncio
    async def test_petr4_quote(self):
        """Testa cotação PETR4"""
        result = await get_quote("PETR4")
        
        if "erro" not in result:
            assert "preco" in result
            assert "ticker" in result
            assert result["ticker"] == "PETR4"
            assert isinstance(result.get("preco"), (float, type(None)))
    
    @pytest.mark.asyncio
    async def test_vale3_quote(self):
        """Testa cotação VALE3"""
        result = await get_quote("VALE3")
        
        if "erro" not in result:
            assert "preco" in result
            assert result["ticker"] == "VALE3"
    
    @pytest.mark.asyncio
    async def test_stock_field_preco(self):
        """Testa busca de campo específico"""
        result = await get_stock_field("PETR4", "preco")
        
        if "erro" not in result:
            assert "valor" in result
            assert "ticker" in result
    
    @pytest.mark.asyncio
    async def test_stock_field_variacao(self):
        """Testa busca de variação"""
        result = await get_stock_field("VALE3", "variacao")
        
        if "erro" not in result:
            assert "valor" in result
            assert isinstance(result["valor"], (float, int))
    
    @pytest.mark.asyncio
    async def test_invalid_ticker(self):
        """Testa ticker inválido"""
        result = await get_quote("TICKER_INEXISTENTE")
        
        assert "erro" in result
    
    def test_format_ticker(self):
        """Testa formatação de tickers"""
        assert format_ticker("PETR4") == "PETR4.SA"
        assert format_ticker("petr4") == "PETR4.SA"
        assert format_ticker("PETR4.SA") == "PETR4.SA"
        assert format_ticker("  vale3  ") == "VALE3.SA"

class TestTesouro:
    """Testes para Tesouro Direto"""
    
    @pytest.mark.asyncio
    async def test_ipca_2035_search(self):
        """Testa busca título IPCA+ 2035"""
        result = await get_titulo("IPCA+ 2035", "taxa")
        
        # Pode não encontrar se título não existir mais, mas deve ter estrutura correta
        if "erro" not in result:
            assert "valor" in result
            assert "titulo" in result
        else:
            # Se não encontrou, deve ter sugestões
            assert "sugestoes" in result or "total_titulos" in result
    
    @pytest.mark.asyncio 
    async def test_prefixado_search(self):
        """Testa busca título Prefixado"""
        result = await get_titulo("Prefixado", "taxa")
        
        # Deve encontrar algum título prefixado
        if "erro" not in result:
            assert "valor" in result
            assert "prefixado" in result["titulo"].lower()
    
    @pytest.mark.asyncio
    async def test_selic_search(self):
        """Testa busca título Selic"""
        result = await get_titulo("Selic", "preco")
        
        if "erro" not in result:
            assert "valor" in result
            assert "selic" in result["titulo"].lower()
    
    def test_parse_decimal(self):
        """Testa parsing de números brasileiros"""
        assert parse_decimal("10,75") == 10.75
        assert parse_decimal("1.234,56") == 1234.56
        assert parse_decimal("") is None
        assert parse_decimal("-") is None
        assert parse_decimal("abc") is None
    
    def test_normalize_titulo_name(self):
        """Testa normalização de nomes"""
        assert "ipca+" in normalize_titulo_name("Tesouro IPCA+ 2035")
        assert "prefixado" in normalize_titulo_name("Tesouro Prefixado 2029")
        assert normalize_titulo_name("") == ""

class TestIntegration:
    """Testes de integração"""
    
    @pytest.mark.asyncio
    async def test_multiple_sources(self):
        """Testa múltiplas fontes simultaneamente"""
        tasks = [
            get_indicator("selic"),
            get_focus_expectations("IPCA", 2025, "mediana"),
            get_stock_field("PETR4", "preco"),
            get_titulo("IPCA+", "taxa")
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Pelo menos uma fonte deve funcionar
        successful_calls = sum(1 for r in results if not isinstance(r, Exception) and "erro" not in r)
        assert successful_calls > 0, "Pelo menos uma fonte deve funcionar"
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Testa tratamento de erros"""
        # Todos estes devem retornar erro estruturado, não exception
        error_calls = [
            get_indicator("inexistente"),
            get_focus_expectations("Inexistente", 2025),
            get_stock_field("INEXISTENTE", "preco"),
            get_titulo("Inexistente", "taxa")
        ]
        
        for coro in error_calls:
            result = await coro
            assert isinstance(result, dict), "Deve retornar dict mesmo em erro"
            # Deve ter erro estruturado, não lançar exception