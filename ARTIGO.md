# Implementação Didática de uma Blockchain Inspirada no Bitcoin: Conceitos, Arquitetura e Experimentação Prática

**Área:** Ciência da Computação — Sistemas Distribuídos, Segurança e Criptografia

---

## Resumo

Este artigo apresenta a implementação de uma blockchain funcional inspirada no protocolo Bitcoin, desenvolvida com fins educacionais para cursos de graduação e pós-graduação em Ciência da Computação, Engenharia de Software e áreas correlatas. O sistema implementa os principais mecanismos do Bitcoin original: modelo UTXO (Unspent Transaction Output), carteiras criptográficas baseadas em ECDSA com a curva secp256k1, Merkle Tree, Proof of Work com dificuldade ajustável e consenso Nakamoto entre múltiplos nós. A infraestrutura é conteinerizada com Docker e utiliza PostgreSQL como camada de persistência. O objetivo é fornecer um ambiente reproduzível onde estudantes possam observar, experimentar e compreender os fundamentos técnicos que sustentam as criptomoedas modernas.

**Palavras-chave:** Blockchain, Bitcoin, UTXO, ECDSA, Proof of Work, Merkle Tree, Sistemas Distribuídos, Criptografia.

---

## Abstract

This paper presents the implementation of a functional blockchain inspired by the Bitcoin protocol, developed for educational purposes in undergraduate and graduate courses in Computer Science, Software Engineering, and related fields. The system implements the main mechanisms of the original Bitcoin: the UTXO (Unspent Transaction Output) model, cryptographic wallets based on ECDSA with the secp256k1 curve, Merkle Tree, Proof of Work with adjustable difficulty, and Nakamoto consensus among multiple nodes. The infrastructure is containerized with Docker and uses PostgreSQL as the persistence layer. The goal is to provide a reproducible environment where students can observe, experiment with, and understand the technical foundations that underpin modern cryptocurrencies.

**Keywords:** Blockchain, Bitcoin, UTXO, ECDSA, Proof of Work, Merkle Tree, Distributed Systems, Cryptography.

---

## 1. Introdução

Desde a publicação do whitepaper de Satoshi Nakamoto em 2008, intitulado *"Bitcoin: A Peer-to-Peer Electronic Cash System"*, a tecnologia blockchain passou de uma proposta acadêmica para a base de um ecossistema financeiro global que movimenta trilhões de dólares. Apesar de sua relevância, os mecanismos internos do Bitcoin permanecem opacos para grande parte dos profissionais de tecnologia, em parte pela ausência de implementações didáticas que traduzam o protocolo original em código compreensível e executável.

O ensino de blockchain em ambientes acadêmicos enfrenta um desafio recorrente: a distância entre a teoria descrita nos livros e a experiência prática de operar uma rede distribuída real. Ferramentas como o Bitcoin Core são complexas demais para fins pedagógicos, enquanto simulações simplificadas frequentemente omitem os mecanismos mais importantes, como o modelo UTXO e a criptografia de chave pública.

Este trabalho apresenta uma implementação completa e funcional de uma blockchain inspirada no Bitcoin, desenvolvida em Python com Flask, PostgreSQL e Docker. O sistema não é uma abstração — ele implementa os mesmos algoritmos criptográficos, o mesmo modelo de transações e o mesmo mecanismo de consenso do Bitcoin original, em escala reduzida e com código legível.

O artigo está organizado da seguinte forma: a Seção 2 apresenta o contexto histórico e os fundamentos teóricos; a Seção 3 descreve a arquitetura do sistema; as Seções 4 a 8 detalham cada componente técnico com trechos de código; a Seção 9 demonstra o sistema em operação; a Seção 10 apresenta as conclusões; e a Seção 11 lista as referências.

---

## 2. Fundamentação Teórica

### 2.1 O Problema do Gasto Duplo

O problema central que o Bitcoin resolve é o **gasto duplo** (*double-spending*): como garantir que uma unidade de moeda digital não seja gasta mais de uma vez, sem depender de uma autoridade central como um banco?

Em sistemas físicos, o problema não existe — uma nota de dinheiro não pode estar em dois lugares ao mesmo tempo. Em sistemas digitais, um arquivo pode ser copiado infinitamente. A solução de Nakamoto foi criar um **livro-caixa público e imutável** (a blockchain), onde todas as transações são registradas de forma que qualquer tentativa de alteração seja detectável por qualquer participante da rede.

