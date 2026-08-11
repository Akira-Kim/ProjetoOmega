# Simulador de Bilhares Simpléticos

Simulador interativo de bilhares **elásticos** e **simpléticos**, com visualização em tempo real do movimento no espaço de configuração e no espaço de fase (incluindo mapa de calor das colisões).

O diferencial do projeto é mostrar o **bilhar simplético acontecendo na tela**, e não apenas resultados estáticos ou gráficos prontos.

---

## Planejamento de Software

### 1. Visão do Projeto

Simulador interativo de bilhares elásticos e **simpléticos**, com visualização em tempo real do movimento da partícula no espaço de configuração e no espaço de fase (incluindo mapa de calor das colisões).

### 2. Objetivos

**Principais**
- Código modular, testável e fácil de expandir.
- Separação clara entre **física**, **visualização** e **interface**.
- Facilitar adição de novas curvas, novos tipos de colisão e novas visualizações.
- Manter a simulação em tempo real como experiência central.

**Secundários**
- Exportação de dados e figuras de qualidade.
- Servir tanto para ensino quanto para exploração científica.
- Base sólida para futuras versões (desktop e/ou web).

### 3. Princípios de Design

- **Separação de responsabilidades**: a física não conhece Matplotlib.
- **Curvas plugáveis**: novas fronteiras são adicionadas com o mínimo de alteração.
- **Estado explícito**: todo o estado da simulação fica em um único objeto.
- **Testabilidade**: a lógica de colisão e integração é testável sem interface gráfica.
- **Performance progressiva**: primeiro correto, depois rápido.

### 4. Arquitetura (Fase 1)

```
bilhar/
├── core/                 # Física e estado (sem dependência gráfica)
│   ├── curva.py          # Interface CurvaBase
│   ├── fisica.py         # Colisões (elástico + simplético)
│   ├── estado.py         # EstadoSimulacao
│   └── integrador.py     # Passo da simulação (event-driven)
│
├── curvas/               # Implementações concretas
│   ├── circulo.py
│   ├── elipse.py
│   └── estadio.py        # Estádio de Bunimovich
│
├── viz/                  # Camada de visualização
│   ├── canvas.py         # Espaço de configuração
│   ├── fase.py           # Espaço de fase + heatmap
│   └── animacao.py
│
├── ui/                   # Controles (widgets Matplotlib nesta fase)
│   └── controles.py
│
└── app.py                # Ponto de entrada
```

### 5. Roadmap

#### Fase 1 – Fundação ✅
- [x] Extrair e limpar as classes principais
- [x] Interface clara para curvas (`CurvaBase`)
- [x] Animação funcionando com a nova estrutura
- [x] Remoção de estado global misturado com física

#### Fase 2 – Robustez e Extensibilidade (em andamento)
- [x] Sistema de registro de curvas mais completo
- [x] Implementar Estádio de Bunimovich
- [x] Testes unitários da física (`bilhar/tests/test_fisica.py`)
- [ ] Polígonos regulares
- [ ] Melhorar detecção de colisão (erros numéricos / túneis)

#### Fase 3 – Interface
- [ ] Migrar UI para PySide6 + Matplotlib ou Dear PyGui
- [ ] Layout mais limpo e estável
- [ ] Presets de condições iniciais
- [ ] Controles de passo a passo

#### Fase 4 – Valor Agregado
- [ ] Exportação de trajetória e dados de colisão
- [ ] Melhorias no mapa de calor
- [ ] Figuras de alta qualidade para artigos
- [ ] Documentação e exemplos

#### Fase 5 – Futuro
- [ ] Versão web
- [ ] Indicadores de caos
- [ ] Mais leis de reflexão
- [ ] Gravação de vídeo/GIF

### 6. Como executar (Fase 1)

```bash
# Criar ambiente (recomendado)
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

pip install -r requirements.txt

# Executar
python -m bilhar.app
# ou
python bilhar/app.py
```

### 7. Critérios de Sucesso da Refatoração

- É possível adicionar uma nova curva alterando apenas a pasta `curvas/`.
- A física roda e é testável sem abrir nenhuma janela gráfica.
- Um novo colaborador consegue entender a estrutura em menos de 30 minutos.

---

**Status atual**: Fase 2 em andamento – Estádio + testes unitários adicionados.  
**Origem**: Projeto desenvolvido em parceria com a UFSJ; continuação independente após saída da faculdade.
