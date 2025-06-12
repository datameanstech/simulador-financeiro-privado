# 🚀 **GUIA DE DEPLOY - Simulador Financeiro**

## 📋 **Pré-requisitos**
- Conta no GitHub
- Arquivo `dados_grandes_litigantes.parquet` (237MB)
- Python 3.10+

---

## 🎯 **OPÇÃO 1: Render.com (RECOMENDADO)**

### ✅ **Vantagens:**
- ✅ **Gratuito** até 750h/mês
- ✅ Deploy automático via GitHub
- ✅ Suporta arquivos grandes
- ✅ HTTPS automático
- ✅ Hibernação automática (economiza recursos)

### 📝 **Passos:**

1. **Criar conta**: https://render.com
2. **Conectar GitHub** e selecionar seu repositório
3. **Configurar serviço:**
   - **Name**: `simulador-financeiro`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Instance Type**: `Free` (ou `Starter $7/mês` para melhor performance)

4. **Variáveis de ambiente:**
   ```
   SECRET_KEY=pdpj2024-simulador-secreto-render
   PYTHON_VERSION=3.10.0
   ```

5. **Deploy automático!** ⚡

---

## 🚄 **OPÇÃO 2: Railway.app**

### ✅ **Vantagens:**
- ✅ **$5 grátis/mês**
- ✅ Deploy super rápido
- ✅ Interface linda
- ✅ Logs em tempo real

### 📝 **Passos:**

1. **Criar conta**: https://railway.app
2. **Deploy from GitHub**
3. **Selecionar repositório**
4. **Configurações automáticas** (Railway detecta Flask automaticamente)
5. **Adicionar variáveis:**
   ```
   SECRET_KEY=pdpj2024-simulador-secreto-railway
   ```

---

## 🎨 **OPÇÃO 3: Heroku**

### ✅ **Vantagens:**
- ✅ Plataforma clássica e confiável
- ✅ Eco Dynos ($7/mês)
- ✅ Add-ons para PostgreSQL, Redis, etc.

### 📝 **Passos:**

1. **Instalar Heroku CLI**
2. **Login**: `heroku login`
3. **Criar app**: `heroku create simulador-financeiro-2024`
4. **Configurar variáveis:**
   ```bash
   heroku config:set SECRET_KEY=pdpj2024-simulador-secreto-heroku
   ```
5. **Deploy:**
   ```bash
   git push heroku main
   ```

---

## ☁️ **OPÇÃO 4: Vercel (Para apps menores)**

### ⚠️ **Limitações:**
- ❌ Limite de 250MB (nosso arquivo é 237MB)
- ⚠️ Melhor para apps menores

### 📝 **Passos:**
1. **Criar conta**: https://vercel.com
2. **Import Git Repository**
3. **Framework Preset**: `Other`
4. **Build Command**: `pip install -r requirements.txt`
5. **Output Directory**: deixar vazio

---

## 🐳 **OPÇÃO 5: DigitalOcean App Platform**

### ✅ **Vantagens:**
- ✅ **$5/mês** para apps básicos
- ✅ Muito confiável
- ✅ Boa para produção

### 📝 **Passos:**
1. **Criar conta DigitalOcean**
2. **App Platform > Create App**
3. **Connect GitHub**
4. **Configure:**
   - **Source**: GitHub repository
   - **Branch**: main
   - **Autodeploy**: ✅

---

## 🎯 **RECOMENDAÇÃO FINAL**

### **Para Teste/Demo:**
🥇 **Render.com** (gratuito, fácil, confiável)

### **Para Produção:**
🥇 **Railway.app** ($5-15/mês, performance excelente)
🥈 **DigitalOcean** ($5-25/mês, muito estável)

---

## 🔧 **Configurações Importantes**

### **Arquivo grande (237MB)**
- ✅ **Git LFS** para versionar arquivo grande
- ✅ **Render/Railway** suportam bem
- ❌ **Vercel/Netlify** podem ter problemas

### **Variáveis de ambiente essenciais:**
```env
SECRET_KEY=sua-chave-secreta-segura
PORT=5000
FLASK_ENV=production
```

### **Performance:**
- **Free tier**: OK para testes/demo
- **$5-7/mês**: Adequado para uso real
- **$15+/mês**: Performance profissional

---

## 🚀 **Deploy em 1 Minuto (Render.com)**

1. **Fork** este repositório
2. Acesse: https://render.com
3. **"New" > "Web Service"**
4. **Connect GitHub** → Selecionar repo
5. **Deploy!** ⚡

✅ **Pronto!** Sua aplicação estará online em ~3-5 minutos

---

## 📞 **Suporte**

Se precisar de ajuda com o deploy:
- 📧 **Issues no GitHub**
- 💬 **Documentação da plataforma escolhida**

**🎉 Boa sorte com o deploy!** 