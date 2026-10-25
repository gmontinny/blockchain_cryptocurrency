import hashlib
import json
import time
from datetime import datetime, timezone

DIFFICULTY_TARGET = 4
BLOCK_TIME_TARGET = 10
DIFFICULTY_ADJUSTMENT_INTERVAL = 10


def merkle_root(tx_ids: list) -> str:
    if not tx_ids:
        return hashlib.sha256(b"").hexdigest()
    layer = tx_ids[:]
    while len(layer) > 1:
        if len(layer) % 2 != 0:
            layer.append(layer[-1])
        layer = [
            hashlib.sha256((layer[i] + layer[i + 1]).encode()).hexdigest()
            for i in range(0, len(layer), 2)
        ]
    return layer[0]


def hash_block(block: dict) -> str:
    block_copy = {k: v for k, v in block.items() if k != "hash"}
    return hashlib.sha256(json.dumps(block_copy, sort_keys=True).encode()).hexdigest()


def proof_of_work(block: dict, difficulty: int) -> dict:
    target = "0" * difficulty
    block["nonce"] = 0
    while True:
        block["hash"] = hash_block(block)
        if block["hash"].startswith(target):
            return block
        block["nonce"] += 1


def calculate_difficulty(chain: list) -> int:
    if len(chain) < DIFFICULTY_ADJUSTMENT_INTERVAL:
        return DIFFICULTY_TARGET

    last = chain[-1]
    first = chain[-DIFFICULTY_ADJUSTMENT_INTERVAL]
    elapsed = (last["timestamp"] - first["timestamp"])
    expected = BLOCK_TIME_TARGET * DIFFICULTY_ADJUSTMENT_INTERVAL

    if elapsed < expected / 2:
        return last["difficulty"] + 1
    if elapsed > expected * 2:
        return max(1, last["difficulty"] - 1)
    return last["difficulty"]


def create_genesis_block() -> dict:
    block = {
        "index": 1,
        "timestamp": time.time(),
        "proof": 1,
        "previous_hash": "0" * 64,
        "merkle_root": merkle_root([]),
        "difficulty": DIFFICULTY_TARGET,
        "nonce": 0,
        "transactions": [],
    }
    return proof_of_work(block, DIFFICULTY_TARGET)


def create_block(previous_block: dict, transactions: list, difficulty: int) -> dict:
    tx_ids = [tx["tx_id"] for tx in transactions]
    block = {
        "index": previous_block["index"] + 1,
        "timestamp": time.time(),
        "proof": previous_block["proof"] + 1,
        "previous_hash": previous_block["hash"],
        "merkle_root": merkle_root(tx_ids),
        "difficulty": difficulty,
        "nonce": 0,
        "transactions": transactions,
    }
    return proof_of_work(block, difficulty)


def is_chain_valid(chain: list) -> bool:
    for i in range(1, len(chain)):
        block = chain[i]
        prev = chain[i - 1]

        if block["previous_hash"] != prev["hash"]:
            return False

        expected_hash = hash_block(block)
        if block["hash"] != expected_hash:
            return False

        target = "0" * block["difficulty"]
        if not block["hash"].startswith(target):
            return False

        computed_root = merkle_root([tx["tx_id"] for tx in block["transactions"]])
        if block["merkle_root"] != computed_root:
            return False

    return True
