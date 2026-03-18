# 🚀 BRAZIL FINANCE - DEPLOY INSTRUCTIONS

**Status:** ✅ Projeto pronto para deploy  
**GitHub:** https://github.com/tiagoclaw/openclaw-brain  
**Pasta:** `brazil-finance-project/`  

---

## 📋 DEPLOY RÁPIDO (5 MINUTOS)

### 🌐 1. Landing Page (VERCEL - Grátis)

```bash
# 1. Instalar Vercel CLI
npm install -g vercel

# 2. Deploy direto da pasta
cd brazil-finance-project/landing-page/
vercel --prod

# 3. Seu link será: https://brazil-finance-xxx.vercel.app
```

**Alternativa Netlify:**
```bash
# Drag & drop da pasta landing-page/ em netlify.com/drop
# Link gerado em segundos!
```

### 🚀 2. Backend API (RAILWAY - Grátis)

```bash
# 1. Conectar GitHub ao Railway
# Visitar: railway.app → "Deploy from GitHub"
# Selecionar: tiagoclaw/openclaw-brain
# Pasta: brazil-finance-project/backend/

# 2. Variáveis de ambiente (automáticas via Dockerfile)
# 3. Deploy automático em ~2 minutos
# 4. Seu link será: https://brazil-finance-xxx.railway.app
```

**Alternativa Render:**
```bash
# 1. Visitar render.com → "New Web Service" 
# 2. Conectar GitHub repo: tiagoclaw/openclaw-brain
# 3. Build Command: cd brazil-finance-project/backend && pip install -r requirements.txt
# 4. Start Command: python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
# 5. Deploy em ~3 minutos
```

---

## 🔗 LINKS DE DEMONSTRAÇÃO

### Landing Page Local (Rodando agora):
```
http://localhost:8080
```

### API Endpoints de Demonstração:
```bash
# Health check
curl http://localhost:8000/v1/health

# BCB Indicators  
curl http://localhost:8000/v1/bcb/selic
curl http://localhost:8000/v1/bcb/ipca
curl http://localhost:8000/v1/bcb/dolar

# Focus Expectations
curl http://localhost:8000/v1/focus/IPCA?year=2026
curl http://localhost:8000/v1/focus/Selic?year=2026

# B3 Quotes
curl http://localhost:8000/v1/b3/PETR4
curl http://localhost:8000/v1/b3/VALE3?field=variacao

# Tesouro Bonds
curl "http://localhost:8000/v1/tesouro/IPCA%2B%202035"

# List all indicators
curl http://localhost:8000/v1/indicators
```

---

## 📊 FÓRMULAS GOOGLE SHEETS

### Após deploy da API, usar no Google Sheets:

```javascript
// No Google Apps Script (sheets-addon/Code.js)
// Trocar API_BASE_URL para sua URL do Railway/Render:

var API_BASE_URL = "https://brazil-finance-xxx.railway.app/v1";

// Depois disso, as fórmulas funcionarão:
=BCB("selic")                    // → 10.75
=FOCUS("IPCA", 2026)            // → 3.8  
=B3("PETR4")                    // → R$ 32.45
=TESOURO("IPCA+ 2035")          // → 6.12%
```

---

## 🎯 DEPLOY PROFISSIONAL (Domínio Próprio)

### Domínio: brazilfinance.com.br

```bash
# 1. Registrar domínio (Registro.br ou Hostinger)
# 2. Configurar DNS:
#    - A record: @ → IP do Railway/Render  
#    - CNAME: www → brazilfinance.com.br
#    - CNAME: api → railway-app-url.railway.app

# 3. URLs finais:
#    - https://brazilfinance.com.br (Landing)
#    - https://api.brazilfinance.com.br (Backend)
#    - https://docs.brazilfinance.com.br (Documentação)
```

---

## 🔧 GOOGLE SHEETS ADD-ON

### Publicação no Marketplace:

```bash
# 1. Criar projeto Google Apps Script
# 2. Copiar arquivos de sheets-addon/:
#    - Code.js (custom functions)
#    - Menu.js (interface)  
#    - Sidebar.html (UI)
#    - appsscript.json (manifest)

# 3. Configurar OAuth scopes
# 4. Submeter para review Google (5-14 dias)
# 5. Publicar no Google Workspace Marketplace
```

**Instalação manual (imediata):**
1. Abrir Google Sheets
2. Extensions → Apps Script
3. Colar código de `sheets-addon/Code.js`
4. Salvar e autorizar
5. Voltar ao Sheets e usar: `=BCB("selic")`

---

## 📱 TESTE RÁPIDO AGORA

### Landing Page (rodando localmente):
```
Servidor iniciado em: http://localhost:8080
- Design responsivo ✅
- Seções: Hero + Features + Pricing ✅  
- Mobile-friendly ✅
- Ready para deploy ✅
```

### Como testar:
1. Abra http://localhost:8080 no navegador
2. Veja o design profissional
3. Fórmulas de demonstração funcionais
4. Layout responsivo (teste no mobile)

---

## 💰 MONETIZAÇÃO

### Stripe Integration:
```bash
# 1. Criar conta Stripe
# 2. Configurar produtos:
#    - Pro: R$ 39/mês (10K requests)
#    - Team: R$ 149/mês (50K requests)
# 3. Webhook para ativar API keys
# 4. Dashboard para usage tracking
```

---

## 📈 CRESCIMENTO

### Semana 1-2: MVP
- ✅ Deploy backend + landing
- ✅ 50 beta users (economistas)
- ✅ Feedback collection

### Semana 3-4: Launch
- ✅ Google Marketplace submission  
- ✅ Twitter/LinkedIn launch
- ✅ Content marketing

### Mês 2-3: Scale
- ✅ Partnerships (gestoras, fintechs)
- ✅ SEO content
- ✅ Feature expansion (crypto, fundos)

---

## 🏆 STATUS ATUAL

```
✅ Código completo (27 arquivos)
✅ Documentação profissional  
✅ Testes automatizados
✅ Deploy configs prontos
✅ Landing page responsiva
✅ Google Sheets add-on funcional
✅ Modelo de negócio estruturado
✅ Roadmap de crescimento

🚀 READY FOR LAUNCH!
```

---

## 🔥 DEPLOY EM 1 COMANDO

```bash
# Clone do repositório
git clone https://github.com/tiagoclaw/openclaw-brain.git
cd openclaw-brain/brazil-finance-project/

# Deploy landing (Vercel)
cd landing-page && vercel --prod

# Deploy backend (Railway)  
# Conectar GitHub no railway.app

# Pronto! 🎉
```

**Estimativa:** 5-10 minutos do zero ao ar

**Custo:** R$ 0 (free tiers Railway + Vercel)

**ROI:** Potencial 6-7 dígitos em 2-3 anos 🚀