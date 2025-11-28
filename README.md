# Simulador F1 2025 - Cenários de Empate (28/11/2025)

Este projeto calcula todas as combinações possíveis de resultados na **penúltima etapa** do campeonato de F1 2025 que resultariam em **empate de pontos** entre os líderes antes da última corrida.

## 🚀 Dashboard Interativo

Explore os cenários visualmente com o dashboard Streamlit:

### Rodar com Docker

```bash
# Clone o repositório
git clone https://github.com/vcaldo/f1-2025-simulations.git
# Acesse o diretório
cd f1-2025-simulations
# Build e run com docker-compose
docker-compose up --build
```
Acesse: [http://localhost:8501](http://localhost:8501)

### Rodar Localmente

```bash
# Instalar dependências
pip install -r requirements.txt

# Gerar/atualizar dados
python f1_simulator.py

# Iniciar dashboard
streamlit run app.py
```
Acesse: [http://localhost:8501](http://localhost:8501)

---

## 📋 Contexto do Problema

### Classificação Atual (antes da penúltima etapa)

| Piloto         | Pontos |
|----------------|-------:|
| L. Norris      |    390 |
| O. Piastri     |    366 |
| M. Verstappen  |    366 |

### Estrutura da Penúltima Etapa

A penúltima etapa inclui:
- **1 Sprint** (máximo 8 pontos para o vencedor)
- **1 Corrida Regular** (máximo 25 pontos para o vencedor)

**Total máximo por piloto:** 33 pontos

---

# TL;DR

## 📊 Resultados

Ao executar o script:

```
Total de cenários: 4666
  - Empates triplos (3 pilotos): 8
  - Empates duplos (2 pilotos): 4658

Empates duplos por combinação:
  - Norris & Piastri: 2326 cenários
  - Norris & Verstappen: 2326 cenários
  - Piastri & Verstappen: 6 cenários

Range de pontuação no empate: 390 - 399 pts
```

### Interpretação

1. **Empate triplo é raro:** Apenas 8 cenários onde os 3 empatam
2. **Piastri vs Verstappen empatando sem Norris é muito difícil:** Apenas 6 cenários, pois exige que Norris perca muitos pontos enquanto os outros dois ganham exatamente a mesma quantidade
3. **Range de 390-399:** O empate ocorre entre 390 pts (Norris não pontua, outros não ganham nada) e 399 pts

---

## 🔢 Matemática do Problema

### Diferença de Pontos Atual

Definimos a **diferença de pontos** ($\Delta$) de cada piloto em relação ao líder (Norris):

$$
\Delta_{\text{Piastri}} = 390 - 366 = 24 \text{ pontos}
$$

$$
\Delta_{\text{Verstappen}} = 390 - 366 = 24 \text{ pontos}
$$

### Condição para Empate

Para haver empate após a penúltima etapa, a pontuação final dos pilotos deve ser igual. Seja $G_i$ os pontos ganhos pelo piloto $i$ na etapa (sprint + corrida):

**Empate Norris-Piastri:**
$$
390 + G_{\text{Norris}} = 366 + G_{\text{Piastri}}
$$
$$
G_{\text{Piastri}} - G_{\text{Norris}} = 24
$$

Ou seja, **Piastri precisa ganhar exatamente 24 pontos a mais que Norris**.

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

### Limites de Pontuação na Etapa

Cada piloto pode ganhar entre 0 e 33 pontos:

| Evento  | Mínimo | Máximo |
|---------|-------:|-------:|
| Sprint  |      0 |      8 |
| Corrida |      0 |     25 |
| **Total** | **0** | **33** |

### Análise das Possibilidades

**Para Piastri/Verstappen empatarem com Norris:**

A diferença máxima possível de pontos ganhos é:
$$
\Delta G_{\max} = 33 - 0 = 33 \text{ pontos}
$$

Como a diferença necessária é 24 pontos, e $24 \leq 33$, **é matematicamente possível**.

Exemplos de combinações onde Piastri ganha 24 pts a mais que Norris:

| Cenário | $G_{\text{Norris}}$ | $G_{\text{Piastri}}$ | Diferença |
|---------|--------------------:|---------------------:|----------:|
| A       | 0                   | 24                   | 24 ✓      |
| B       | 1                   | 25                   | 24 ✓      |
| C       | 8                   | 32                   | 24 ✓      |
| D       | 9                   | 33                   | 24 ✓      |

**Para Piastri e Verstappen empatarem SEM Norris:**

Isso requer que ambos ganhem a mesma quantidade de pontos E que Norris fique à frente. Ou seja:
$$
G_{\text{Piastri}} = G_{\text{Verstappen}} \quad \text{e} \quad 390 + G_{\text{Norris}} > 366 + G_{\text{Piastri}}
$$
$$
G_{\text{Norris}} > G_{\text{Piastri}} - 24
$$

Isso é muito restritivo: Norris precisa pontuar o suficiente para ficar na frente, mas não tanto que impeça o empate entre os outros dois. Na prática, encontramos apenas **6 cenários** assim.

### Contagem Combinatória

**Espaço amostral bruto:**

Para a sprint, cada piloto pode terminar em 9 posições possíveis (1º-8º ou fora):
$$
\text{Combinações sprint} = 9^3 = 729
$$

Para a corrida, cada piloto pode terminar em 11 posições possíveis (1º-10º ou fora):
$$
\text{Combinações corrida} = 11^3 = 1331
$$

Total bruto:
$$
729 \times 1331 = 970.299 \text{ combinações}
$$

**Aplicando restrição de posições únicas:**

Dois pilotos não podem ocupar a mesma posição pontuada. O número de combinações válidas para 3 pilotos em $n$ posições pontuadas + 1 posição "fora" é:

$$
\text{Válidas} = P(n,3) + 3 \cdot P(n,2) + 3 \cdot n + 1
$$

Onde $P(n,k) = \frac{n!}{(n-k)!}$ é o número de permutações.

Para sprint ($n=8$):
$$
P(8,3) + 3 \cdot P(8,2) + 3 \cdot 8 + 1 = 336 + 168 + 24 + 1 = 529
$$

Para corrida ($n=10$):
$$
P(10,3) + 3 \cdot P(10,2) + 3 \cdot 10 + 1 = 720 + 270 + 30 + 1 = 1021
$$

Total de combinações válidas:
$$
529 \times 1021 = 540.109 \text{ combinações}
$$

Destas, **4.666 resultam em empate** (≈ 0,86% das combinações válidas).

---

## 🏗️ Estrutura do Script

### 1. Constantes de Pontuação

```python
PONTOS_SPRINT = {1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1, 99: 0}
PONTOS_CORRIDA = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1, 99: 0}
```

- Posições de 1º a 8º na sprint ganham pontos (8 a 1)
- Posições de 1º a 10º na corrida ganham pontos (25 a 1)
- **Posição 99** = fora dos pontos (DNF, abandono, ou posição 11º+)

### 2. Dados dos Pilotos

```python
PILOTOS = {
    'norris': {'nome': 'L. Norris', 'pontos': 390},
    'piastri': {'nome': 'O. Piastri', 'pontos': 366},
    'verstappen': {'nome': 'M. Verstappen', 'pontos': 366},
}
```

---

## 🔄 Fluxo de Execução

### Passo 1: Gerar Combinações de Posições

O script usa `itertools.product` para gerar o **produto cartesiano** de todas as posições possíveis:

```
Sprint:  [1, 2, 3, 4, 5, 6, 7, 8, 99] → 9 posições possíveis
Corrida: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 99] → 11 posições possíveis
```

Para cada evento (sprint e corrida), são geradas combinações para os 3 pilotos:
- Sprint: 9³ = 729 combinações brutas
- Corrida: 11³ = 1.331 combinações brutas
- **Total bruto:** 729 × 1.331 = **970.299 combinações**

### Passo 2: Filtrar Posições Válidas

A função `posicoes_validas()` remove combinações impossíveis:

```python
def posicoes_validas(pos1, pos2, pos3):
    posicoes = [pos1, pos2, pos3]
    posicoes_pontuadas = [p for p in posicoes if p != 99]
    return len(posicoes_pontuadas) == len(set(posicoes_pontuadas))
```

**Regra:** Dois pilotos **não podem ocupar a mesma posição pontuada** (1º-8º na sprint, 1º-10º na corrida). Porém, **múltiplos pilotos podem ficar fora dos pontos** (posição 99) simultaneamente.

Exemplos:
- ✅ Válido: Norris 1º, Piastri 3º, Verstappen 99 (fora dos pontos)
- ✅ Válido: Norris 99, Piastri 99, Verstappen 2º (dois fora dos pontos)
- ❌ Inválido: Norris 1º, Piastri 1º, Verstappen 5º (dois em 1º)

### Passo 3: Calcular Pontos Finais

Para cada combinação válida:

```python
pts_final = pts_atual + pts_sprint + pts_corrida
```

Exemplo:
- Norris: 390 + 0 (99 na sprint) + 0 (99 na corrida) = 390 pts
- Piastri: 366 + 8 (1º sprint) + 18 (2º corrida) = 392 pts
- Verstappen: 366 + 7 (2º sprint) + 25 (1º corrida) = 398 pts

### Passo 4: Identificar Empates no Topo

A função `identificar_empate()` verifica se o maior pontuador tem companhia:

```python
max_pontos = max(pontos.values())
lideres = [piloto for piloto, pts in pontos.items() if pts == max_pontos]

if len(lideres) >= 2:
    tipo = 'triplo' if len(lideres) == 3 else 'duplo'
```

**Tipos de empate:**
- **Triplo:** Todos os 3 pilotos empatados com a pontuação máxima
- **Duplo:** 2 pilotos empatados na liderança

### Passo 5: Exportar para CSV

Os cenários válidos são exportados para `cenarios_empate.csv` com as colunas:

| Coluna | Descrição |
|--------|-----------|
| `sprint_norris` | Posição de Norris na sprint |
| `sprint_piastri` | Posição de Piastri na sprint |
| `sprint_verstappen` | Posição de Verstappen na sprint |
| `corrida_norris` | Posição de Norris na corrida |
| `corrida_piastri` | Posição de Piastri na corrida |
| `corrida_verstappen` | Posição de Verstappen na corrida |
| `pts_norris` | Pontuação final de Norris |
| `pts_piastri` | Pontuação final de Piastri |
| `pts_verstappen` | Pontuação final de Verstappen |
| `tipo_empate` | `duplo` ou `triplo` |
| `pilotos_empatados` | Nomes dos pilotos empatados |

---

## ▶️ Como Executar

```bash
python f1_simulator.py
```

O arquivo `cenarios_empate.csv` será gerado no mesmo diretório.

---

## 🔧 Customização

Para simular outros cenários, edite as constantes no início do arquivo:

```python
# Alterar pontuação inicial dos pilotos
PILOTOS = {
    'norris': {'nome': 'L. Norris', 'pontos': 390},
    'piastri': {'nome': 'O. Piastri', 'pontos': 366},
    'verstappen': {'nome': 'M. Verstappen', 'pontos': 366},
}
```
