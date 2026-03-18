#!/usr/bin/env python3
"""
BrazilFinance Demo Server
Servidor HTTP simples para demonstração da API
"""

import json
import random
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

class BrazilFinanceHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        params = parse_qs(parsed_path.query)
        
        # CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
        
        # Routing
        if path == '/v1/health':
            self.health_check()
        elif path.startswith('/v1/bcb/'):
            indicator = path.split('/')[-1]
            self.bcb_indicator(indicator, params)
        elif path.startswith('/v1/focus/'):
            indicator = path.split('/')[-1]
            self.focus_expectation(indicator, params)
        elif path.startswith('/v1/b3/'):
            ticker = path.split('/')[-1]
            self.b3_quote(ticker, params)
        elif path.startswith('/v1/tesouro/'):
            title = path.split('/')[-1]
            self.tesouro_bond(title, params)
        elif path == '/v1/indicators':
            self.list_indicators()
        else:
            self.send_error(404, "Endpoint not found")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
        self.end_headers()
    
    def send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def health_check(self):
        data = {
            "status": "healthy",
            "service": "BrazilFinance Demo API",
            "version": "1.0.0-demo",
            "timestamp": datetime.now().isoformat(),
            "uptime": "Demo mode",
            "endpoints": [
                "/v1/bcb/{indicator}",
                "/v1/focus/{indicator}",
                "/v1/b3/{ticker}",
                "/v1/tesouro/{title}"
            ]
        }
        self.send_json_response(data)
    
    def bcb_indicator(self, indicator, params):
        # Mock data for BCB indicators
        mock_data = {
            "selic": {"valor": 10.75, "data": "2026-03-17", "unidade": "%"},
            "ipca": {"valor": 0.32, "data": "2026-02-28", "unidade": "% mês"},
            "cdi": {"valor": 10.90, "data": "2026-03-17", "unidade": "%"},
            "dolar": {"valor": 5.15, "data": "2026-03-17", "unidade": "R$/USD"},
            "euro": {"valor": 5.58, "data": "2026-03-17", "unidade": "R$/EUR"},
            "igpm": {"valor": 0.28, "data": "2026-02-28", "unidade": "% mês"},
            "ibc_br": {"valor": 1.2, "data": "2026-01-31", "unidade": "% trim"},
            "desemprego": {"valor": 7.8, "data": "2026-02-28", "unidade": "%"}
        }
        
        if indicator.lower() in mock_data:
            data = mock_data[indicator.lower()]
            data["indicador"] = indicator.upper()
            data["fonte"] = "BCB SGS"
            data["demo"] = True
            self.send_json_response(data)
        else:
            self.send_json_response({
                "erro": f"Indicador '{indicator}' não encontrado",
                "indicadores_disponiveis": list(mock_data.keys())
            }, 404)
    
    def focus_expectation(self, indicator, params):
        year = params.get('year', ['2026'])[0]
        metric = params.get('metric', ['mediana'])[0]
        
        mock_data = {
            "IPCA": {"valor": 3.8, "ano": year, "metrica": metric},
            "Selic": {"valor": 9.5, "ano": year, "metrica": metric},
            "PIB Total": {"valor": 2.1, "ano": year, "metrica": metric},
            "Taxa de câmbio": {"valor": 5.20, "ano": year, "metrica": metric}
        }
        
        if indicator in mock_data:
            data = mock_data[indicator]
            data["indicador"] = indicator
            data["fonte"] = "BCB Focus"
            data["data_consulta"] = datetime.now().isoformat()
            data["demo"] = True
            self.send_json_response(data)
        else:
            self.send_json_response({
                "erro": f"Expectativa '{indicator}' não encontrada",
                "indicadores_disponiveis": list(mock_data.keys())
            }, 404)
    
    def b3_quote(self, ticker, params):
        field = params.get('field', ['preco'])[0]
        
        # Mock stock data
        mock_prices = {
            "PETR4": 32.45,
            "VALE3": 62.18,
            "ITUB4": 28.90,
            "BBDC4": 15.67,
            "ABEV3": 11.23,
            "WEGE3": 45.78,
            "HGLG11": 165.50,  # FII
            "BOVA11": 118.30   # ETF
        }
        
        if ticker.upper() in mock_prices:
            base_price = mock_prices[ticker.upper()]
            variation = round(random.uniform(-3, 3), 2)
            
            data = {
                "ticker": ticker.upper(),
                "preco": base_price,
                "variacao": variation,
                "fechamento_anterior": round(base_price * (1 - variation/100), 2),
                "volume": random.randint(1000000, 50000000),
                "maxima": round(base_price * 1.02, 2),
                "minima": round(base_price * 0.98, 2),
                "data": datetime.now().date().isoformat(),
                "hora": datetime.now().time().strftime("%H:%M:%S"),
                "fonte": "Yahoo Finance",
                "demo": True
            }
            
            if field in data:
                response = {"valor": data[field], **data}
                self.send_json_response(response)
            else:
                self.send_json_response(data)
        else:
            self.send_json_response({
                "erro": f"Ticker '{ticker}' não encontrado",
                "tickers_disponiveis": list(mock_prices.keys())
            }, 404)
    
    def tesouro_bond(self, title, params):
        field = params.get('field', ['taxa'])[0]
        
        mock_bonds = {
            "IPCA+ 2035": {"taxa": 6.12, "taxa_venda": 6.15, "preco": 3245.67, "preco_venda": 3250.00},
            "Prefixado 2029": {"taxa": 10.85, "taxa_venda": 10.88, "preco": 875.45, "preco_venda": 880.00},
            "Selic 2029": {"taxa": 0.02, "taxa_venda": 0.03, "preco": 14650.30, "preco_venda": 14700.00},
            "IPCA+ 2040": {"taxa": 6.25, "taxa_venda": 6.28, "preco": 2890.12, "preco_venda": 2895.00}
        }
        
        if title in mock_bonds:
            data = mock_bonds[title]
            data.update({
                "titulo": title,
                "data_vencimento": "2035-05-15" if "2035" in title else "2029-01-01",
                "tipo": "IPCA+" if "IPCA+" in title else ("Prefixado" if "Prefixado" in title else "Selic"),
                "data": datetime.now().date().isoformat(),
                "fonte": "Tesouro Direto",
                "demo": True
            })
            
            if field in data:
                response = {"valor": data[field], **data}
                self.send_json_response(response)
            else:
                self.send_json_response(data)
        else:
            self.send_json_response({
                "erro": f"Título '{title}' não encontrado",
                "titulos_disponiveis": list(mock_bonds.keys())
            }, 404)
    
    def list_indicators(self):
        data = {
            "bcb_sgs": {
                "indicators": ["selic", "ipca", "cdi", "dolar", "euro", "igpm", "ibc_br", "desemprego"]
            },
            "bcb_focus": {
                "indicators": ["IPCA", "Selic", "PIB Total", "Taxa de câmbio"]
            },
            "b3": {
                "sample_tickers": ["PETR4", "VALE3", "ITUB4", "HGLG11", "BOVA11"]
            },
            "tesouro": {
                "bonds": ["IPCA+ 2035", "Prefixado 2029", "Selic 2029", "IPCA+ 2040"]
            },
            "demo": True,
            "timestamp": datetime.now().isoformat()
        }
        self.send_json_response(data)
    
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

def run_server(port=8000):
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, BrazilFinanceHandler)
    print(f"🚀 BrazilFinance Demo API iniciada em http://0.0.0.0:{port}")
    print(f"📖 Health check: http://localhost:{port}/v1/health")
    print(f"📊 Exemplo BCB: http://localhost:{port}/v1/bcb/selic")
    print(f"🔮 Exemplo Focus: http://localhost:{port}/v1/focus/IPCA?year=2026")
    print(f"📈 Exemplo B3: http://localhost:{port}/v1/b3/PETR4")
    print(f"🏛️ Exemplo Tesouro: http://localhost:{port}/v1/tesouro/IPCA%2B%202035")
    print("=" * 60)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor encerrado")
        httpd.shutdown()

if __name__ == "__main__":
    run_server(8001)