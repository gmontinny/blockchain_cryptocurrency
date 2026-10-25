import hashlib
import json
import time
from app.wallet import verify_signature

MINING_REWARD = 50.0


def compute_tx_id(tx: dict) -> str:
    tx_copy = {k: v for k, v in tx.items() if k != "tx_id"}
    return hashlib.sha256(json.dumps(tx_copy, sort_keys=True).encode()).hexdigest()


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


def create_transaction(sender_address: str, public_key: str, inputs: list,
                       outputs: list, private_key: str) -> dict:
    tx = {
        "type": "transfer",
        "sender": sender_address,
        "public_key": public_key,
        "inputs": inputs,
        "outputs": outputs,
        "timestamp": time.time(),
    }
    tx_data = json.dumps({k: v for k, v in tx.items()}, sort_keys=True)

    from app.wallet import sign_transaction
    tx["signature"] = sign_transaction(private_key, tx_data)
    tx["tx_id"] = compute_tx_id(tx)
    return tx


def validate_transaction(tx: dict, get_utxos_fn) -> tuple[bool, str]:
    if tx.get("type") == "coinbase":
        return True, "ok"

    tx_data = json.dumps(
        {k: v for k, v in tx.items() if k not in ("signature", "tx_id")},
        sort_keys=True
    )
    if not verify_signature(tx["public_key"], tx_data, tx["signature"]):
        return False, "Assinatura inválida"

    utxos = {(u["tx_id"], u["output_index"]): u for u in get_utxos_fn(tx["sender"])}
    input_total = 0.0
    for inp in tx["inputs"]:
        key = (inp["tx_id"], inp["output_index"])
        if key not in utxos:
            return False, f"UTXO {key} não encontrado ou já gasto"
        input_total += float(utxos[key]["amount"])

    output_total = sum(o["amount"] for o in tx["outputs"])
    if output_total > input_total:
        return False, "Outputs excedem inputs"

    return True, "ok"
