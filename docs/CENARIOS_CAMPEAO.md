# 🏆 Cenários de Campeão - Documentação Técnica

Este documento detalha a simulação de **todos os cenários possíveis** para determinar o campeão do campeonato de F1 2025.

---

## 📋 Contexto do Problema

### Classificação Atual (28/11/2025)

| Piloto         | Pontos | Vitórias | 2º Lugares | 3º Lugares |
|----------------|-------:|---------:|-----------:|-----------:|
| L. Norris      |    390 |        7 |          6 |          4 |
| O. Piastri     |    366 |        7 |          4 |          3 |
| M. Verstappen  |    366 |        6 |          4 |          3 |

### Eventos Restantes

| Evento | Tipo | Posições | Máx Pontos |
|--------|------|:--------:|:----------:|
| Qatar Sprint | Sprint | 1º-8º | 8 pts |
| Qatar GP | Corrida | 1º-10º | 25 pts |
| Abu Dhabi GP | Corrida | 1º-10º | 25 pts |

**Total máximo por piloto:** 58 pontos (8 + 25 + 25)

---

## 🔢 Sistema de Desempate da F1

Quando dois ou mais pilotos terminam com a mesma pontuação, o campeão é decidido por:

1. **Mais pontos** (critério principal)
2. **Mais vitórias** (1º lugar em corridas)
3. **Mais segundos lugares**
4. **Mais terceiros lugares**

```python
def determinar_campeao(pts, wins, seconds, thirds):
    """
    Determina o campeão usando sistema de tie-break da F1.
    """
    stats = [
        (pts[i], wins[i], seconds[i], thirds[i], pilotos[i])
        for i in range(3)
    ]
    stats.sort(reverse=True)  # Ordenar por todos os critérios

    primeiro, segundo = stats[0], stats[1]

    if primeiro[0] > segundo[0]:
        return primeiro[4], 'pontos'
    elif primeiro[1] > segundo[1]:
        return primeiro[4], 'vitorias'
    elif primeiro[2] > segundo[2]:
        return primeiro[4], 'segundos_lugares'
    elif primeiro[3] > segundo[3]:
        return primeiro[4], 'terceiros_lugares'
    else:
        return primeiro[4], 'empate_total'
```

---

## 📐 Otimização por Convolução

### O Problema de Escala

Cálculo bruto de todas as combinações:

$$
\text{Combinações brutas} = 529 \times 1.021 \times 1.021 \approx 551 \text{ milhões}
$$

Isso seria computacionalmente inviável.

### Solução: Agregação por Delta

Em vez de armazenar cada combinação individual, o simulador usa **agregação por delta**:

1. Para cada evento, calcula-se o **delta** (variação) de stats:
   - Delta de pontos ganhos
   - Delta de vitórias (+1 se 1º lugar)
   - Delta de 2º lugares (+1 se 2º lugar)
   - Delta de 3º lugares (+1 se 3º lugar)

2. Agrupa combinações que resultam no **mesmo delta final**

3. Armazena apenas **estados únicos** com contagem de quantas combinações levam a cada estado

### Estrutura de Dados

```python
@dataclass(frozen=True)
class Delta:
    """Delta de um evento para um piloto."""
    pontos: int
    vitoria: int  # 0 ou 1
    segundo: int  # 0 ou 1
    terceiro: int  # 0 ou 1

@dataclass(frozen=True)
class DeltaTrio:
    """Delta combinado para os 3 pilotos."""
    norris: Delta
    piastri: Delta
    verstappen: Delta
```

### Processo de Convolução

```
[Sprint Qatar]     [Race Qatar]      [Race Abu Dhabi]
   529 deltas   ×   1.021 deltas  →  Estados Qatar (~20k únicos)
                                          ↓
                                    × 1.021 deltas
                                          ↓
                                  Estados Finais (~100k únicos)
```

**Resultado:** Redução de ~551M para ~100k estados únicos a processar.

---

## 📊 Resultados Típicos

### Chances de Título

| Piloto | Chance | Combinações |
|--------|-------:|------------:|
| Norris | ~60% | ~330.000 |
| Piastri | ~20% | ~110.000 |
| Verstappen | ~20% | ~110.000 |

### Métodos de Decisão

| Método | Descrição | Frequência |
|--------|-----------|:----------:|
| Pontos | Mais pontos totais | ~95% |
| Vitórias | Empate em pontos, mais vitórias | ~4% |
| 2º Lugares | Empate em pontos e vitórias | ~0.5% |
| 3º Lugares | Muito raro | ~0.1% |
| Empate Total | Praticamente impossível | <0.01% |

---

## 🏗️ Detalhes de Implementação

### Geração de Deltas por Evento

```python
def gerar_deltas_evento(posicoes: list[int], tabela_pontos: dict) -> list[DeltaTrio]:
    """
    Gera todos os deltas válidos para um evento.

    Regras:
    - Cada piloto pode ficar em qualquer posição que pontua OU fora (99)
    - Posições pontuadas não podem se repetir
    """
    todas_posicoes = posicoes + [FORA_PONTOS]
    deltas = []

    for pos_n, pos_p, pos_v in product(todas_posicoes, repeat=3):
        # Verificar posições não repetidas (exceto fora)
        posicoes_dentro = [p for p in [pos_n, pos_p, pos_v] if p != FORA_PONTOS]
        if len(posicoes_dentro) != len(set(posicoes_dentro)):
            continue

        deltas.append(DeltaTrio(
            norris=posicao_para_delta(pos_n, tabela_pontos),
            piastri=posicao_para_delta(pos_p, tabela_pontos),
            verstappen=posicao_para_delta(pos_v, tabela_pontos),
        ))

    return deltas
```

