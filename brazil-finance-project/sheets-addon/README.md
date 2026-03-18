# BrazilFinance Sheets - Google Sheets Add-on

Google Sheets Add-on que permite buscar dados financeiros brasileiros com fórmulas simples.

## Fórmulas Disponíveis

### 📊 Indicadores Macro (BCB)

```excel
=BCB("selic")                    // Taxa Selic atual
=BCB("ipca")                     // IPCA mensal atual  
=BCB("ipca", "12m")              // IPCA últimos 12 meses
=BCB("dolar")                    // Cotação USD/BRL atual
=BCB("cdi")                      // CDI atual
=BCB("igpm")                     // IGP-M mensal
=BCB("ibc_br")                   // IBC-Br (proxy PIB)
=BCB("desemprego")               // Taxa de desemprego
```

### 🔮 Expectativas de Mercado (Focus)

```excel
=FOCUS("IPCA", 2026)             // Expectativa IPCA 2026
=FOCUS("Selic", 2025)            // Expectativa Selic 2025
=FOCUS("PIB Total", 2026)        // Expectativa PIB 2026
=FOCUS("Taxa de câmbio", 2026)   // Expectativa USD/BRL 2026
=FOCUS("IPCA", 2025, "media")    // IPCA 2025 (média vs mediana)
```

### 📈 Cotações B3 (Ações, FIIs, ETFs)

```excel
=B3("PETR4")                     // Preço PETR4 atual
=B3("VALE3", "variacao")         // Variação % VALE3
=B3("HGLG11")                    // Cotação FII HGLG11
=B3("BOVA11", "volume")          // Volume BOVA11
=B3("ITUB4", "maxima")           // Máxima do dia ITUB4
=B3("WEGE3", "fechamento_anterior") // Fechamento anterior
```

### 🏛️ Tesouro Direto

```excel
=TESOURO("IPCA+ 2035")           // Taxa IPCA+ 2035
=TESOURO("Prefixado 2029", "taxa") // Taxa Prefixado 2029
=TESOURO("Selic 2029", "preco")  // Preço Selic 2029
=TESOURO("IPCA+ 2040", "taxa_venda") // Taxa de venda
```

### 🔧 Funções Auxiliares

```excel
=B3_MULTIPLOS("PETR4,VALE3,ITUB4")     // Múltiplas cotações
=FOCUS_RESUMO(2026)                     // Resumo expectativas 2026
=TESOURO_CURVA("IPCA+")                 // Curva de juros IPCA+
```

## Exemplos Práticos

### Dashboard Macro Brasil
| Indicador | Atual | Expectativa 2026 |
|-----------|-------|------------------|
| Selic | `=BCB("selic")` | `=FOCUS("Selic", 2026)` |
| IPCA | `=BCB("ipca")` | `=FOCUS("IPCA", 2026)` |
| PIB | `=BCB("ibc_br")` | `=FOCUS("PIB Total", 2026)` |
| Dólar | `=BCB("dolar")` | `=FOCUS("Taxa de câmbio", 2026)` |

### Portfolio Tracking
| Ticker | Preço | Variação % | Volume |
|--------|-------|------------|--------|
| PETR4 | `=B3("PETR4")` | `=B3("PETR4", "variacao")` | `=B3("PETR4", "volume")` |
| VALE3 | `=B3("VALE3")` | `=B3("VALE3", "variacao")` | `=B3("VALE3", "volume")` |
| HGLG11 | `=B3("HGLG11")` | `=B3("HGLG11", "variacao")` | `=B3("HGLG11", "volume")` |

### Análise Tesouro Direto
| Título | Taxa Compra | Taxa Venda | Preço |
|--------|-------------|------------|-------|
| IPCA+ 2035 | `=TESOURO("IPCA+ 2035", "taxa")` | `=TESOURO("IPCA+ 2035", "taxa_venda")` | `=TESOURO("IPCA+ 2035", "preco")` |
| Prefixado 2029 | `=TESOURO("Prefixado 2029", "taxa")` | `=TESOURO("Prefixado 2029", "taxa_venda")` | `=TESOURO("Prefixado 2029", "preco")` |

