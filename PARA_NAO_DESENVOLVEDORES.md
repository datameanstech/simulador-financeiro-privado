# 🎯 GUIA PARA NÃO-DESENVOLVEDORES

## 📋 Você tem 3 opções SIMPLES para usar o simulador:

---

## 🌐 **OPÇÃO 1: STREAMLIT (MAIS FÁCIL)**

### ✅ Vantagens:
- Interface web bonita e simples
- Apenas clique em botões
- Não precisa instalar nada

### 📍 Como usar:
1. **Digite na barra do navegador:** `simulatorleadsdm.streamlit.app`
2. **Digite a senha:** `pdpj2024`
3. **Escolha o tamanho da análise** (Rápido/Completo/Máximo)
4. **Aguarde carregar** os dados
5. **Veja os resultados** automaticamente

### ⚠️ Limitação:
- Para volumes muito grandes (14M+ registros), pode ser lento
- Recomendado usar modo "Rápido" ou "Completo"

---

## 📓 **OPÇÃO 2: GOOGLE COLAB (RECOMENDADO PARA ANÁLISES COMPLETAS)**

### ✅ Vantagens:
- Processa TODOS os 14+ milhões de registros
- Gratuito
- Roda no navegador
- Gráficos interativos

### 📍 Como usar:
1. **Abra o link:** [Google Colab - Simulador](https://colab.research.google.com/github/datameanstech/simulador-financeiro-privado/blob/main/simulador_colab.ipynb)
2. **Clique na seta ▶️** ao lado de cada código
3. **Aguarde processar** (vai aparecendo o progresso)
4. **Vá para o próximo código** quando aparecer "✅ PRONTO"

### 📝 Passo a passo detalhado:
```
PASSO 1: Clique na seta do código "Instalar bibliotecas" ▶️
         Aguarde 2-3 minutos (aparece "✅ PRONTO")

PASSO 2: Clique na seta do código "Baixar dados" ▶️  
         Aguarde 5-10 minutos (baixa 14M+ registros)

PASSO 3: Clique na seta do código "Escolher quantos dados" ▶️
         Mude o OPCAO_ESCOLHIDA se quiser (1=Rápido, 2=Médio, 3=Todos)

PASSO 4: Clique nas análises que quiser ▶️
         - Ranking empresas
         - Simulação financeira  
         - Análise tribunais
         - Relatório completo
```

---

## 💻 **OPÇÃO 3: EXECUTÁVEL (PARA USO OFFLINE)**

### ✅ Vantagens:
- Funciona sem internet (depois do download inicial)
- Interface desktop simples
- Controle total dos dados

### 📍 Como usar:
1. **Baixe o arquivo:** `simulador_executavel.py`
2. **Clique duas vezes** no arquivo
3. **Use a interface gráfica:**
   - Botão verde "BAIXAR DADOS" 
   - Configure valores se quiser
   - Clique nas análises desejadas

### ⚙️ Se não funcionar:
```
1. Instale Python: https://python.org (baixe versão mais recente)
2. Ao instalar, marque "Add Python to PATH" 
3. Clique duas vezes no arquivo novamente
```

---

## 🎯 **QUAL ESCOLHER?**

### Para análise rápida e simples:
**→ Use OPÇÃO 1 (Streamlit)**

### Para análise completa com todos os dados:
**→ Use OPÇÃO 2 (Google Colab)**

### Para uso frequente ou offline:
**→ Use OPÇÃO 3 (Executável)**

---

## ❓ **DÚVIDAS COMUNS**

### **"Qual a diferença entre as opções?"**
- **Streamlit:** Mais simples, mas pode ser lento com muitos dados
- **Google Colab:** Mais poderoso, processa todos os dados
- **Executável:** Para quem quer usar offline

### **"Preciso saber programação?"**
- **NÃO!** Todas as opções são point-and-click
- Apenas clique nos botões e aguarde

### **"É seguro?"**
- **SIM!** Todos os dados ficam protegidos
- Senha necessária para acesso
- Código open-source no GitHub

### **"Quanto custa?"**
- **GRATUITO!** Todas as opções são 100% gratuitas

---

## 🚀 **COMECE AGORA**

### Recomendação para primeira vez:
1. **Teste o Streamlit:** `simulatorleadsdm.streamlit.app`
2. **Se gostar, use o Google Colab** para análises mais detalhadas
3. **Senha:** `pdpj2024`

### 📞 Precisa de ajuda?
- Todas as interfaces têm instruções step-by-step
- Mensagens claras de erro e progresso
- Botões grandes e intuitivos

---

## 📊 **O QUE VOCÊ VAI VER**

### Ranking das Empresas:
```
🏆 TOP 20 EMPRESAS - PROCESSOS NOVOS:
 1. CAIXA ECONÔMICA FEDERAL           |   45,234 processos
 2. BANCO DO BRASIL SA                |   38,567 processos  
 3. BANCO BRADESCO SA                 |   28,901 processos
```

### Simulação Financeira:
```
💰 POTENCIAL FINANCEIRO POR EMPRESA:
EMPRESA                    | PROCESSOS  | RECEITA MENSAL
BANCO DO BRASIL SA         |     38,567 |  R$   115,701
CAIXA ECONÔMICA FEDERAL    |     45,234 |  R$   135,702
```

### Análise por Tribunais:
```
⚖️ PROCESSOS POR TRIBUNAL:
TST                    |   234,567 ( 15.2%)
TRT01                  |   189,234 ( 12.3%)
TRT02                  |   156,789 ( 10.1%)
```

Todos os resultados aparecem de forma clara e organizada! 🎉 