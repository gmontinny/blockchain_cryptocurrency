import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://bitcoin:bitcoin@db:5432/bitcoindb")


def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Advisory lock garante que apenas um nó executa o DDL por vez
            cur.execute("SELECT pg_advisory_lock(1)")
            try:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS blocks (
                        id          SERIAL PRIMARY KEY,
                        block_index INTEGER UNIQUE NOT NULL,
                        timestamp   FLOAT NOT NULL,
                        proof       BIGINT NOT NULL,
                        previous_hash VARCHAR(64) NOT NULL,
                        merkle_root   VARCHAR(64) NOT NULL,
                        hash          VARCHAR(64) UNIQUE NOT NULL,
                        difficulty    INTEGER NOT NULL,
                        nonce         BIGINT NOT NULL,
                        transactions  JSONB NOT NULL DEFAULT '[]'
                    );

                    CREATE TABLE IF NOT EXISTS utxos (
                        tx_id        VARCHAR(64) NOT NULL,
                        output_index INTEGER NOT NULL,
                        address      VARCHAR(130) NOT NULL,
                        amount       NUMERIC(20, 8) NOT NULL,
                        spent        BOOLEAN NOT NULL DEFAULT FALSE,
                        PRIMARY KEY (tx_id, output_index)
                    );

                    CREATE TABLE IF NOT EXISTS nodes (
                        address VARCHAR(255) PRIMARY KEY
                    );

                    CREATE INDEX IF NOT EXISTS idx_utxos_address ON utxos(address, spent);
                """)
            finally:
                cur.execute("SELECT pg_advisory_unlock(1)")
        conn.commit()


def save_block(block: dict):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO blocks (block_index, timestamp, proof, previous_hash, merkle_root, hash, difficulty, nonce, transactions)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (block_index) DO NOTHING
            """, (
                block["index"], block["timestamp"], block["proof"],
                block["previous_hash"], block["merkle_root"], block["hash"],
                block["difficulty"], block["nonce"],
                json.dumps(block["transactions"])
            ))
        conn.commit()


def load_chain() -> list:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM blocks ORDER BY block_index ASC")
            rows = cur.fetchall()
    return [dict(r) | {"transactions": r["transactions"]} for r in rows]


def save_utxos(tx_id: str, outputs: list):
    with get_connection() as conn:
        with conn.cursor() as cur:
            for i, out in enumerate(outputs):
                cur.execute("""
                    INSERT INTO utxos (tx_id, output_index, address, amount, spent)
                    VALUES (%s, %s, %s, %s, FALSE)
                    ON CONFLICT DO NOTHING
                """, (tx_id, i, out["address"], out["amount"]))
        conn.commit()


def mark_utxos_spent(inputs: list):
    with get_connection() as conn:
        with conn.cursor() as cur:
            for inp in inputs:
                cur.execute(
                    "UPDATE utxos SET spent = TRUE WHERE tx_id = %s AND output_index = %s",
                    (inp["tx_id"], inp["output_index"])
                )
        conn.commit()


def get_utxos(address: str) -> list:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM utxos WHERE address = %s AND spent = FALSE",
                (address,)
            )
            return [dict(r) for r in cur.fetchall()]


def get_balance(address: str) -> float:
    utxos = get_utxos(address)
    return float(sum(u["amount"] for u in utxos))


def save_node(address: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO nodes (address) VALUES (%s) ON CONFLICT DO NOTHING", (address,))
        conn.commit()


def load_nodes() -> list:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT address FROM nodes")
            return [r["address"] for r in cur.fetchall()]
