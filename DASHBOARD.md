# 📊 Guia do Dashboard F1 2025

Este documento explica o dashboard interativo de cenários de empate do campeonato de F1 2025 e cada uma de suas visualizações.

---

## 🏠 Visão Geral

O dashboard permite explorar os **4.666 cenários** onde 2 ou 3 pilotos terminam empatados em pontos após a penúltima etapa do campeonato (Sprint + Corrida).

### Estrutura do Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│  🏎️ F1 2025 - Simulador de Cenários de Empate              │
├─────────────┬─────────────┬─────────────────────────────────┤
│  🔍 Filtros │             │                                 │
│  (Sidebar)  │   Cards dos Pilotos (Norris, Piastri, Ver.)  │
│             ├─────────────┴─────────────────────────────────┤
│  • Tipo     │   📊 Métricas Resumo                          │
│  • Pilotos  │   (Total, Triplos, Duplos, Range)            │
│  • Pontos   ├─────────────────────────────────────────────────┤
│             │   📈 Visualizações (4 abas)                   │
│             │   • Por Combinação • Hierarquia               │
│             │   • Heatmaps      • Pontos Ganhos             │
│             ├─────────────────────────────────────────────────┤
│             │   📋 Tabela de Cenários                       │
└─────────────┴─────────────────────────────────────────────────┘
```

---

## 👤 Cards dos Pilotos

Exibe a **classificação atual** dos 3 pilotos na disputa pelo título:

| Piloto | Pontos | Cor |
|--------|-------:|-----|
| **L. Norris** | 390 | 🟠 Laranja pastel |
| **O. Piastri** | 366 | 🔵 Azul pastel |
| **M. Verstappen** | 366 | 🟣 Lavanda pastel |

Cada card mostra:
- Foto do piloto (PNG)
- Nome
- Pontuação atual antes da penúltima etapa

---

## 🔍 Filtros (Sidebar)

A sidebar à esquerda permite filtrar os cenários:

### Tipo de Empate
- **Todos** — Mostra empates duplos e triplos
- **duplo** — Apenas cenários onde 2 pilotos empatam
- **triplo** — Apenas cenários onde os 3 pilotos empatam (raro: apenas 8 cenários)

### Pilotos Empatados
- **Todas** — Todas as combinações
- **Norris & Piastri** — 2.326 cenários
- **Norris & Verstappen** — 2.326 cenários
- **Piastri & Verstappen** — 6 cenários (muito raro)
- **Norris & Piastri & Verstappen** — 8 cenários (empate triplo)

### Faixa de Pontos do Empate
Slider para filtrar por pontuação final do empate:
- **Mínimo:** 390 pts (Norris não pontua, outros não ganham diferença)
- **Máximo:** 399 pts (cenários de alta pontuação)

---

## 📊 Métricas Resumo

Quatro cards com estatísticas dos cenários **após aplicar os filtros**:

| Métrica | Descrição |
|---------|-----------|
| **Total de Cenários** | Quantidade de cenários que atendem aos filtros |
| **Empates Triplos** | Cenários onde os 3 pilotos empatam |
| **Empates Duplos** | Cenários onde apenas 2 pilotos empatam |
| **Range de Pontos** | Menor e maior pontuação de empate nos cenários filtrados |

---

## 📈 Visualizações

O dashboard possui 4 abas de visualização:

### 📊 Aba 1: Por Combinação

**Tipo:** Gráfico de barras

**O que mostra:** Quantidade de cenários para cada combinação de pilotos empatados.

**Insight principal:**
- Norris & Piastri e Norris & Verstappen têm a mesma quantidade de cenários (2.326 cada)
- Piastri & Verstappen empatando sem Norris é extremamente raro (6 cenários)
- Isso acontece porque Norris lidera com 24 pontos de vantagem

**Como interpretar:**
- Barras mais altas = combinação mais provável de ocorrer
- Use para entender quais empates são mais "fáceis" de acontecer matematicamente

---

### 🎯 Aba 2: Hierarquia (Sunburst)

**Tipo:** Gráfico Sunburst (pizza em camadas)

**O que mostra:** Hierarquia de 3 níveis:
1. **Centro:** Tipo de empate (duplo/triplo)
2. **Meio:** Combinação de pilotos
3. **Borda:** Faixa de pontuação (390-392, 393-395, 396-399, 400+)

**Insight principal:**
- Visualiza a proporção entre empates duplos (grande maioria) e triplos (fatia mínima)
- Mostra como os cenários se distribuem por faixa de pontos

**Como interpretar:**
- Clique em uma fatia para fazer zoom
- Fatias maiores = mais cenários naquela categoria
- Verde menta = empates triplos
- Laranja = empates duplos

---

### 🔥 Aba 3: Heatmaps

**Tipo:** Mapa de calor (matriz)

**O que mostra:** Frequência de cenários de empate para cada combinação de:
- **Eixo Y:** Posição na Sprint (1º a 8º, ou Fora)
- **Eixo X:** Posição na Corrida (1º a 10º, ou Fora)

**Seletor:** Escolha qual piloto analisar (Norris, Piastri ou Verstappen)

**Insight principal:**
- Células mais escuras = mais cenários de empate com aquela combinação de posições
- Revela quais resultados de corrida cada piloto precisa para gerar empate

**Como interpretar:**
- Para **Norris** (líder): células escuras em posições ruins (fora dos pontos) — ele precisa "perder" para empatar
- Para **Piastri/Verstappen**: células escuras em posições boas — eles precisam ganhar muitos pontos

**Exemplo:**
> Se o heatmap de Norris mostra cor intensa em Sprint="Fora" e Corrida="Fora", significa que muitos cenários de empate requerem que Norris não pontue em nenhuma das provas.

---

### 📦 Aba 4: Pontos Ganhos

**Tipo:** Box plot (diagrama de caixa)

**O que mostra:** Distribuição dos pontos ganhos na etapa (Sprint + Corrida) para cada piloto, considerando apenas os cenários de empate.

**Componentes do box plot:**
- **Caixa:** 50% dos cenários (quartis Q1 a Q3)
- **Linha central:** Mediana
- **Bigodes:** Valores típicos
- **Pontos:** Outliers

**Insight principal:**
- Compara quanto cada piloto precisa ganhar para que ocorra empate
- Norris tem mediana mais baixa (precisa ganhar menos ou perder pontos)
- Piastri e Verstappen têm medianas mais altas (precisam ganhar mais)

**Como interpretar:**
- Caixas mais altas = piloto precisa pontuar mais para empatar
- Sobreposição entre caixas = cenários onde ambos ganham quantidade similar

---

## 📋 Tabela de Cenários

Abaixo das visualizações, uma tabela interativa mostra os cenários detalhados:

| Coluna | Descrição |
|--------|-----------|
| `tipo_empate` | duplo ou triplo |
| `pilotos_empatados` | Quais pilotos empatam |
| `pontos_empate` | Pontuação final do empate |
| `sprint_*` | Posição de cada piloto na Sprint (1-8 ou 99=fora) |
| `corrida_*` | Posição de cada piloto na Corrida (1-10 ou 99=fora) |
| `pts_*` | Pontuação final de cada piloto |

**Limitação:** Exibe no máximo 100 linhas. Use os filtros para refinar a busca.

---

## 🎨 Paleta de Cores

O dashboard usa cores pastéis para facilitar a leitura:

| Elemento | Cor | Hex |
|----------|-----|-----|
| Norris | 🟠 Pêssego/Laranja | `#FFB347` |
| Piastri | 🔵 Azul céu | `#87CEEB` |
| Verstappen | 🟣 Lavanda | `#DDA0DD` |
| Destaque | 🟢 Verde menta | `#98D8C8` |
| Fundo | ⬜ Cinza claro | `#F5F5F5` |
| Texto | ⬛ Cinza escuro | `#4A4A4A` |

---

## 💡 Dicas de Uso

1. **Comece pelos filtros** — Reduza o escopo para análises específicas
2. **Use o heatmap para estratégia** — Entenda quais posições cada piloto precisa
3. **Explore o sunburst clicando** — Faça zoom em categorias específicas
4. **Exporte dados** — A tabela pode ser copiada para análise externa
5. **Compare pilotos** — Alterne entre pilotos no heatmap para comparar padrões

---

## 🔧 Tecnologias

- **Streamlit** — Framework do dashboard
- **Plotly** — Gráficos interativos
- **Pandas** — Manipulação de dados
- **Python 3.12** — Linguagem base