### Simulação por Convolução

```python
def simular_cenarios() -> list[dict]:
    # Fase 1: Gerar deltas por evento
    deltas_sprint = gerar_deltas_evento(POSICOES_SPRINT, PONTOS_SPRINT)
    deltas_corrida = gerar_deltas_evento(POSICOES_CORRIDA, PONTOS_CORRIDA)

    # Fase 2: Convolução Sprint Qatar + Race Qatar
    estados_qatar: Counter[DeltaTrio] = Counter()
    for ds in deltas_sprint:
        for dr in deltas_corrida:
            delta_combinado = somar_delta_trios(ds, dr)
            estados_qatar[delta_combinado] += 1

    # Fase 3: Convolução com Abu Dhabi
    estados_finais: Counter[DeltaTrio] = Counter()
    for delta_qatar, count_qatar in estados_qatar.items():
        for da in deltas_corrida:
            delta_final = somar_delta_trios(delta_qatar, da)
            estados_finais[delta_final] += count_qatar

    # Fase 4: Determinar campeão para cada estado final
    cenarios = []
    for delta, num_combinacoes in estados_finais.items():
        campeao, metodo = calcular_campeao(delta)
        cenarios.append({
            'delta': delta,
            'campeao': campeao,
            'metodo_decisao': metodo,
            'num_combinacoes': num_combinacoes,
        })

    return cenarios
```

---

## 📈 Dashboard

### Estrutura

```
┌─────────────────────────────────────────────────────────────┐
│  🏆 F1 2025 - Cenários de Campeão                           │
├─────────────────────────────────────────────────────────────┤
│  👤 Cards dos Pilotos + Chances                             │
├─────────────────────────────────────────────────────────────┤
│  📊 Tabs de Visualização                                    │
│  ├── 🎯 Como Ganhar (chances + métodos)                     │
│  ├── 📈 Distribuição de Pontos                              │
│  ├── 🎛️ Simulador What If                                   │
│  └── 📋 Tabela de Cenários                                  │
└─────────────────────────────────────────────────────────────┘
```

### Visualizações

#### 🎯 Como Cada Piloto Pode Ganhar

- **Barras horizontais:** Chance de título por piloto
- **Barras empilhadas:** Métodos de decisão por piloto
- **Sunburst:** Hierarquia Campeão → Método de Decisão

#### 📈 Distribuição de Pontos

- **Box plots:** Distribuição de pontos finais por piloto
- **Comparativo de ranges:** Intervalos de pontuação vitoriosa

#### 🎛️ Simulador "What If"

Permite ao usuário definir posições específicas para cada piloto em cada evento:

| Evento | Norris | Piastri | Verstappen |
|--------|:------:|:-------:|:----------:|
| Sprint Qatar | Selectbox | Selectbox | Selectbox |
| Race Qatar | Selectbox | Selectbox | Selectbox |
| Race Abu Dhabi | Selectbox | Selectbox | Selectbox |

Exibe instantaneamente:
- Pontuação final de cada piloto
- Quem seria campeão
- Critério de desempate usado (se houver)

#### 📋 Tabela de Cenários

Cenários filtráveis por:
- Campeão selecionado
- Método de decisão
- Range de pontos

---

## 🎨 Paleta de Cores

| Elemento | Cor | Uso |
|----------|-----|-----|
| Norris | 🟠 `#FFB347` | Cards, gráficos |
| Piastri | 🔵 `#87CEEB` | Cards, gráficos |
| Verstappen | 🟣 `#DDA0DD` | Cards, gráficos |
| Pontos (método) | 🟢 `#98D8C8` | Verde menta |
| Vitórias (método) | 🟡 `#F7DC6F` | Amarelo |
| 2º Lugares | 🟣 `#BB8FCE` | Roxo claro |
| 3º Lugares | 🔵 `#85C1E9` | Azul claro |

---

## 🧠 Insights Matemáticos

### Por que Norris é Favorito?

1. **Vantagem de 24 pontos** sobre Piastri e Verstappen
2. **Mesmo número de vitórias** que Piastri (7), e mais que Verstappen (6)
3. **Mais 2º lugares** (6 vs 4) — vantagem em desempates

### Cenários de Virada

Para Piastri ou Verstappen vencerem, precisam:

$$
G_{\text{desafiante}} - G_{\text{Norris}} > 24 \text{ (para vencer em pontos)}
$$

Ou igualar/superar em pontos E ter vantagem em vitórias:

$$
G_{\text{desafiante}} - G_{\text{Norris}} = 24 \text{ e } V_{\text{desafiante}} > V_{\text{Norris}}
$$

Com máximo de 58 pontos disponíveis, a diferença máxima possível é 58 pontos.
