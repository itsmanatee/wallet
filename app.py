import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

SOLANA_RPC_URL = "https://rpc.shyft.to?api_key=uD0vRSGoxY8QIoa6"

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/transaction_history", methods=["POST"])
def transaction_history():
    """
    API endpoint to fetch transaction history of a wallet and provide tax overview.
    """
    data = request.json
    wallet_address = data.get("wallet_address")

    if not wallet_address:
        return jsonify({"error": "Wallet address is required"}), 400

    try:
        # Fetch transaction signatures
        headers = {"Content-Type": "application/json"}
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getConfirmedSignaturesForAddress2",
            "params": [wallet_address, {"limit": 10}],
        }
        response = requests.post(SOLANA_RPC_URL, json=payload, headers=headers)
        response_data = response.json()

        if not response_data.get("result"):
            return jsonify({"error": "No transactions found"}), 404

        # Example: Collect additional transaction details (you can expand this part)
        transactions = []
        for tx in response_data["result"]:
            tx_details = {
                "signature": tx["signature"],
                "slot": tx["slot"],
                "block_time": tx.get("blockTime"),
                "amount": 0,  # Replace with logic to extract amount
                "token": "SOL",  # Replace with logic to identify token
                "flow": "IN" if tx["err"] is None else "OUT",
            }
            transactions.append(tx_details)

        # Example: Calculate tax overview (stubbed for now)
        tax_overview = {
            "total_liability": "$0",
            "tax_rate": "0%",
            "net_after_tax": "$0",
            "net_capital_gains": "$0",
            "total_transactions": len(transactions),
        }

        return jsonify({"transactions": transactions, "tax_overview": tax_overview})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.after_request
def add_cors_headers(response):
    """
    Add CORS headers to the response.
    """
    response.headers["Access-Control-Allow-Origin"] = "*"  # Replace with your Carrd domain if needed
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
