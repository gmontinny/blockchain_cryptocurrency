# 🪙 Bitcoin Blockchain

Simulação de uma blockchain inspirada no Bitcoin, com os mesmos conceitos usados na rede real: carteiras digitais, transações com assinatura criptográfica, mineração de blocos e consenso entre múltiplos nós.

> **Para quem é este projeto?**
> Para quem quer entender como o Bitcoin funciona por dentro, rodando uma rede local completa com 3 nós independentes e banco de dados real.

---

## 📋 Sumário

- [O que este projeto faz?](#-o-que-este-projeto-faz)
- [Como o Bitcoin funciona? (resumo simples)](#-como-o-bitcoin-funciona-resumo-simples)
- [Arquitetura](#-arquitetura)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Pré-requisitos](#-pré-requisitos)
- [Como Executar](#-como-executar)
- [Guia Prático: Fazendo sua primeira transação](#-guia-prático-fazendo-sua-primeira-transação)
- [API Reference](#-api-reference)
- [Banco de Dados](#-banco-de-dados)
- [Conceitos Implementados](#-conceitos-implementados)

---

## 🤔 O que este projeto faz?

Este projeto simula uma rede Bitcoin local com:

- **3 nós** (computadores) que se comunicam entre si
- **Carteiras digitais** com chaves criptográficas reais
- **Mineração** de blocos com Proof of Work
- **Transações** que seguem o modelo UTXO do Bitcoin
- **Banco de dados** PostgreSQL para persistir todos os dados
- **Consenso** automático: se os nós divergirem, o mais longo vence

---

## 💡 Como o Bitcoin funciona? (resumo simples)

Imagine que o Bitcoin é como um **livro-caixa público** onde todo mundo pode ver todas as transações, mas ninguém pode falsificá-las.

| Conceito | Analogia do mundo real |
|---|---|
| **Carteira** | Sua conta bancária, mas sem banco — você é o dono da chave |
| **Endereço** | Número da sua conta, que você compartilha para receber |
| **Chave privada** | Sua senha secreta — nunca compartilhe! |
| **Transação** | Transferência de dinheiro assinada por você |
| **Bloco** | Página do livro-caixa com várias transações |
| **Blockchain** | O livro-caixa completo, com todas as páginas encadeadas |
| **Mineração** | Processo de "selar" uma página do livro para que não possa ser alterada |
| **UTXO** | Cédulas de dinheiro — você gasta cédulas inteiras e recebe troco |
| **Mempool** | Fila de espera das transações antes de entrar num bloco |

### Como funciona o UTXO (o modelo de saldo do Bitcoin)?

No Bitcoin, seu saldo **não é um número guardado em algum lugar**. É a soma de todas as "cédulas" que você recebeu e ainda não gastou.

**Exemplo:**
```
Você recebeu:  50 moedas (bloco 1)
Você recebeu:  30 moedas (bloco 2)
Você gastou:   50 moedas (enviou para alguém)

Seu saldo = 30 moedas  ← apenas o UTXO não gasto
```

Quando você envia 20 moedas de um UTXO de 30, você **gasta o UTXO inteiro** e recebe 10 de troco de volta para você mesmo — exatamente como pagar com uma nota de R$50 e receber troco.

---

## 🏗 Arquitetura

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Node 1    │    │   Node 2    │    │   Node 3    │
│  :5001      │◄──►│  :5002      │◄──►│  :5003      │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       └──────────────────┴──────────────────┘
                          │
                 ┌────────▼────────┐
                 │   PostgreSQL    │
                 │   :5432         │
                 └─────────────────┘
```

- Cada **nó** é um servidor independente que pode minerar blocos e processar transações
- Os 3 nós **compartilham o mesmo banco** PostgreSQL
- Quando há divergência entre nós, o **consenso Nakamoto** resolve: a cadeia mais longa e válida vence

---

## 📁 Estrutura do Projeto

```
cryptocurrency/
├── app/
│   ├── blockchain.py     # Lógica do bloco: hash, mineração, Merkle Tree, dificuldade
│   ├── wallet.py         # Criação de carteiras e assinatura criptográfica (ECDSA)
│   ├── transaction.py    # Modelo UTXO: criar, validar e assinar transações
│   ├── database.py       # Tudo que salva/lê no PostgreSQL
│   └── routes.py         # Endpoints da API REST (Flask)
├── main.py               # Ponto de entrada: conecta ao banco e sobe o servidor
├── requirements.txt      # Dependências Python
├── Dockerfile            # Como construir a imagem do nó
└── docker-compose.yml    # Orquestra os 3 nós + banco de dados
```

---

## ✅ Pré-requisitos

Você só precisa ter instalado:

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — versão 24 ou superior
- [Docker Compose](https://docs.docker.com/compose/) — já vem junto com o Docker Desktop

> Não precisa instalar Python, PostgreSQL nem nenhuma outra dependência. O Docker cuida de tudo.

---

## 🚀 Como Executar

### 1. Clone ou baixe o projeto

```bash
git clone <url-do-repositorio>
cd cryptocurrency
```

### 2. Suba todos os serviços com um único comando

```bash
docker-compose up --build
```

Aguarde até ver as mensagens abaixo nos logs (pode levar 1-2 minutos na primeira vez):

```
bitcoin_node1  | Banco de dados conectado e inicializado.
bitcoin_node1  |  * Running on http://0.0.0.0:5001
bitcoin_node2  | Banco de dados conectado e inicializado.
bitcoin_node2  |  * Running on http://0.0.0.0:5002
bitcoin_node3  | Banco de dados conectado e inicializado.
bitcoin_node3  |  * Running on http://0.0.0.0:5003
```

Isso inicia 4 serviços:

| Serviço | Endereço | O que é |
|---|---|---|
| `bitcoin_db` | `localhost:5432` | Banco de dados PostgreSQL |
| `bitcoin_node1` | `http://localhost:5001` | Nó 1 da blockchain |
| `bitcoin_node2` | `http://localhost:5002` | Nó 2 da blockchain |
| `bitcoin_node3` | `http://localhost:5003` | Nó 3 da blockchain |

### 3. Parar os serviços

```bash
# Para os serviços mas mantém os dados do banco
docker-compose down

# Para os serviços E apaga todos os dados (começa do zero)
docker-compose down -v
```

---

## 🧪 Guia Prático: Fazendo sua primeira transação

Siga este passo a passo completo usando qualquer ferramenta HTTP (curl, Postman, Insomnia ou o próprio navegador para os GETs).

> Todos os exemplos usam o **Node 1** (`http://localhost:5001`). Você pode usar qualquer nó.

---

### Passo 1 — Criar a carteira do minerador (Alice)

```
GET http://localhost:5001/wallet/new
```

**Resposta:**
```json
{
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgnMGLgPPaFyBNMFqo\n...\n-----END PRIVATE KEY-----\n",
  "public_key": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEqW3FKJA...\n-----END PUBLIC KEY-----\n",
  "address": "1a7f3c9d2e4b8a1f6c0d5e2b9a3f7c1d4e8b2a5f"
}
```

> 💾 **Salve esses dados!** Você vai precisar do `address`, `public_key` e `private_key` nos próximos passos.
>
> - `address` → é o número da sua "conta", compartilhe para receber moedas
> - `public_key` → usada para verificar que você assinou a transação
> - `private_key` → sua senha secreta para assinar transações, **nunca compartilhe**

---

### Passo 2 — Minerar o primeiro bloco (Alice recebe 50 moedas)

Passe o endereço de Alice como parâmetro para que a recompensa vá para a carteira dela:

```
GET http://localhost:5001/mine?address=1a7f3c9d2e4b8a1f6c0d5e2b9a3f7c1d4e8b2a5f
```

> ⚠️ Substitua o endereço pelo `address` que você recebeu no Passo 1.

**Resposta:**
```json
{
  "message": "Bloco minerado com sucesso!",
  "block_index": 2,
  "hash": "0000a3f7c2d1e9b4a8f5c0d3e7b2a1f6c9d4e8b3a7f2c1d5e0b9a4f8c3d7e2b1",
  "difficulty": 4,
  "nonce": 38291,
  "merkle_root": "d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3",
  "transactions": 1,
  "miner_reward": 50.0,
  "miner_address": "1a7f3c9d2e4b8a1f6c0d5e2b9a3f7c1d4e8b2a5f"
}
```

> O nó trabalhou para encontrar um hash que começa com `0000` (4 zeros = dificuldade 4).
> Isso é o **Proof of Work** — prova que trabalho computacional foi feito.
> Como recompensa, **50 moedas foram creditadas** ao endereço de Alice.

---

### Passo 3 — Verificar o saldo de Alice

Substitua `<address_alice>` pelo `address` que você salvou no Passo 1.

```
GET http://localhost:5001/balance/1a7f3c9d2e4b8a1f6c0d5e2b9a3f7c1d4e8b2a5f
```

**Resposta:**
```json
{
  "address": "1a7f3c9d2e4b8a1f6c0d5e2b9a3f7c1d4e8b2a5f",
  "balance": 50.0,
  "utxos": [
    {
      "tx_id": "f7e8d9c0b1a2f3e4d5c6b7a8f9e0d1c2b3a4f5e6",
      "output_index": 0,
      "address": "1a7f3c9d2e4b8a1f6c0d5e2b9a3f7c1d4e8b2a5f",
      "amount": "50.00000000",
      "spent": false
    }
  ]
}
```

> 💡 Guarde o `tx_id` e o `output_index` do UTXO — você vai precisar deles para enviar moedas.

---

### Passo 4 — Criar a carteira do destinatário (Bob)

```
GET http://localhost:5001/wallet/new
```

**Resposta:**
```json
{
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQg...\n-----END PRIVATE KEY-----\n",
  "public_key": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE...\n-----END PUBLIC KEY-----\n",
  "address": "1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c"
}
```

> Salve o `address` de Bob — é para onde Alice vai enviar as moedas.

---

### Passo 5 — Alice envia 10 moedas para Bob

Agora Alice vai gastar o UTXO de 50 moedas:
- **10 moedas** vão para Bob
- **40 moedas** voltam para Alice como troco

```
POST http://localhost:5001/transaction/new
Content-Type: application/json
```

```json
{
  "sender": "1a7f3c9d2e4b8a1f6c0d5e2b9a3f7c1d4e8b2a5f",
  "public_key": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEqW3FKJA...\n-----END PUBLIC KEY-----\n",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQg...\n-----END PRIVATE KEY-----\n",
  "inputs": [
    {
      "tx_id": "f7e8d9c0b1a2f3e4d5c6b7a8f9e0d1c2b3a4f5e6",
      "output_index": 0
    }
  ],
  "outputs": [
    { "address": "1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c", "amount": 10.0 },
    { "address": "1a7f3c9d2e4b8a1f6c0d5e2b9a3f7c1d4e8b2a5f", "amount": 40.0 }
  ]
}
```

> ⚠️ **Atenção aos campos:**
> - `sender` → endereço de Alice (quem envia)
> - `inputs` → o UTXO que Alice vai gastar (o `tx_id` e `output_index` do Passo 3)
> - `outputs` → para onde vai o dinheiro: 10 para Bob + 40 de troco para Alice
> - A soma dos outputs (10 + 40 = 50) deve ser **igual ou menor** que o input (50)

**Resposta:**
```json
{
  "message": "Transação adicionada ao mempool",
  "tx_id": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"
}
```

> A transação está na **fila de espera (mempool)**. Ela ainda não foi confirmada — precisa ser incluída em um bloco.

---

### Passo 6 — Minerar o bloco com a transação

```
GET http://localhost:5001/mine?address=1a7f3c9d2e4b8a1f6c0d5e2b9a3f7c1d4e8b2a5f
```

**Resposta:**
```json
{
  "message": "Bloco minerado com sucesso!",
  "block_index": 3,
  "hash": "00001f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e",
  "difficulty": 4,
  "nonce": 12847,
  "merkle_root": "e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4",
  "transactions": 2,
  "miner_reward": 50.0
}
```

> O bloco 3 contém 2 transações: a coinbase (recompensa do minerador) + a transação de Alice para Bob.

---

### Passo 7 — Confirmar os saldos

**Saldo de Bob:**
```
GET http://localhost:5001/balance/1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c
```
```json
{
  "address": "1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c",
  "balance": 10.0,
  "utxos": [...]
}
```

**Saldo de Alice (troco):**
```
GET http://localhost:5001/balance/1a7f3c9d2e4b8a1f6c0d5e2b9a3f7c1d4e8b2a5f
```
```json
{
  "address": "1a7f3c9d2e4b8a1f6c0d5e2b9a3f7c1d4e8b2a5f",
  "balance": 40.0,
  "utxos": [...]
}
```

> ✅ Transação confirmada! Alice tem 40 moedas de troco e Bob tem 10 moedas.

---

## 📡 API Reference

### Resumo dos endpoints

| Método | Endpoint | O que faz |
|---|---|---|
| GET | `/wallet/new` | Cria uma nova carteira |
| GET | `/mine?address=<carteira>` | Minera um novo bloco e credita a recompensa ao endereço informado |
| GET | `/chain` | Retorna toda a blockchain |
| GET | `/validate` | Verifica se a cadeia é válida |
| POST | `/transaction/new` | Cria uma nova transação |
| GET | `/mempool` | Lista transações aguardando mineração |
| GET | `/balance/<address>` | Consulta saldo e UTXOs de um endereço |
| POST | `/nodes/register` | Registra outros nós na rede |
| GET | `/nodes` | Lista os nós conhecidos |
| GET | `/nodes/consensus` | Sincroniza com a cadeia mais longa |

---

### Carteira

#### `GET /wallet/new`
Gera um novo par de chaves criptográficas e um endereço.

**Resposta `201`**
```json
{
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "public_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----\n",
  "address": "1a7f3c9d2e4b8a1f6c0d5e2b9a3f7c1d4e8b2a5f"
}
```

---

### Mineração

#### `GET /mine?address=<carteira>`
Minera um novo bloco. Inclui todas as transações do mempool e gera automaticamente a recompensa de 50 moedas para o endereço informado.

| Parâmetro | Obrigatório | Descrição |
|---|---|---|
| `address` | Não | Endereço da carteira que receberá as 50 moedas. Se omitido, usa o endereço padrão do nó. |

**Exemplo:**
```
GET http://localhost:5001/mine?address=1a7f3c9d2e4b8a1f6c0d5e2b9a3f7c1d4e8b2a5f
```

**Resposta `200`**
```json
{
  "message": "Bloco minerado com sucesso!",
  "block_index": 2,
  "hash": "0000a3f7c2d1e9b4a8f5c0d3e7b2a1f6c9d4e8b3",
  "difficulty": 4,
  "nonce": 38291,
  "merkle_root": "d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3",
  "transactions": 1,
  "miner_reward": 50.0,
  "miner_address": "1a7f3c9d2e4b8a1f6c0d5e2b9a3f7c1d4e8b2a5f"
}
```

---

### Blockchain

#### `GET /chain`
Retorna todos os blocos da cadeia.

**Resposta `200`**
```json
{
  "chain": [
    {
      "index": 1,
      "timestamp": 1714000000.0,
      "hash": "0000genesis...",
      "previous_hash": "0000000000000000000000000000000000000000000000000000000000000000",
      "transactions": [],
      "difficulty": 4,
      "nonce": 12345,
      "merkle_root": "e3b0c44298fc..."
    }
  ],
  "length": 1
}
```

#### `GET /validate`
Verifica se a blockchain local está íntegra (nenhum bloco foi adulterado).

**Resposta `200`**
```json
{
  "valid": true,
  "blocks": 3
}
```

---

### Transações

#### `POST /transaction/new`
Cria uma transação assinada e a adiciona ao mempool.

**Corpo da requisição**
```json
{
  "sender": "<endereço de quem envia>",
  "public_key": "<chave pública de quem envia>",
  "private_key": "<chave privada de quem envia>",
  "inputs": [
    { "tx_id": "<id da transação de origem>", "output_index": 0 }
  ],
  "outputs": [
    { "address": "<endereço do destinatário>", "amount": 10.0 },
    { "address": "<endereço do remetente>",    "amount": 40.0 }
  ]
}
```

> O segundo output é o **troco** de volta para quem enviou. A soma dos outputs não pode ultrapassar a soma dos inputs.

**Resposta `201`**
```json
{
  "message": "Transação adicionada ao mempool",
  "tx_id": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"
}
```

**Erros possíveis**
```json
{ "error": "Assinatura inválida" }
{ "error": "UTXO ('abc123', 0) não encontrado ou já gasto" }
{ "error": "Outputs excedem inputs" }
```

#### `GET /mempool`
Lista as transações que estão aguardando ser incluídas no próximo bloco.

**Resposta `200`**
```json
{
  "mempool": [
    {
      "type": "transfer",
      "tx_id": "a1b2c3...",
      "sender": "1a7f3c...",
      "inputs": [...],
      "outputs": [...],
      "timestamp": 1714000100.0
    }
  ],
  "count": 1
}
```

---

### Saldo

#### `GET /balance/<address>`
Retorna o saldo total e a lista de UTXOs não gastos de um endereço.

**Exemplo:**
```
GET http://localhost:5001/balance/1a7f3c9d2e4b8a1f6c0d5e2b9a3f7c1d4e8b2a5f
```

**Resposta `200`**
```json
{
  "address": "1a7f3c9d2e4b8a1f6c0d5e2b9a3f7c1d4e8b2a5f",
  "balance": 50.0,
  "utxos": [
    {
      "tx_id": "f7e8d9c0b1a2f3e4d5c6b7a8f9e0d1c2b3a4f5e6",
      "output_index": 0,
      "address": "1a7f3c9d2e4b8a1f6c0d5e2b9a3f7c1d4e8b2a5f",
      "amount": "50.00000000",
      "spent": false
    }
  ]
}
```

---

### Nós e Consenso

#### `POST /nodes/register`
Registra outros nós da rede para que este nó possa se comunicar com eles.

**Corpo da requisição**
```json
{
  "nodes": [
    "http://node2:5002",
    "http://node3:5003"
  ]
}
```

**Resposta `201`**
```json
{
  "message": "Nós registrados",
  "nodes": ["http://node2:5002", "http://node3:5003"]
}
```

#### `GET /nodes`
Lista todos os nós que este nó conhece.

**Resposta `200`**
```json
{
  "nodes": ["http://node2:5002", "http://node3:5003"]
}
```

#### `GET /nodes/consensus`
Consulta todos os nós conhecidos e adota a cadeia mais longa que seja válida.

> Use este endpoint quando suspeitar que um nó ficou para trás (ex: após reiniciar um nó).

**Resposta `200` — cadeia substituída**
```json
{
  "replaced": true,
  "chain_length": 5
}
```

**Resposta `200` — cadeia já era a mais longa**
```json
{
  "replaced": false,
  "chain_length": 3
}
```

---

## 🗄 Banco de Dados

O PostgreSQL armazena três tabelas:

### Tabela `blocks` — os blocos minerados

| Coluna | Tipo | Descrição |
|---|---|---|
| `block_index` | INTEGER | Número do bloco na cadeia (altura) |
| `timestamp` | FLOAT | Momento da mineração (Unix timestamp) |
| `proof` | BIGINT | Valor acumulado do proof |
| `previous_hash` | VARCHAR(64) | Hash do bloco anterior — é o que "encadeia" os blocos |
| `merkle_root` | VARCHAR(64) | Resumo criptográfico de todas as transações do bloco |
| `hash` | VARCHAR(64) | Hash deste bloco (começa com zeros) |
| `difficulty` | INTEGER | Quantos zeros o hash precisava ter |
| `nonce` | BIGINT | Número que foi incrementado até o hash satisfazer a dificuldade |
| `transactions` | JSONB | Lista completa das transações em formato JSON |

### Tabela `utxos` — as "cédulas" não gastas

| Coluna | Tipo | Descrição |
|---|---|---|
| `tx_id` | VARCHAR(64) | ID da transação que criou este UTXO |
| `output_index` | INTEGER | Posição deste output dentro da transação |
| `address` | VARCHAR(130) | Endereço do dono deste UTXO |
| `amount` | NUMERIC(20,8) | Valor com 8 casas decimais (como o Bitcoin) |
| `spent` | BOOLEAN | `false` = disponível para gastar, `true` = já foi gasto |

### Tabela `nodes` — os nós conhecidos

| Coluna | Tipo | Descrição |
|---|---|---|
| `address` | VARCHAR(255) | URL completa do nó (ex: `http://node2:5002`) |

---

## 🔬 Conceitos Implementados

### UTXO (Unspent Transaction Output)
Ao invés de guardar um saldo, o sistema guarda todas as "cédulas" recebidas. Gastar uma cédula a consome inteiramente e gera troco. Isso torna impossível gastar a mesma moeda duas vezes.

### Carteiras Criptográficas (ECDSA secp256k1)
A mesma curva elíptica usada pelo Bitcoin real. A chave privada assina a transação, e qualquer um pode verificar a assinatura com a chave pública — sem precisar revelar a chave privada.

### Merkle Tree
Todas as transações de um bloco são resumidas em um único hash (a raiz). Isso permite verificar se uma transação pertence a um bloco sem precisar baixar o bloco inteiro.

### Proof of Work com Dificuldade Ajustável
O minerador precisa encontrar um número (nonce) tal que o hash do bloco comece com N zeros. A dificuldade é recalculada a cada 10 blocos para manter o tempo médio de mineração em ~10 segundos.

### Coinbase Transaction
O primeiro bloco de cada mineração cria moedas do nada — é assim que novas moedas entram em circulação. No Bitcoin real, a recompensa cai pela metade a cada 210.000 blocos (halving).

### Consenso Nakamoto
Se dois nós minerarem blocos ao mesmo tempo, a rede diverge temporariamente. O algoritmo resolve isso adotando sempre a cadeia mais longa que seja válida.
