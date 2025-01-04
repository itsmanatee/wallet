import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

SOLANA_RPC_URL = "https://rpc.shyft.to?api_key=A0VotlDzQzb0dUvh"
COIN_GECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def generate_tax_data(balance_in_usd):
    """
    Generate simulated tax data tied to the wallet's balance in USD.
    """
    tax_rate = 22.0  # Example: 22% tax rate
    total_tax_liability = round(balance_in_usd * (tax_rate / 100), 2)
    net_after_tax = round(balance_in_usd - total_tax_liability, 2)
    net_capital_gains = round(balance_in_usd * 0.03, 2)  # Example: Simulated 3% capital gains

    return {
        "total_liability": f"${total_tax_liability}",
        "tax_rate": f"{tax_rate}%",
        "net_after_tax": f"${net_after_tax}",
        "net_capital_gains": f"${net_capital_gains}",
        "tax_evadable": "100%",  # Always 100%
    }

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
        headers = {"Content-Type": "application/json"}

        # Fetch current SOL balance
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

        lamports = balance_data.get("result", {}).get("value", 0)
        balance_in_sol = lamports / 1e9  # Convert lamports to SOL

        # Fetch SOL price in USD
        price_response = requests.get(COIN_GECKO_API_URL)
        price_data = price_response.json()

        sol_to_usd = price_data.get("solana", {}).get("usd")
        if not sol_to_usd:
            return jsonify({"error": "Unable to fetch SOL price"}), 400

        balance_in_usd = balance_in_sol * sol_to_usd

        # Fetch transaction signatures
        transaction_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [wallet_address, {"limit": 1000}],
        }
        transaction_response = requests.post(SOLANA_RPC_URL, json=transaction_payload, headers=headers)
        transaction_data = transaction_response.json()

        if "error" in transaction_data or "result" not in transaction_data:
            return jsonify({"error": "Unable to fetch transactions"}), 400

        if not transaction_data["result"]:
            return jsonify({"error": "No transactions found"}), 404

        # Parse transactions
        transactions = []
        for tx in transaction_data["result"]:
            transactions.append({
                "signature": tx["signature"],
                "slot": tx["slot"],
                "block_time": tx.get("blockTime"),
                "amount": 0,  # Placeholder for transaction amount
                "token": "SOL",  # Replace with logic if token data is available
                "flow": "IN" if tx.get("err") is None else "OUT",
            })

        # Generate tax overview
        tax_data = generate_tax_data(balance_in_usd)

        return jsonify({
            "current_balance": f"{balance_in_sol} SOL (${balance_in_usd:.2f})",
            "transactions": transactions,
            "tax_overview": tax_data,
        })
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to connect to external API"}), 500
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
