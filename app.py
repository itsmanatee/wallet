import os
from flask import Flask, request, jsonify
from solana_client import calculate_wallet_score
from flask_cors import CORS

app = Flask(__name__)

# Allow CORS on your Flask app
CORS(app, resources={r"/*": {"origins": "*"}})

# In-memory leaderboard (replace with a database for persistence)
leaderboard = []

@app.route("/wallet_score", methods=["POST"])
def wallet_score():
    """
    API endpoint to calculate the wallet score based on hard-coded preset contracts.
    """
    global leaderboard
    data = request.json
    wallet_address = data.get("wallet_address")
    wallet_name = data.get("wallet_name")  # Get the wallet name from the request

    if not wallet_address:
        return jsonify({"error": "Wallet address is required"}), 400

    if not wallet_name:
        return jsonify({"error": "Wallet name is required"}), 400

    try:
        # Calculate the score
        score = calculate_wallet_score(wallet_address)

        # Check for existing wallet entry
        existing_entry = next((entry for entry in leaderboard if entry["wallet"] == wallet_address), None)
        if existing_entry:
            # Update the existing entry with the new name and score
            existing_entry["name"] = wallet_name
            existing_entry["score"] = score
        else:
            # Add new entry if wallet is not already in leaderboard
            leaderboard.append({"name": wallet_name, "wallet": wallet_address, "score": score})

        # Keep leaderboard sorted and limited to top 50
        leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)[:50]

        # Return the calculated score
        return jsonify({"score": score})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/leaderboard", methods=["GET"])
def get_leaderboard():
    """
    API endpoint to fetch the leaderboard.
    """
    return jsonify(leaderboard)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Default to port 5000 if PORT is not set
    app.run(host="0.0.0.0", port=port)

@app.after_request
def add_cors_headers(response):
    """
    Add CORS headers to the response.
    """
    response.headers["Access-Control-Allow-Origin"] = "asgasg.carrd.co"  # Replace with your Carrd domain
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response