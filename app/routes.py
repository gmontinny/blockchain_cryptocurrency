import os
import requests
from flask import Blueprint, jsonify, request
from uuid import uuid4

from app import blockchain as bc
from app import database as db
from app.transaction import create_coinbase_tx, create_transaction, validate_transaction
from app.wallet import generate_wallet

router = Blueprint("router", __name__)

NODE_ADDRESS = str(uuid4()).replace("-", "")
MINER_ADDRESS = os.getenv("MINER_ADDRESS", NODE_ADDRESS)

mempool: list = []


def _get_chain() -> list:
    chain = db.load_chain()
    if not chain:
        genesis = bc.create_genesis_block()
        db.save_block(genesis)
        chain = [genesis]
    return chain


@router.route("/mine", methods=["GET"])
def mine():
    chain = _get_chain()
    difficulty = bc.calculate_difficulty(chain)
    coinbase = create_coinbase_tx(MINER_ADDRESS, chain[-1]["index"] + 1)
    transactions = [coinbase] + mempool[:]

    block = bc.create_block(chain[-1], transactions, difficulty)
    db.save_block(block)

    db.save_utxos(coinbase["tx_id"], coinbase["outputs"])
    for tx in mempool:
        db.mark_utxos_spent(tx["inputs"])
        db.save_utxos(tx["tx_id"], tx["outputs"])

    mempool.clear()

    return jsonify({
        "message": "Bloco minerado com sucesso!",
        "block_index": block["index"],
        "hash": block["hash"],
        "difficulty": block["difficulty"],
        "nonce": block["nonce"],
        "merkle_root": block["merkle_root"],
        "transactions": len(block["transactions"]),
        "miner_reward": 50.0,
    }), 200


@router.route("/chain", methods=["GET"])
def get_chain():
    chain = _get_chain()
    return jsonify({"chain": chain, "length": len(chain)}), 200


@router.route("/validate", methods=["GET"])
def validate():
    chain = _get_chain()
    valid = bc.is_chain_valid(chain)
    return jsonify({"valid": valid, "blocks": len(chain)}), 200


@router.route("/transaction/new", methods=["POST"])
def new_transaction():
    data = request.get_json()
    required = ["sender", "public_key", "private_key", "inputs", "outputs"]
    if not all(k in data for k in required):
        return jsonify({"error": "Campos obrigatórios: sender, public_key, private_key, inputs, outputs"}), 400

    tx = create_transaction(
        data["sender"], data["public_key"],
        data["inputs"], data["outputs"], data["private_key"]
    )
    valid, msg = validate_transaction(tx, db.get_utxos)
    if not valid:
        return jsonify({"error": msg}), 400

    mempool.append(tx)
    return jsonify({"message": "Transação adicionada ao mempool", "tx_id": tx["tx_id"]}), 201


@router.route("/mempool", methods=["GET"])
def get_mempool():
    return jsonify({"mempool": mempool, "count": len(mempool)}), 200


@router.route("/wallet/new", methods=["GET"])
def new_wallet():
    wallet = generate_wallet()
    return jsonify(wallet), 201


@router.route("/balance/<address>", methods=["GET"])
def balance(address):
    bal = db.get_balance(address)
    utxos = db.get_utxos(address)
    return jsonify({"address": address, "balance": bal, "utxos": utxos}), 200


@router.route("/nodes/register", methods=["POST"])
def register_nodes():
    data = request.get_json()
    nodes = data.get("nodes", [])
    if not nodes:
        return jsonify({"error": "Lista de nós vazia"}), 400
    for node in nodes:
        db.save_node(node)
    return jsonify({"message": "Nós registrados", "nodes": db.load_nodes()}), 201


@router.route("/nodes", methods=["GET"])
def list_nodes():
    return jsonify({"nodes": db.load_nodes()}), 200


@router.route("/nodes/consensus", methods=["GET"])
def consensus():
    nodes = db.load_nodes()
    local_chain = _get_chain()
    best_chain = local_chain
    replaced = False

    for node in nodes:
        try:
            resp = requests.get(f"{node}/chain", timeout=5)
            if resp.status_code != 200:
                continue
            remote = resp.json()
            remote_chain = remote["chain"]
            if len(remote_chain) > len(best_chain) and bc.is_chain_valid(remote_chain):
                best_chain = remote_chain
                replaced = True
        except requests.RequestException:
            continue

    if replaced:
        for block in best_chain:
            db.save_block(block)

    return jsonify({
        "replaced": replaced,
        "chain_length": len(best_chain),
    }), 200
