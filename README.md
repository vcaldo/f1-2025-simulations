# 🏎️ Simulador F1 2025

Dashboard interativo para análise de cenários do campeonato de Fórmula 1 2025, com foco na disputa pelo título entre **Norris**, **Piastri** e **Verstappen**.

---

## 🚀 Como Rodar

### Com Docker (recomendado)

```bash
git clone https://github.com/vcaldo/f1-2025-simulations.git
cd f1-2025-simulations
docker-compose up --build
```

### Localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

📍 Acesse: [http://localhost:8501](http://localhost:8501)

---

## 📊 Dashboards

### 🏁 [Cenários de Empate para Última Etapa](docs/CENARIOS_EMPATE.md)

Análise dos **4.666 cenários** onde 2 ou 3 pilotos podem empatar em pontos antes da última corrida do campeonato.

- Simula resultados da penúltima etapa (Sprint + Corrida do Qatar)
- Identifica combinações de empate duplo e triplo
- Visualiza quais posições cada piloto precisa para empatar

**Funcionalidades:**
- 📋 **Tabela de Cenários** — Exibe resultados necessários em Sprint e Corrida para cada piloto
- 📊 **Gráfico por Combinação** — Distribuição dos cenários por tipo de empate
- 🎯 **Hierarquia Sunburst** — Visualização hierárquica dos pilotos empatados
- 🔥 **Heatmaps de Posições** — Mapa de calor mostrando frequência de posições por piloto
- 📦 **Pontos Ganhos** — Análise dos pontos conquistados em cada cenário

### 🏆 [Cenários de Campeão](docs/CENARIOS_CAMPEAO.md)

Análise de **~540 mil combinações** de resultados para determinar as chances de título de cada piloto.

- Simula 3 eventos restantes (Sprint Qatar, Corrida Qatar, Corrida Abu Dhabi)
- Calcula probabilidades de título por piloto
- Considera sistema de desempate da F1 (pontos → vitórias → 2º lugares → 3º lugares)

**Funcionalidades:**
- 🎯 **Como Cada Um Pode Ganhar** — Análise detalhada das combinações que levam cada piloto ao título
- 📊 **Gráficos de Chances** — Visualização das probabilidades de cada piloto
- 🏅 **Métodos de Decisão** — Mostra se o título foi decidido por pontos, vitórias ou desempate
- 📈 **Sunburst Campeão → Método** — Hierarquia visual de campeões e critérios de desempate
- 📦 **Boxplot de Pontos** — Distribuição de pontos finais por piloto
- 🎮 **Simulador "What If"** — Interativo para testar cenários customizados de resultados

---

## 🛠️ Tecnologias

- **Streamlit** — Interface do dashboard
- **Plotly** — Gráficos interativos
- **DuckDB** — Banco de dados analítico
- **Python 3.12** — Linguagem base

---

## 📁 Estrutura

```
├── app.py                    # Ponto de entrada
├── pages/                    # Páginas do dashboard
│   ├── 1_Cenarios_Empate.py
│   └── 2_Cenarios_Campeao.py
├── simulations/              # Lógica de simulação
│   ├── cenarios_empate/
│   └── cenarios_campeao/
├── data/                     # Banco DuckDB
└── docs/                     # Documentação detalhada
    ├── CENARIOS_EMPATE.md
    └── CENARIOS_CAMPEAO.md
```
