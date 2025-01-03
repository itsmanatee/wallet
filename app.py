import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

SOLANA_RPC_URL = "https://rpc.shyft.to?api_key=uD0vRSGoxY8QIoa6"

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def generate_tax_data(balance_in_sol):
    """
    Generate simulated tax data tied to the wallet's balance.
    """
    tax_rate = round(balance_in_sol * 0.05, 2)  # 5% tax rate simulation
    total_tax_liability = round(balance_in_sol * 0.05, 2)  # Tax liability as a percentage of balance
    net_after_tax = round(balance_in_sol - total_tax_liability, 2)  # Remaining balance
    net_capital_gains = round(balance_in_sol * 0.03, 2)  # Simulate capital gains

    return {
        "total_tax_liability": f"${total_tax_liability}",
        "tax_rate": f"{tax_rate}%",
        "net_after_tax": f"${net_after_tax}",
        "net_capital_gains": f"${net_capital_gains}",
    }


@app.route("/transaction_history", methods=["POST"])
def transaction_history():
    """
    API endpoint to fetch transaction history and tax overview of a wallet.
    """
    data = request.json
    wallet_address = data.get("wallet_address")

    if not wallet_address:
        return jsonify({"error": "Wallet address is required"}), 400

    try:
        headers = {"Content-Type": "application/json"}

        # Fetch current balance
        balance_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [wallet_address],
        }
        balance_response = requests.post(SOLANA_RPC_URL, json=balance_payload, headers=headers)
        balance_data = balance_response.json()

        if "error" in balance_data:
            return jsonify({"error": "Unable to fetch balance"}), 400

        lamports = balance_data.get("result", 0)
        balance_in_sol = lamports / 1e9  # Convert lamports to SOL

        # Fetch transactions (use getConfirmedSignaturesForAddress2)
        transaction_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getConfirmedSignaturesForAddress2",
            "params": [wallet_address, {"limit": 10}],
        }
        transaction_response = requests.post(SOLANA_RPC_URL, json=transaction_payload, headers=headers)
        transaction_data = transaction_response.json()

        if "error" in transaction_data or "result" not in transaction_data:
            return jsonify({"error": "Unable to fetch transactions"}), 400

        # Parse transactions
        transactions = []
        for tx in transaction_data["result"]:
            transactions.append({
                "signature": tx["signature"],
                "slot": tx["slot"],
                "block_time": tx.get("blockTime"),
                "amount": 0,  # Replace with logic if available
                "token": "SOL",
                "flow": "IN" if tx.get("err") is None else "OUT",
            })

        # Generate tax data
        tax_data = generate_tax_data(balance_in_sol)

        return jsonify({
            "current_balance": balance_in_sol,
            "transactions": transactions,
            "tax_overview": tax_data,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.after_request
def add_cors_headers(response):
    """
    Add CORS headers to the response.
    """
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
