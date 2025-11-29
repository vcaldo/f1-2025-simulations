# 🏁 Cenários de Empate - Documentação Técnica

Este documento detalha o cenário de **empate de pontos** entre os líderes do campeonato de F1 2025 antes da última corrida.

---

## 📋 Contexto do Problema

### Classificação Atual (antes da penúltima etapa)

| Piloto         | Pontos | Diferença para Líder |
|----------------|-------:|---------------------:|
| L. Norris      |    390 |                    — |
| O. Piastri     |    366 |                  -24 |
| M. Verstappen  |    366 |                  -24 |

### Estrutura da Penúltima Etapa (Qatar)

| Evento  | Posições que Pontuam | Pontos (1º lugar) |
|---------|:--------------------:|:-----------------:|
| Sprint  | 1º a 8º              | 8 pts             |
| Corrida | 1º a 10º             | 25 pts            |

**Máximo por piloto:** 33 pontos (8 + 25)

---

## 🔢 Matemática do Problema

### Condições para Empate

Seja $G_i$ os pontos ganhos pelo piloto $i$ na etapa (sprint + corrida):

**Empate Norris-Piastri:**

$$
390 + G_{\text{Norris}} = 366 + G_{\text{Piastri}}
$$

$$
G_{\text{Piastri}} - G_{\text{Norris}} = 24
$$

> Piastri precisa ganhar **exatamente 24 pontos a mais** que Norris.

**Empate Norris-Verstappen:**

$$
G_{\text{Verstappen}} - G_{\text{Norris}} = 24
$$

**Empate Piastri-Verstappen:**

$$
G_{\text{Piastri}} = G_{\text{Verstappen}}
$$

Como ambos partem com 366 pontos, basta ganharem a mesma quantidade.

**Empate Triplo:**

$$
G_{\text{Piastri}} - G_{\text{Norris}} = 24 \quad \text{e} \quad G_{\text{Verstappen}} - G_{\text{Norris}} = 24
$$

### Análise de Viabilidade

A diferença máxima possível de pontos ganhos é:

$$
\Delta G_{\max} = 33 - 0 = 33 \text{ pontos}
$$

Como a diferença necessária é 24 pontos e $24 \leq 33$, o empate é **matematicamente possível**.

Exemplos de combinações onde Piastri ganha 24 pts a mais que Norris:

| $G_{\text{Norris}}$ | $G_{\text{Piastri}}$ | Diferença |
|--------------------:|---------------------:|:---------:|
| 0                   | 24                   | ✅ 24      |
| 1                   | 25                   | ✅ 24      |
| 8                   | 32                   | ✅ 24      |
| 9                   | 33                   | ✅ 24      |

---

## 📐 Contagem Combinatória

### Espaço Amostral Bruto

Para a sprint, cada piloto pode terminar em 9 posições (1º-8º ou fora):

$$
\text{Combinações sprint} = 9^3 = 729
$$

Para a corrida, cada piloto pode terminar em 11 posições (1º-10º ou fora):

$$
\text{Combinações corrida} = 11^3 = 1.331
$$

**Total bruto:**

$$
729 \times 1.331 = 970.299 \text{ combinações}
$$

### Restrição de Posições Únicas

Dois pilotos **não podem ocupar a mesma posição pontuada**. O número de combinações válidas para 3 pilotos em $n$ posições pontuadas + 1 posição "fora" é:

$$
\text{Válidas} = P(n,3) + 3 \cdot P(n,2) + 3 \cdot n + 1
$$

Onde $P(n,k) = \frac{n!}{(n-k)!}$ é o número de permutações.

**Para sprint ($n=8$):**

$$
P(8,3) + 3 \cdot P(8,2) + 3 \cdot 8 + 1 = 336 + 168 + 24 + 1 = 529
$$

**Para corrida ($n=10$):**

$$
P(10,3) + 3 \cdot P(10,2) + 3 \cdot 10 + 1 = 720 + 270 + 30 + 1 = 1.021
$$

**Total de combinações válidas:**

$$
529 \times 1.021 = 540.109 \text{ combinações}
$$

