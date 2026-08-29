
# Simulador de Bilhares Simpléticos

Simulador interativo de bilhares **elásticos** e **simpléticos**, com visualização em tempo real no espaço de configuração e no espaço de fase (mapa de calor das colisões).

O diferencial do projeto é mostrar o **bilhar simplético acontecendo na tela**, e não apenas resultados estáticos ou gráficos prontos.

Origem: projeto em parceria com a UFSJ; continuação independente.

---

## O que já existe

- Física separada da interface (`core/`)
- Curvas plugáveis: Círculo, Elipse, Estádio de Bunimovich, Polígono regular
- Colisões elástica e simplética (com fallback seguro)
- Interface em **PySide6** com gráficos Matplotlib embutidos
- Animação por `QTimer`, passo a passo, reset
- Espaço de fase com eixos adaptativos e mapa de calor
- Testes básicos da física

---

## Estrutura do código

```text
bilhar/
├── core/           # Física (CurvaBase, estado, colisões, integrador)
├── curvas/         # Círculo, Elipse, Estádio, Polígono
├── viz/            # Espaço de configuração + espaço de fase
├── ui/
│   ├── qt_main.py  # Interface principal (PySide6)
│   └── controles.py# Versão antiga (Matplotlib widgets)
├── tests/
└── app.py          # Entrada antiga (Matplotlib puro)
```

Nova fronteira → novo arquivo em `curvas/`.  
A física não depende da interface.

---

## Como executar

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
pip install PySide6

# Interface atual (recomendado)
PYTHONPATH=. python -m bilhar.ui.qt_main

# Testes de física
PYTHONPATH=. python bilhar/tests/test_fisica.py
```

---

## Mini planejamento – próximas implementações

### Etapa 1 – Polígono livre (física)
- Criar `curvas/poligonolivre.py`
- Fronteira definida por lista de vértices quaisquer
- Fecha sozinha se o primeiro e o último ponto forem diferentes
- Testar a bolinha batendo nesse polígono (sem UI de desenho ainda)

### Etapa 2 – Desenho poligonal na tela
- Botão “Desenhar polígono” na interface Qt
- Clique no gráfico = novo vértice
- Fechar manualmente ou automático (reta do fim → início)
- Simular em cima do desenho

### Etapa 3 – Desenho à mão livre
- Botão “Desenhar à mão”
- Arrastar o mouse gera a curva
- Se não fechar, o programa fecha com uma reta
- Simplificar pontos em excesso, se necessário

### Etapa 4 – Função paramétrica fechada
- Criar `curvas/parametrica.py`
- Usuário digita uma fórmula (ex.: `r(θ) = 1 + 0.3*cos(3*θ)`)
- Programa gera a fronteira e simula
- Começa por amostragem da fórmula; depois melhora a precisão se precisar

### Etapa 5 – Ajustes
- Desfazer último ponto / limpar desenho
- Salvar e carregar fronteira
- (Opcional) arco de circunferência no modo desenho
- Exportar trajetória e colisões (CSV)
- Polir mapa de calor e figuras para artigo

---

## Roadmap resumido

| Fase | Conteúdo                         | Status        |
|------|----------------------------------|---------------|
| 1    | Fundação modular                 | Feito         |
| 2    | Estádio, polígono, testes        | Feito         |
| 3    | Interface PySide6 + animação     | Em andamento  |
| 4    | Desenho livre + função paramétrica | Próximo     |
| 5    | Exportação, polimento, extras    | Depois        |

---

## Princípios (para não perder o rumo)

1. Uma etapa de cada vez, testada antes da seguinte.
2. Nova fronteira = arquivo em `curvas/`.
3. UI só captura pontos ou fórmula e entrega para a física.
4. Não criar pastas novas até o desenho poligonal estar funcionando.
5. Simplético em fronteiras não suaves pode cair para elástico (já existe fallback).

---

## Critérios de sucesso

- Dá para adicionar uma curva nova só mexendo em `curvas/`.
- A física roda sem abrir janela gráfica.
- Dá para desenhar uma fronteira na tela e simular nela.
- Dá para definir uma fronteira por fórmula e simular nela.