### 2.2 Estrutura de um Bloco

Um bloco na blockchain é uma estrutura de dados que agrupa um conjunto de transações validadas. Cada bloco contém:

- **Index:** posição do bloco na cadeia (altura)
- **Timestamp:** momento da criação
- **Transactions:** lista de transações incluídas
- **Previous Hash:** hash do bloco anterior — o elo que forma a cadeia
- **Merkle Root:** resumo criptográfico de todas as transações
- **Nonce:** número encontrado pelo minerador para satisfazer o Proof of Work
- **Difficulty:** número de zeros exigidos no início do hash
- **Hash:** impressão digital única deste bloco

A propriedade fundamental é que qualquer alteração em qualquer campo de qualquer bloco invalida o hash daquele bloco e de todos os blocos subsequentes, tornando a adulteração computacionalmente inviável.

### 2.3 Funções de Hash Criptográfico

O SHA-256 (Secure Hash Algorithm 256 bits) é a função de hash utilizada pelo Bitcoin e por esta implementação. Suas propriedades essenciais são:

- **Determinismo:** a mesma entrada sempre produz a mesma saída
- **Efeito avalanche:** uma pequena mudança na entrada altera completamente a saída
- **Irreversibilidade:** é computacionalmente inviável obter a entrada a partir da saída
- **Resistência a colisões:** é computacionalmente inviável encontrar duas entradas com a mesma saída

Essas propriedades são o que tornam o hash adequado tanto para encadear blocos quanto para o Proof of Work.

### 2.4 Criptografia de Chave Pública

O Bitcoin utiliza criptografia assimétrica baseada em **curvas elípticas** (Elliptic Curve Cryptography — ECC). O par de chaves funciona da seguinte forma:

- A **chave privada** é um número aleatório de 256 bits, mantido em segredo pelo dono
- A **chave pública** é derivada matematicamente da chave privada através de operações na curva elíptica
- O **endereço** é derivado da chave pública através de funções de hash (SHA-256 seguido de RIPEMD-160)

A propriedade fundamental é que a derivação é **unidirecional**: é trivial calcular a chave pública a partir da privada, mas computacionalmente inviável fazer o caminho inverso.

---

## 3. Arquitetura do Sistema

### 3.1 Visão Geral

O sistema é composto por três nós independentes que se comunicam via HTTP e compartilham um banco de dados PostgreSQL. Cada nó é uma instância idêntica da aplicação, diferenciada apenas por variáveis de ambiente.

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

**Figura 1** — Arquitetura da rede com 3 nós e banco de dados compartilhado.

### 3.2 Separação de Responsabilidades

O projeto é organizado em módulos com responsabilidades bem definidas:

| Módulo | Responsabilidade |
|---|---|
| `blockchain.py` | Estrutura do bloco, Proof of Work, Merkle Tree, validação da cadeia |
| `wallet.py` | Geração de carteiras, assinatura e verificação ECDSA |
| `transaction.py` | Modelo UTXO, criação e validação de transações |
| `database.py` | Persistência no PostgreSQL: blocos, UTXOs, nós |
| `routes.py` | API REST Flask com todos os endpoints |
| `main.py` | Entrypoint com retry de conexão ao banco |

**Tabela 1** — Módulos do sistema e suas responsabilidades.

### 3.3 Infraestrutura com Docker

A conteinerização garante que o ambiente seja idêntico em qualquer máquina. O `docker-compose.yml` define os quatro serviços:

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: bitcoin
      POSTGRES_PASSWORD: bitcoin
      POSTGRES_DB: bitcoindb
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U bitcoin -d bitcoindb"]
      interval: 5s
      retries: 10

  node1:
    build: .
    environment:
      DATABASE_URL: postgresql://bitcoin:bitcoin@db:5432/bitcoindb
      PORT: 5001
    depends_on:
      db:
        condition: service_healthy