## Instalação

### Método 1: Google Workspace Marketplace (Quando Publicado)
1. Abrir Google Sheets
2. Extensions → Add-ons → Get add-ons
3. Buscar "BrazilFinance"
4. Instalar

### Método 2: Google Apps Script (Desenvolvimento)
1. Abrir Google Sheets
2. Extensions → Apps Script
3. Copiar código de `Code.js`
4. Salvar e autorizar permissões
5. Voltar ao Sheets e usar as fórmulas

## Configuração

### API Key (Opcional para Free Tier)
```javascript
// No Google Apps Script, executar uma vez:
setUserApiKey("sua-api-key-aqui");

// Para limpar:
clearUserApiKey();
```

### Teste de Conectividade
```javascript
// No Google Apps Script, executar:
testarConectividade();
```

## Planos e Limites

### 🆓 Free Tier
- **500 requests/dia**
- Indicadores básicos BCB
- Cotações B3 principais
- Cache de 5-30 minutos

### 💎 Pro Tier (R$ 39/mês)
- **10.000 requests/dia**
- Todos os indicadores
- Expectativas Focus completas
- Tesouro Direto
- Cache otimizado
- Suporte prioritário

### 🏢 Team Tier (R$ 149/mês)
- **50.000 requests/dia**
- API key dedicada
- SLA 99.9%
- Suporte 24/7
- Custom functions sob demanda

## Troubleshooting

### Erros Comuns

**❌ "Limite de requests atingido"**
- Solução: Upgrade para Pro ou aguardar reset diário

**❌ "API key inválida"**  
- Verificar: `getUserApiKey()` retorna key válida
- Reconfigurar: `setUserApiKey("nova-key")`

**❌ "Erro HTTP 500"**
- Problema temporário da API
- Aguardar alguns minutos e tentar novamente

**❌ "Ticker não encontrado"**
- Verificar ticker na B3 (ex: PETR4, não PETR)
- Tentar outros campos: "preco", "variacao"

### Funções de Diagnóstico

```javascript
// Testar API
testarConectividade();

// Limpar cache  
limparCache();

// Listar indicadores disponíveis
listarIndicadores();
```

### Performance

- **Cache automático**: Dados ficam em cache por 5min-2h dependendo do tipo
- **Rate limiting**: Requests são limitados por tier
- **Timeout**: Requests falham após 30s (Google Sheets limit)

## Desenvolvimento

### Setup Local (Google Apps Script)

```bash
# Instalar clasp (CLI do Apps Script)
npm install -g @google/clasp

# Login
clasp login

# Clone do projeto
clasp clone <script-id>

# Deploy
clasp push
```

### Estrutura do Código

```
sheets-addon/
├── appsscript.json     # Manifest do add-on
├── Code.js            # Funções principais + custom functions  
├── API.js             # Comunicação com backend
├── Menu.js            # Menu personalizado
├── Auth.js            # Gerenciamento API keys
└── README.md          # Esta documentação
```

### Customização

Para adicionar nova função:

1. **Backend**: Implementar endpoint na API
2. **Frontend**: Criar custom function em `Code.js`
3. **Teste**: Verificar em planilha real
4. **Documentação**: Atualizar este README

## Roadmap

- [ ] **Crypto integration** (`=CRYPTO("BTC", "BRL")`)
- [ ] **Commodities** (`=COMMODITIES("petroleo")`)
- [ ] **CVM Fundos** (`=FUNDOS("cnpj", "cota")`)
- [ ] **Historical data** (`=BCB("selic", "2020-01-01:2025-12-31")`)
- [ ] **Charts helpers** (integração com Google Charts)
- [ ] **Real-time updates** (WebSocket feeds)

## Suporte

- **Documentação**: [docs.brazilfinance.com.br](https://docs.brazilfinance.com.br)
- **Email**: suporte@brazilfinance.com.br  
- **Discord**: [Comunidade BrazilFinance](https://discord.gg/brazilfinance)

## Licença

MIT License - Ver arquivo LICENSE