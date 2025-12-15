# 👻 Pac-Man Hunt Multiplayer

**Pac-Man Hunt** é uma reinterpretação multiplayer competitiva do clássico Pac-Man, sendo totalmente desenvolvido em Python. O jogo permite que múltiplos jogadores se conectem simultaneamente assumindo o papel de um dos **Fantasmas** (Blinky, Pinky, Inky e Clyde) em uma caçada ao Pac-Man, que é controlado pelo servidor.

---

## 🛠️ Tecnologias Utilizadas
* **Linguagem:** Python 3.10+
* **Renderização:** PyGame (Client-side)
* **Rede:** Módulo `socket` (TCP/IP), `threading`, `struct` e `pickle`.

---

## 🚀 Instalação

### Requisitos

- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)

### Passos

1. Clone o repositório
```bash
git clone https://github.com/codevinni/pacman-hunt.git
cd pacman-hunt
```

2. Crie um ambiente virtual (recomendado)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Instale as dependências
```bash
pip install -r client/client_requirements.txt
```

4. Verifique os IPs
  
Defina o IP e porta do servidor no arquivo `server/settings.json` e certifique-se que o mesmo endereço esteja configurado no arquivo `client/settings.json`

```json
{
    "network": {
        "ip": "127.0.0.1",
        "port": 8888,
        "timeout": null
    }
}
```

5. Inicie o servidor  
Execute a partir da raiz do projeto:

```bash
python3 -m server.main
```

6. Inicie os clientes  
Execute a partir da raiz do projeto:

```bash
# Jogador 1
python -m client.main

# Jogador 2... N
python -m client.main

...
```

## 🎮 Como Jogar

Ao entrar, você assume o controle de um fantasma. Trabalhe em equipe para impedir o Pac-Man.

### Controles

| Tecla | Ação |
|-------|------|
| `↑` `↓` `←` `→` | Movimentação |
| `F11` | Alternar tela cheia |
| `P` | Pausar/Menu |
| `ESC` | Sair do jogo |

### 🔄 Ciclo de Jogo e Reinício
* **Fim de Partida:** Assim que houver um vencedor (Pac-Man ou Fantasmas), o jogo exibe a tela de vitória e reinicia automaticamente após alguns segundos. Não é necessário fechar o cliente.
* **Reset de Servidor:** Se todos os jogadores se desconectarem, o servidor reseta o estado do jogo, aguardando novas conexões.

---

## 👥 Equipe

Projeto desenvolvido para a disciplina de Sistemas Distribuídos.

[**Vinícius (Líder)**](https://github.com/codevinni) - Arquitetura, Networking e Manutenção  
[**Hugo**](https://github.com/hugovrp) - Movimentação e Networking  
[**Pedro Nunes**](https://github.com/PedroIFSEMG) - Renderização e Interface  
[**Pedro Cota**](https://github.com/pedrocota) - Inteligência artificial do Pac-Man e Áudio  
[**Tainara**](https://github.com/tainararcs) - Mapa/Matriz e Lógica

---