Destas, **4.666 resultam em empate** (≈ 0,86%).

---

## 📊 Resultados

```
Total de cenários: 4.666
  - Empates triplos (3 pilotos): 8
  - Empates duplos (2 pilotos): 4.658

Empates duplos por combinação:
  - Norris & Piastri: 2.326 cenários
  - Norris & Verstappen: 2.326 cenários
  - Piastri & Verstappen: 6 cenários

Range de pontuação no empate: 390 - 399 pts
```

### Interpretação

1. **Empate triplo é raro:** Apenas 8 cenários onde os 3 empatam
2. **Piastri vs Verstappen empatando sem Norris é muito difícil:** Apenas 6 cenários — exige que Norris perca muitos pontos enquanto os outros dois ganham exatamente a mesma quantidade
3. **Range 390-399:** O empate ocorre entre 390 pts (Norris não pontua) e 399 pts

---

## 🏗️ Detalhes de Implementação

### Constantes de Pontuação

```python
PONTOS_SPRINT = {1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1, 99: 0}
PONTOS_CORRIDA = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1, 99: 0}
```

- **Posição 99** = fora dos pontos (DNF, abandono, ou posição 11º+)

### Validação de Posições

```python
def posicoes_validas(pos1: int, pos2: int, pos3: int) -> bool:
    """
    Verifica se a combinação de posições é válida.
    Dois pilotos não podem ocupar a mesma posição pontuada.
    Posição 99 (fora dos pontos) pode ser compartilhada.
    """
    posicoes = [pos1, pos2, pos3]
    posicoes_pontuadas = [p for p in posicoes if p != 99]
    return len(posicoes_pontuadas) == len(set(posicoes_pontuadas))
```

### Fluxo de Simulação

1. **Gerar combinações** via `itertools.product` (produto cartesiano)
2. **Filtrar posições inválidas** (dois pilotos na mesma posição)
3. **Calcular pontos finais** para cada cenário
4. **Identificar empates** no topo da classificação
5. **Exportar** para DuckDB e CSV

---

## 📈 Dashboard

### Estrutura

```
┌─────────────────────────────────────────────────────────────┐
│  🏎️ F1 2025 - Simulador de Cenários de Empate              │
├─────────────┬───────────────────────────────────────────────┤
│  🔍 Filtros │  👤 Cards dos Pilotos                         │
│  (Sidebar)  │                                               │
│             │  📊 Métricas Resumo                           │
│  • Tipo     │  (Total, Triplos, Duplos, Range)             │
│  • Pilotos  │                                               │
│  • Pontos   │  📈 Visualizações (4 abas)                   │
│             │  📋 Tabela de Cenários                        │
└─────────────┴───────────────────────────────────────────────┘
```

### Filtros Disponíveis

| Filtro | Opções |
|--------|--------|
| Tipo de Empate | Todos, Duplo, Triplo |
| Pilotos Empatados | Todas as combinações |
| Faixa de Pontos | Slider 390-399 |

### Visualizações

#### 📊 Por Combinação (Barras)
Quantidade de cenários para cada combinação de pilotos empatados.

#### 🎯 Hierarquia (Sunburst)
Gráfico em camadas: Tipo → Pilotos → Faixa de Pontos.

#### 🔥 Heatmaps
Mapa de calor mostrando frequência de empate por posição Sprint × Corrida para cada piloto.

**Interpretação:**
- **Norris (líder):** células escuras em posições ruins = ele precisa "perder" para empatar
- **Piastri/Verstappen:** células escuras em posições boas = precisam ganhar muitos pontos

#### 📦 Pontos Ganhos (Box Plot)
Distribuição dos pontos ganhos na etapa para cada piloto nos cenários de empate.

---

## 🎨 Paleta de Cores

| Elemento | Cor | Hex |
|----------|-----|-----|
| Norris | 🟠 Laranja | `#FFB347` |
| Piastri | 🔵 Azul | `#87CEEB` |
| Verstappen | 🟣 Lavanda | `#DDA0DD` |
| Destaque | 🟢 Verde | `#98D8C8` |
