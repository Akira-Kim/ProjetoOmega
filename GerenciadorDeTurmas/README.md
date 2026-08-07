# Gerenciador de Turmas

**Versão 1.0** · App desktop para professores planejarem aulas, acompanharem turmas e registrarem o dia a dia da sala.

Python · Flet · SQLite · Uso local · Em produção pessoal

**Licença:** Apache License 2.0 (Projeto Omega)

---

## O que é

O **Gerenciador de Turmas** nasceu de necessidades reais de sala de aula: montar o calendário do período, respeitar feriados, remarcar aulas sem bagunçar o restante, saber o que já foi estudado ou dado, e guardar notas, observações e relatórios dos alunos.

É um aplicativo **desktop**, com dados **locais** (SQLite), pensado para o professor usar no dia a dia — não apenas um protótipo de estudo.

> Parte do **Projeto Omega**, ecossistema pessoal de ferramentas educacionais e IA.

---

## Funcionalidades (v1.0)

### Calendário e planejamento
- Visão **Semana** e **Mês** com cores por status
- Turmas com dias da semana, data de início e fim
- Geração automática de aulas no período
- Feriados oficiais do Brasil + eventos manuais (recesso, reposição, monitoria)
- Remarcação de aula com empurrão das aulas seguintes em caso de conflito

### Aula a aula
- Status: planejada · estudada · dada
- Conteúdo, links e observações
- Indicadores visuais nos cards da semana

### Alunos
- Cadastro por turma
- Nota, coins e análise por aula
- Ficha do aluno com histórico editável e resumo (média, coins totais)

### Relatórios
- Relatório de aula (texto livre vinculado à aula)
- Relatório do aluno com **modelo** (.txt / .md / .docx) + dados montados pelo app
- Geração assistida por **Gemini** (opcional; chave local)
- Histórico com filtros, edição e exclusão

### Utilitários
- Backup do banco (`data/backups/`)
- Atalho de inicialização no Windows (script `iniciar.bat`)

---

## Cores no calendário

| Cor | Significado |
|-----|-------------|
| Verde | Aula dada |
| Amarelo | Aula desta semana (ainda não dada) |
| Cinza | Passou e não foi dada |
| Claro | Futuras |
| Roxo | Feriado / recesso / evento |
| Laranja | Reposição / monitoria |

---

## Stack

| Camada | Tecnologia |
|--------|------------|
| Linguagem | Python 3.11+ |
| Interface | Flet |
| Banco | SQLite |
| Feriados | holidays (Brasil) |
| IA (opcional) | Gemini via httpx |
| Modelos Word | python-docx |

---

## Estrutura do projeto

```text
GerenciadorDeTurmas/
├── main.py
├── database.py
├── models.py
├── requirements.txt
├── iniciar.bat
├── LICENSE
├── PLANEJAMENTO.txt
├── docs/
├── keys/
│   └── gemini_key.txt
├── data/
│   ├── planner.db
│   └── backups/
├── assets/
├── utils/
│   ├── calendar_helpers.py
│   ├── ai_client.py
│   ├── backup.py
│   └── theme.py
└── views/
    ├── semana.py
    ├── mes.py
    ├── turmas.py
    ├── gerenciar.py
    └── relatorios.py

Como rodar
1. Dependências

    cd GerenciadorDeTurmas
    pip install -r requirements.txt


2. Iniciar

    python main.py

Ou, no Windows, dois cliques em iniciar.bat (ou no atalho da área de trabalho).


3. Gemini (opcional)

    - Crie a pasta keys/
    - Arquivo keys/gemini_key.txt com a API key (uma linha)
    - Modelo de relatório em .txt / .md / .docx (pode usar {{dados}} no texto)

    A pasta keys/ deve estar no .gitignore.

Requisitos

Windows, Linux ou macOS (Flet)
Python 3.11 ou superior
Conexão com internet apenas se for gerar relatório com Gemini


Status do projeto

    Item,                                   Situação

Núcleo funcional,                   Concluído (v1.0)
Uso real,                           Em uso pelo autor em aulas
Polimento visual,                   Planejado para v1.1+
Integração Maria (IA própria),      Futuro

A v1.0 prioriza funcionar bem no cotidiano. Melhorias estéticas e extras (PDF, temas, etc.) vêm depois, sem reabrir o que já está estável.


Roadmap breve
Feito (1.0)
Fundação, gerenciar, semana, mês, alunos, relatórios de aula, relatório do aluno + Gemini, backup.
Próximo (1.1 — quando retomar)
Visual (tema, tipografia, cards), UX, exportação, configurações.
Depois
IA própria (Maria), possíveis recursos multi-professor / distribuição.


Privacidade

Dados ficam no seu computador (data/planner.db)
Não há conta obrigatória nem servidor próprio do app
A única saída de dados para a rede, se ativada, é a chamada ao Gemini na geração de relatório do aluno


Autor
Desenvolvido por Akira Kim (Bruno) — professor de Programação e Robótica, Técnico em Informática (CEFET), em formação em Engenharia de Software.

GitHub: https://github.com/Akira-Kim
LinkedIn: https://www.linkedin.com/in/akira-bruno

Projeto autodidata, construído de ponta a ponta (requisitos, modelagem, interface, regras de calendário e documentação).

Licença
Este projeto faz parte do Projeto Omega e é distribuído sob a licença Apache License 2.0.
Você pode usar, modificar e distribuir o código, inclusive em projetos comerciais, desde que preserve o aviso de copyright e a licença, e indique alterações relevantes. A licença não concede uso de marcas do autor e inclui isenção de garantias.
O texto completo está no arquivo LICENSE na raiz do repositório.

Copyright 2026 Akira Kim (Bruno)


Planejar bem a aula também é código: organização, regras claras e respeito ao calendário real.
