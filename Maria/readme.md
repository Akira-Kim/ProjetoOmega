# Dona Maria — v01.00

Assistente pessoal em Python (em evolução).

**Versão:** `v01.00`  
**Status:** base usável no dia a dia (texto + SQLite + contexto + IA opcional)  
**Próximo:** cascata de IAs, base confiável, raciocínio local, modo guia (ver planejamento)

---

## O que é

A **Dona Maria** é um assistente de conversa em português do Brasil.  
Nesta versão ela já:

- responde a partir de uma base local (SQLite);
- entende digitação informal e abreviações;
- mantém contexto curto de conversa (ex.: “e o de C?”);
- pode consultar IA externa (Gemini) quando a base não sabe;
- aprende novas respostas (usuário ou IA, conforme configuração);
- roda em **interface gráfica** ou **terminal**.

**Destino de longo prazo (não é esta versão):** assistente no espírito Jarvis/Sexta-feira — guia, confidente e mentor (elogia e puxa a orelha), com memória, raciocínio local, ferramentas web/PC e controle total do usuário.

---

## O que a v01.00 inclui (P0 — feito)

| Recurso | Detalhe |
|--------|---------|
| Interpretador PT | Normalização, juntadas (`oque` → `o que`), correção de digitação |
| Base SQLite | `conhecimento.db`, campo `vezes_usada` |
| Busca | Match exato + similaridade por palavras de conteúdo |
| Contexto | Expansão de continuações curtas na conversa |
| Fallback IA | Google Gemini (`fallback_ia.py`), opcional |
| Aprendizado | `salva_sugestao` + `AUTO_APRENDER_IA` |
| Interface | Tkinter (`InterfaceGrafica.py`) e console (`DonaMaria.py`) |
| Launcher | `python iniciar.py` ou `python iniciar.py console` |
| Segurança básica | Filtro de palavras proibidas; `api_key.txt` fora do Git |

---

## O que a v01.00 ainda **não** é

- Cascata de várias IAs (Groq, OpenRouter, reserva)
- Verificação de fatos (yellow/red/estável)
- Memória longa de vida / filosofia / projetos
- Composição de vários trechos (raciocínio local avançado)
- Botão ligar/desligar API só nas respostas
- Voz, agente no PC, limite de 2 máquinas, protocolo SURTO

Isso está no **planejamento futuro**, não nesta tag.

---

## Como rodar

### Requisitos

- Python 3.10+ (recomendado 3.11+)
- Bibliotecas padrão (não exige `pip` obrigatório para o núcleo)
- Windows / Linux / macOS com Tkinter (para a GUI)

### Arquivos essenciais

```
Maria/
├── iniciar.py
├── chat.py
├── InterfaceGrafica.py
├── DonaMaria.py
├── fallback_ia.py
├── conhecimento.db
├── info.txt
├── criar_banco.py
├── importar_info.py
├── api_key.txt          ← local, NÃO versionar
└── README.md
```

### Comandos

```bash
cd Maria   # ou a pasta do projeto

# Interface gráfica
python iniciar.py

# Terminal
python iniciar.py console
```

### Base de conhecimento

Se precisar recriar / reimportar:

```bash
python criar_banco.py
python importar_info.py
python teste_banco.py
```

### IA externa (opcional)

1. Crie uma chave em [Google AI Studio](https://aistudio.google.com/apikey)
2. Arquivo `api_key.txt` na mesma pasta (uma linha = a chave)
3. Sem chave, a Maria usa só a base local e o modo “ensinar”

**Nunca** faça commit de `api_key.txt`.

---

## Configuração rápida (`chat.py`)

| Variável | Efeito |
|----------|--------|
| `AUTO_APRENDER_IA = True` | Grava no SQLite respostas vindas da IA |
| `LIMIAR_JACCARD` / `LIMIAR_DIGITACAO` | Sensibilidade da busca por similaridade |

---

## Estrutura do código (v01.00)

| Arquivo | Função |
|---------|--------|
| `chat.py` | Núcleo: normalizar, buscar, contexto, aprender |
| `fallback_ia.py` | Chamada ao Gemini |
| `InterfaceGrafica.py` | GUI Tkinter |
| `DonaMaria.py` | Loop no terminal |
| `iniciar.py` | Sobe GUI ou console |
| `conhecimento.db` | Base SQLite |
| `info.txt` | Fonte texto para importação |
| `ProximosPassos.txt` | Planejamento completo (se presente no repo) |

---

## Planejamento futuro (resumo)

Ordem prevista após a v01.00:

1. **P1** — Cascata de IAs + controle API respostas vs conferência  
2. **P2** — Base confiável (flags, verificação, correção)  
3. **P2/P3** — “Info fixa?” na GUI  
4. **P3** — Painel e GUI mais clara  
5. **Raciocínio local** — composição de trechos + rastreio de origem  
6. **P4** — Pessoal, filosofia, modo guia (mentor / confidente)  
7. **P5** — Embeddings / neural local  
8. **P6–P8** — Voz, mídia, PC assistido, segurança avançada  

**Norte:** assistente que guia com memória e ferramentas, sem depender sempre de API externa; API como módulo ligável.

Detalhes: ver `ProximosPassos.txt` no repositório (quando versionado).

---

## Segurança e privacidade (v01.00)

- Chaves de API apenas locais (`.gitignore`)
- Não commitar dados íntimos futuros (`pessoal.db`, histórico, incidentes)
- Filtro de conteúdo ofensivo / scam básico na conversa

---

## Como citar esta versão

```
Dona Maria v01.00 — assistente local em Python (SQLite + contexto + Gemini opcional)
```

---

## Licença / autor

Projeto pessoal de aprendizado e produto (ProjetoOmega / Maria).  
Ajuste autor e licença conforme o seu repositório GitHub.