```

O `healthcheck` do banco garante que os nós só iniciam após o PostgreSQL estar pronto para aceitar conexões, evitando falhas de inicialização em race conditions.

### 3.4 Persistência e Concorrência

Um desafio específico desta arquitetura é que os três nós iniciam simultaneamente e todos tentam criar as tabelas no banco. Para evitar o erro de `UniqueViolation` por race condition no DDL do PostgreSQL, a inicialização utiliza um **advisory lock**:

```python
def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_advisory_lock(1)")
            try:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS blocks ( ... );
                    CREATE TABLE IF NOT EXISTS utxos  ( ... );
                    CREATE TABLE IF NOT EXISTS nodes  ( ... );
                """)
            finally:
                cur.execute("SELECT pg_advisory_unlock(1)")
        conn.commit()
```

O `pg_advisory_lock(1)` é um mecanismo do PostgreSQL que serializa o acesso: apenas um processo executa o bloco DDL por vez, os demais aguardam na fila. O `finally` garante que o lock seja sempre liberado, mesmo em caso de erro.

---

## 4. Carteiras Criptográficas

### 4.1 A Curva Elíptica secp256k1

O Bitcoin utiliza a curva elíptica **secp256k1**, definida pela equação:

```
y² = x³ + 7  (mod p)
```

onde `p` é um primo de 256 bits. Esta curva foi escolhida por Satoshi Nakamoto por suas propriedades de eficiência computacional e por não ter sido gerada por nenhuma autoridade central, reduzindo o risco de backdoors.

A operação fundamental é a **multiplicação escalar**: dado um ponto gerador `G` na curva e uma chave privada `k` (número inteiro), a chave pública é `K = k × G`. Esta operação é eficiente em uma direção e computacionalmente inviável na direção inversa — o chamado **problema do logaritmo discreto em curvas elípticas**.

### 4.2 Implementação da Carteira

```python
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
import hashlib, binascii

def generate_wallet() -> dict:
    private_key = ec.generate_private_key(ec.SECP256K1(), default_backend())
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption()
    ).decode()

    public_pem = public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

    address = _public_key_to_address(public_pem)
    return {"private_key": private_pem, "public_key": public_pem, "address": address}
```

### 4.3 Derivação do Endereço

O endereço é derivado da chave pública através de duas funções de hash em sequência, seguindo o padrão do Bitcoin:

```python
def _public_key_to_address(public_pem: str) -> str:
    pub_bytes = public_pem.encode()
    sha256  = hashlib.sha256(pub_bytes).digest()
    ripemd  = hashlib.new("ripemd160", sha256).digest()
    return "1" + binascii.hexlify(ripemd).decode()
```

O uso de duas funções de hash em sequência (SHA-256 → RIPEMD-160) serve a dois propósitos: reduzir o tamanho do endereço (de 256 para 160 bits) e adicionar uma camada extra de segurança — mesmo que uma vulnerabilidade seja descoberta no SHA-256, o RIPEMD-160 ainda protege a chave pública.

### 4.4 Assinatura Digital ECDSA

A assinatura digital garante que apenas o dono da chave privada pode autorizar uma transação:

```python
def sign_transaction(private_pem: str, data: str) -> str:
    private_key = serialization.load_pem_private_key(
        private_pem.encode(), password=None, backend=default_backend()
    )
    signature = private_key.sign(data.encode(), ec.ECDSA(hashes.SHA256()))
    return binascii.hexlify(signature).decode()

def verify_signature(public_pem: str, data: str, signature_hex: str) -> bool:
    try:
        public_key = serialization.load_pem_public_key(
            public_pem.encode(), backend=default_backend()
        )
        public_key.verify(
            binascii.unhexlify(signature_hex),
            data.encode(),
            ec.ECDSA(hashes.SHA256())
        )
        return True
    except (InvalidSignature, Exception):
        return False
```

O algoritmo ECDSA (Elliptic Curve Digital Signature Algorithm) produz uma assinatura que:

1. Só pode ser gerada por quem possui a chave privada
2. Pode ser verificada por qualquer pessoa com a chave pública
3. É única para cada combinação de mensagem e chave privada
4. Invalida qualquer tentativa de alterar a mensagem após a assinatura

---

## 5. Modelo UTXO e Transações

### 5.1 O Modelo UTXO

O Bitcoin não armazena saldos. Em vez disso, armazena **outputs de transações não gastos** (UTXOs — Unspent Transaction Outputs). O saldo de um endereço é calculado dinamicamente como a soma de todos os UTXOs que pertencem a ele.

Esta abordagem tem vantagens importantes sobre o modelo de conta (usado pelo Ethereum, por exemplo):

- **Prevenção de gasto duplo:** cada UTXO só pode ser gasto uma vez; após ser consumido como input, é marcado como gasto
- **Paralelismo:** transações que consomem UTXOs diferentes podem ser validadas em paralelo
- **Privacidade:** facilita o uso de endereços diferentes para cada transação
- **Auditabilidade:** o histórico completo de cada "cédula" pode ser rastreado desde sua criação

### 5.2 Analogia com Cédulas Físicas

O modelo UTXO é análogo ao uso de cédulas físicas:

```
Estado inicial:
  Alice possui: UTXO_A = 50 moedas

Alice envia 10 moedas para Bob:
  Input:   UTXO_A (50 moedas) — consumido inteiramente
  Output1: 10 moedas → Bob    (novo UTXO de Bob)
  Output2: 40 moedas → Alice  (troco, novo UTXO de Alice)

Estado final:
  Alice possui: UTXO_B = 40 moedas  (troco)
  Bob   possui: UTXO_C = 10 moedas  (recebido)
  UTXO_A: marcado como gasto (spent = true)
```

**Figura 2** — Fluxo de consumo e criação de UTXOs em uma transação.

### 5.3 Implementação das Transações

```python
MINING_REWARD = 50.0

def create_coinbase_tx(miner_address: str, block_index: int) -> dict:
    tx = {
        "type": "coinbase",
        "inputs": [],
        "outputs": [{"address": miner_address, "amount": MINING_REWARD}],
        "timestamp": time.time(),
        "block_index": block_index,
    }
    tx["tx_id"] = compute_tx_id(tx)
    return tx

def create_transaction(sender_address, public_key, inputs, outputs, private_key):
    tx = {
        "type": "transfer",
        "sender": sender_address,
        "public_key": public_key,
        "inputs": inputs,
        "outputs": outputs,
        "timestamp": time.time(),
    }
    tx_data = json.dumps(tx, sort_keys=True)
    tx["signature"] = sign_transaction(private_key, tx_data)
    tx["tx_id"] = compute_tx_id(tx)
    return tx
```

A **transação coinbase** é especial: não possui inputs e cria moedas do nada. É o mecanismo pelo qual novas moedas entram em circulação — a recompensa do minerador. No Bitcoin real, essa recompensa é reduzida pela metade a cada 210.000 blocos (evento chamado de *halving*).

### 5.4 Validação de Transações

A validação verifica três condições em sequência:

```python
def validate_transaction(tx: dict, get_utxos_fn) -> tuple[bool, str]:
    if tx.get("type") == "coinbase":
        return True, "ok"

    # 1. Verificar assinatura criptográfica
    tx_data = json.dumps(
        {k: v for k, v in tx.items() if k not in ("signature", "tx_id")},
        sort_keys=True
    )
    if not verify_signature(tx["public_key"], tx_data, tx["signature"]):
        return False, "Assinatura inválida"

    # 2. Verificar se os UTXOs existem e não foram gastos
    utxos = {(u["tx_id"], u["output_index"]): u
             for u in get_utxos_fn(tx["sender"])}
    input_total = 0.0
    for inp in tx["inputs"]:
        key = (inp["tx_id"], inp["output_index"])
        if key not in utxos:
            return False, f"UTXO {key} não encontrado ou já gasto"
        input_total += float(utxos[key]["amount"])

    # 3. Verificar que outputs não excedem inputs
    output_total = sum(o["amount"] for o in tx["outputs"])
    if output_total > input_total:
        return False, "Outputs excedem inputs"

    return True, "ok"
```

As três verificações correspondem às três garantias fundamentais do sistema:

1. **Autenticidade:** apenas o dono da chave privada pode criar a transação
2. **Disponibilidade:** o dinheiro existe e não foi gasto antes
3. **Conservação:** não é possível criar moedas do nada em transações comuns

### 5.5 Persistência dos UTXOs no PostgreSQL

```sql
CREATE TABLE utxos (
    tx_id        VARCHAR(64)    NOT NULL,
    output_index INTEGER        NOT NULL,
    address      VARCHAR(130)   NOT NULL,
    amount       NUMERIC(20, 8) NOT NULL,
    spent        BOOLEAN        NOT NULL DEFAULT FALSE,
    PRIMARY KEY (tx_id, output_index)
);

CREATE INDEX idx_utxos_address ON utxos(address, spent);
```

O índice em `(address, spent)` é fundamental para a performance: a consulta de saldo filtra exatamente por esses dois campos. Sem o índice, uma consulta de saldo exigiria varredura completa da tabela.

---

## 6. Proof of Work e Merkle Tree

### 6.1 O Problema do Proof of Work

O Proof of Work (PoW) resolve o problema de **quem tem o direito de adicionar o próximo bloco** à cadeia. Em vez de uma autoridade central, o direito é conquistado por quem primeiro resolver um problema computacional difícil — encontrar um número (nonce) tal que o hash do bloco comece com N zeros.

A assimetria é a chave: **encontrar** o nonce é difícil (requer tentativas aleatórias), mas **verificar** que o nonce é correto é trivial (basta calcular o hash uma vez). Isso permite que qualquer nó da rede verifique instantaneamente o trabalho realizado pelo minerador.

### 6.2 Implementação do Proof of Work

```python
def proof_of_work(block: dict, difficulty: int) -> dict:
    target = "0" * difficulty
    block["nonce"] = 0
    while True:
        block["hash"] = hash_block(block)
        if block["hash"].startswith(target):
            return block
        block["nonce"] += 1
```

O minerador incrementa o nonce indefinidamente até que o hash do bloco comece com `difficulty` zeros. Com dificuldade 4, a probabilidade de sucesso em cada tentativa é de 1/16⁴ = 1/65.536, exigindo em média 65.536 tentativas por bloco.

### 6.3 Dificuldade Ajustável

O Bitcoin ajusta a dificuldade a cada 2.016 blocos para manter o tempo médio de mineração em 10 minutos. Esta implementação usa o mesmo princípio em escala menor:

```python
BLOCK_TIME_TARGET = 10          # segundos
DIFFICULTY_ADJUSTMENT_INTERVAL = 10  # blocos

def calculate_difficulty(chain: list) -> int:
    if len(chain) < DIFFICULTY_ADJUSTMENT_INTERVAL:
        return DIFFICULTY_TARGET

    last  = chain[-1]
    first = chain[-DIFFICULTY_ADJUSTMENT_INTERVAL]
    elapsed  = last["timestamp"] - first["timestamp"]
    expected = BLOCK_TIME_TARGET * DIFFICULTY_ADJUSTMENT_INTERVAL

    if elapsed < expected / 2:   # minerando rápido demais
        return last["difficulty"] + 1
    if elapsed > expected * 2:   # minerando lento demais
        return max(1, last["difficulty"] - 1)
    return last["difficulty"]
```

Se os últimos 10 blocos foram minerados em menos da metade do tempo esperado, a dificuldade aumenta em 1. Se levaram mais que o dobro, diminui em 1. Isso mantém o sistema estável independentemente do poder computacional disponível.

### 6.4 Merkle Tree

A Merkle Tree é uma estrutura de dados em árvore onde cada nó folha contém o hash de uma transação, e cada nó interno contém o hash da concatenação de seus dois filhos. A raiz da árvore (Merkle Root) é um resumo criptográfico de todas as transações do bloco.

```
Transações: [TX1, TX2, TX3, TX4]

Nível 0 (folhas):  H1=hash(TX1)  H2=hash(TX2)  H3=hash(TX3)  H4=hash(TX4)
                        │              │              │              │
Nível 1:           H12=hash(H1+H2)              H34=hash(H3+H4)
                              │                        │
Nível 2 (raiz):          MR=hash(H12+H34)
```

**Figura 3** — Estrutura da Merkle Tree com 4 transações.

```python
def merkle_root(tx_ids: list) -> str:
    if not tx_ids:
        return hashlib.sha256(b"").hexdigest()
    layer = tx_ids[:]
    while len(layer) > 1:
        if len(layer) % 2 != 0:
            layer.append(layer[-1])  # duplica o último se ímpar
        layer = [
            hashlib.sha256((layer[i] + layer[i+1]).encode()).hexdigest()
            for i in range(0, len(layer), 2)
        ]
    return layer[0]
```

A propriedade fundamental da Merkle Tree é que qualquer alteração em qualquer transação altera a raiz. Isso permite que o cabeçalho do bloco (que contém a Merkle Root) seja suficiente para verificar a integridade de todas as transações, sem precisar armazená-las todas.

### 6.5 Validação da Cadeia

A validação percorre todos os blocos verificando quatro condições:

```python
def is_chain_valid(chain: list) -> bool:
    for i in range(1, len(chain)):
        block = chain[i]
        prev  = chain[i - 1]

        # 1. Encadeamento: previous_hash deve bater com o hash do bloco anterior
        if block["previous_hash"] != prev["hash"]:
            return False

        # 2. Integridade: o hash armazenado deve ser o hash real do bloco
        if block["hash"] != hash_block(block):
            return False

        # 3. Proof of Work: o hash deve satisfazer a dificuldade
        if not block["hash"].startswith("0" * block["difficulty"]):
            return False

        # 4. Merkle Root: o resumo das transações deve ser correto
        computed = merkle_root([tx["tx_id"] for tx in block["transactions"]])
        if block["merkle_root"] != computed:
            return False

    return True
```

---

## 7. Consenso Nakamoto

### 7.1 O Problema da Divergência

Em uma rede distribuída, dois nós podem minerar blocos válidos ao mesmo tempo, criando uma **bifurcação** (*fork*) temporária na cadeia. Cada nó passa a ter uma versão diferente da blockchain. O sistema precisa de um mecanismo para convergir para uma única versão canônica.

```
Nó 1:  Bloco 1 → Bloco 2 → Bloco 3A
Nó 2:  Bloco 1 → Bloco 2 → Bloco 3B  ← fork!
```

### 7.2 A Regra da Cadeia Mais Longa

O consenso Nakamoto resolve o problema com uma regra simples: **a cadeia válida mais longa é a cadeia canônica**. "Mais longa" significa mais blocos, o que implica mais trabalho computacional acumulado.

```python
@router.route("/nodes/consensus", methods=["GET"])
def consensus():
    nodes = db.load_nodes()
    local_chain = _get_chain()
    best_chain = local_chain
    replaced = False

    for node in nodes:
        try:
            resp = requests.get(f"{node}/chain", timeout=5)
            remote_chain = resp.json()["chain"]
            if (len(remote_chain) > len(best_chain)
                    and bc.is_chain_valid(remote_chain)):
                best_chain = remote_chain
                replaced = True
        except requests.RequestException:
            continue

    if replaced:
        for block in best_chain:
            db.save_block(block)

    return jsonify({"replaced": replaced, "chain_length": len(best_chain)})
```

O nó consulta todos os peers registrados, valida cada cadeia recebida e adota a mais longa que seja válida. A validação é obrigatória — um nó malicioso poderia enviar uma cadeia longa mas inválida.

### 7.3 Implicações de Segurança

A regra da cadeia mais longa implica que para **reescrever a história** da blockchain, um atacante precisaria recomputar todos os blocos a partir do ponto que deseja alterar, e fazê-lo mais rápido do que a rede honesta continua adicionando blocos. Isso exigiria controlar mais de 50% do poder computacional total da rede — o chamado **ataque dos 51%**.

No Bitcoin real, com milhares de mineradores ao redor do mundo, esse ataque é economicamente inviável. Em redes menores (como esta implementação local), o ataque seria trivial — o que reforça a importância do tamanho da rede para a segurança do sistema.

---

## 8. API REST e Fluxo de Operação

### 8.1 Endpoints Disponíveis

A API expõe dez endpoints que cobrem todas as operações da blockchain:

| Método | Endpoint | Função |
|---|---|---|
| GET | `/wallet/new` | Gera par de chaves e endereço |
| GET | `/mine?address=<addr>` | Minera bloco e credita recompensa |
| GET | `/chain` | Retorna a blockchain completa |
| GET | `/validate` | Verifica integridade da cadeia |
| POST | `/transaction/new` | Cria e assina transação |
| GET | `/mempool` | Lista transações pendentes |
| GET | `/balance/<address>` | Consulta saldo e UTXOs |
| POST | `/nodes/register` | Registra peers na rede |
| GET | `/nodes` | Lista nós conhecidos |
| GET | `/nodes/consensus` | Executa algoritmo de consenso |

**Tabela 2** — Endpoints da API REST.

### 8.2 Mempool

O mempool é a fila de espera das transações. Uma transação validada entra no mempool e aguarda ser incluída no próximo bloco minerado. Este mecanismo desacopla a criação de transações da mineração de blocos:

```python
mempool: list = []

@router.route("/transaction/new", methods=["POST"])
def new_transaction():
    data = request.get_json()
    tx = create_transaction(
        data["sender"], data["public_key"],
        data["inputs"], data["outputs"], data["private_key"]
    )
    valid, msg = validate_transaction(tx, db.get_utxos)
    if not valid:
        return jsonify({"error": msg}), 400

    mempool.append(tx)
    return jsonify({"tx_id": tx["tx_id"]}), 201
```

No Bitcoin real, o mempool também é usado para priorização por taxa de transação (*fee*): mineradores escolhem as transações com maior taxa para maximizar sua receita. Esta implementação não cobra taxas, mas a estrutura do mempool é idêntica.

---

## 9. Demonstração Prática

### 9.1 Inicialização do Ambiente

Com Docker instalado, o ambiente completo é iniciado com um único comando:

```bash
docker-compose up --build
```

Após a inicialização, três nós estão disponíveis em `localhost:5001`, `localhost:5002` e `localhost:5003`.

### 9.2 Ciclo Completo de uma Transação

O fluxo a seguir demonstra todos os conceitos em operação:

**Passo 1 — Criar carteira de Alice:**
```
GET http://localhost:5001/wallet/new

Resposta:
{
  "address":     "1a7f3c9d2e4b8a1f6c0d5e2b9a3f7c1d4e8b2a5f",
  "public_key":  "-----BEGIN PUBLIC KEY-----\nMFkwEwYH...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIGHAgEA..."
}
```

**Passo 2 — Alice minera um bloco e recebe 50 moedas:**
```
GET http://localhost:5001/mine?address=1a7f3c9d2e4b8a1f6c0d5e2b9a3f7c1d4e8b2a5f

Resposta:
{
  "block_index":   2,
  "hash":          "0000a3f7c2d1e9b4a8f5c0d3e7b2a1f6...",
  "difficulty":    4,
  "nonce":         38291,
  "miner_reward":  50.0,
  "miner_address": "1a7f3c9d2e4b8a1f6c0d5e2b9a3f7c1d4e8b2a5f"
}
```

O hash começa com `0000`, confirmando que o Proof of Work foi satisfeito com dificuldade 4.

**Passo 3 — Verificar saldo de Alice:**
```
GET http://localhost:5001/balance/1a7f3c9d2e4b8a1f6c0d5e2b9a3f7c1d4e8b2a5f

Resposta:
{
  "balance": 50.0,
  "utxos": [{
    "tx_id":        "f7e8d9c0b1a2f3e4d5c6b7a8f9e0d1c2b3a4f5e6",
    "output_index": 0,
    "amount":       "50.00000000",
    "spent":        false
  }]
}
```

**Passo 4 — Criar carteira de Bob e enviar 10 moedas:**
```
POST http://localhost:5001/transaction/new

{
  "sender":      "1a7f3c9d2e4b8a1f6c0d5e2b9a3f7c1d4e8b2a5f",
  "public_key":  "-----BEGIN PUBLIC KEY-----\n...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "inputs":  [{ "tx_id": "f7e8d9c0...", "output_index": 0 }],
  "outputs": [
    { "address": "1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c", "amount": 10.0 },
    { "address": "1a7f3c9d2e4b8a1f6c0d5e2b9a3f7c1d4e8b2a5f", "amount": 40.0 }
  ]
}

Resposta:
{
  "message": "Transação adicionada ao mempool",
  "tx_id":   "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"
}
```

**Passo 5 — Minerar o bloco com a transação:**
```
GET http://localhost:5001/mine?address=1a7f3c9d2e4b8a1f6c0d5e2b9a3f7c1d4e8b2a5f

Resposta:
{
  "block_index":  3,
  "transactions": 2,   ← coinbase + transação de Alice para Bob
  "miner_reward": 50.0
}
```

**Passo 6 — Confirmar saldos finais:**
```
Alice: balance = 90.0  (40 de troco + 50 de recompensa de mineração)
Bob:   balance = 10.0  (recebido de Alice)
```

### 9.3 Verificação da Integridade

```
GET http://localhost:5001/validate

Resposta:
{
  "valid":  true,
  "blocks": 3
}
```

### 9.4 Sincronização entre Nós

Para demonstrar o consenso, registre os nós entre si e execute a sincronização:

```
POST http://localhost:5001/nodes/register
{ "nodes": ["http://node2:5002", "http://node3:5003"] }

GET http://localhost:5002/nodes/consensus
{ "replaced": true, "chain_length": 3 }
```

O nó 2, que não havia minerado nenhum bloco, adota a cadeia do nó 1 por ser mais longa.

---

## 10. Conclusão

Este trabalho apresentou a implementação de uma blockchain funcional que reproduz os mecanismos fundamentais do Bitcoin em um ambiente educacional controlado. Os resultados demonstram que é possível implementar, em aproximadamente 300 linhas de código Python, os mesmos algoritmos que sustentam uma rede financeira global.

Os principais conceitos implementados e validados foram:

- **UTXO:** o modelo de "cédulas digitais" que previne o gasto duplo sem autoridade central
- **ECDSA secp256k1:** a mesma criptografia de chave pública do Bitcoin real, garantindo autenticidade e não-repúdio
- **Merkle Tree:** estrutura que permite verificar a integridade de transações de forma eficiente
- **Proof of Work com dificuldade ajustável:** mecanismo que torna a reescrita da história computacionalmente inviável
- **Consenso Nakamoto:** regra da cadeia mais longa que resolve divergências em redes distribuídas

Do ponto de vista pedagógico, a principal contribuição é a **observabilidade**: cada conceito pode ser verificado diretamente via API, com respostas JSON que expõem o estado interno do sistema. Um estudante pode criar uma carteira, minerar um bloco, inspecionar o hash, alterar manualmente um registro no banco e observar a validação falhar — experiências que solidificam a compreensão de forma que nenhuma leitura teórica consegue substituir.

Como trabalhos futuros, destacam-se: a implementação de taxas de transação e priorização no mempool; a adição de *Simplified Payment Verification* (SPV) para clientes leves; a implementação do protocolo P2P de propagação de transações entre nós; e a exploração de mecanismos alternativos de consenso como Proof of Stake.

A tecnologia blockchain, compreendida em seus fundamentos, revela-se não como uma solução mágica para todos os problemas, mas como uma engenharia elegante de incentivos, criptografia e teoria dos jogos — cujo entendimento profundo é cada vez mais relevante para profissionais de tecnologia.

---

## 11. Referências

NAKAMOTO, S. **Bitcoin: A Peer-to-Peer Electronic Cash System**. 2008. Disponível em: https://bitcoin.org/bitcoin.pdf. Acesso em: out. 2024.

ANTONOPOULOS, A. M. **Mastering Bitcoin: Programming the Open Blockchain**. 2. ed. Sebastopol: O'Reilly Media, 2017.

ANTONOPOULOS, A. M.; WOOD, G. **Mastering Ethereum: Building Smart Contracts and DApps**. Sebastopol: O'Reilly Media, 2018.

BACK, A. **Hashcash — A Denial of Service Counter-Measure**. 2002. Disponível em: http://www.hashcash.org/papers/hashcash.pdf. Acesso em: out. 2024.

MERKLE, R. C. **A Digital Signature Based on a Conventional Encryption Function**. In: *Advances in Cryptology — CRYPTO '87*. Lecture Notes in Computer Science, v. 293. Springer, Berlin, Heidelberg, 1988. p. 369–378.

JOHNSON, D.; MENEZES, A.; VANSTONE, S. **The Elliptic Curve Digital Signature Algorithm (ECDSA)**. *International Journal of Information Security*, v. 1, n. 1, p. 36–63, 2001.

STANDARDS FOR EFFICIENT CRYPTOGRAPHY GROUP. **SEC 2: Recommended Elliptic Curve Domain Parameters**. Version 2.0. 2010. Disponível em: https://www.secg.org/sec2-v2.pdf. Acesso em: out. 2024.

RIVEST, R. L. **The MD5 Message-Digest Algorithm**. RFC 1321. Internet Engineering Task Force, 1992.

TANENBAUM, A. S.; VAN STEEN, M. **Distributed Systems: Principles and Paradigms**. 3. ed. Pearson, 2017.

SWAN, M. **Blockchain: Blueprint for a New Economy**. Sebastopol: O'Reilly Media, 2015.

NARAYANAN, A. et al. **Bitcoin and Cryptocurrency Technologies**. Princeton: Princeton University Press, 2016. Disponível em: https://bitcoinbook.cs.princeton.edu. Acesso em: out. 2024.

POSTGRESQL GLOBAL DEVELOPMENT GROUP. **PostgreSQL 16 Documentation: Advisory Locks**. 2024. Disponível em: https://www.postgresql.org/docs/16/explicit-locking.html. Acesso em: out. 2024.
