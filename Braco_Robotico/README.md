# 🤖 Braço Robótico Controlado por Python

Projeto de automação e robótica que substitui o controle físico por potenciômetros por uma interface gráfica desenvolvida em Python, permitindo controlar um braço robótico de 4 servomotores diretamente pelo computador.

O projeto integra **programação, eletrônica, comunicação serial e robótica**, demonstrando como o software pode interagir diretamente com o mundo físico.

## 📸 Demonstração

O sistema utiliza uma interface gráfica para controlar individualmente cada articulação do braço robótico, permitindo ajustar os ângulos dos servomotores em tempo real.

## ⚙️ Funcionalidades

- **Comunicação serial:** conexão com o braço robótico pela porta COM, com indicação do status da conexão.
- **Controle individual:** sliders para controlar cada uma das quatro articulações, com ângulos de 0° a 180°.
- **Posição central:** botão para retornar todos os servomotores à posição de 90°.
- **Controle em tempo real:** envio dos ângulos diretamente para os servomotores.
- **Interface gráfica:** controle intuitivo por meio de uma aplicação desenvolvida em Python.

## 🦾 Estrutura do braço robótico

O braço possui quatro servomotores, responsáveis pelos seguintes movimentos:

| Articulação | Função |
|---|---|
| Base | Rotação horizontal do braço |
| Braço | Movimento de elevação |
| Antebraço | Ajuste de alcance e posição |
| Garra | Abertura e fechamento |

## 🛠️ Tecnologias e componentes

**Software**
- Python
- Interface gráfica (GUI)
- Comunicação serial

**Hardware**
- Arduino
- 4 servomotores
- Estrutura física do braço robótico
- Circuito de alimentação e conexões

**Bibliotecas Python**
- `pyserial` – Comunicação com o Arduino.
- Biblioteca gráfica utilizada no desenvolvimento da interface.

## 🚀 Como executar

### 1. Pré-requisitos

- Python instalado.
- Arduino conectado ao computador.
- Servomotores conectados ao circuito de controle.
- Bibliotecas necessárias instaladas.

### 2. Instalação das dependências

```bash
pip install pyserial
```

### 3. Configuração da comunicação

Conecte o Arduino ao computador e identifique a porta serial correspondente (COM).

Configure a porta e os parâmetros de comunicação conforme o código do projeto.

### 4. Execução

Execute o arquivo principal da aplicação Python:

```bash
python main.py
```

Após estabelecer a conexão, utilize os controles deslizantes para movimentar cada articulação do braço robótico.

## 💡 Possibilidades de expansão

A substituição dos potenciômetros por um controle via software abre possibilidades para novas funcionalidades:

- Salvamento e recuperação de posições.
- Gravação e reprodução de sequências de movimentos.
- Automação de tarefas repetitivas.
- Controle remoto do braço robótico.
- Integração futura com visão computacional.
- Desenvolvimento de sistemas de movimentação automatizados.

## 🎓 Objetivo educacional

Além da construção física do braço, o projeto demonstra a aplicação prática de conceitos fundamentais de programação e eletrônica.

A proposta é mostrar como o código pode deixar de ser apenas uma sequência de instruções na tela e passar a controlar dispositivos e movimentos no mundo real.

**Um projeto que conecta programação, eletrônica e criatividade para transformar código em movimento!**

---

### 🏷️ Tags

`Python` `Robótica` `Arduino` `Programação` `Eletrônica` `Automação` `Educação Tecnológica`