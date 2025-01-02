import requests

SOLANA_RPC_URL = "https://rpc.shyft.to?api_key=uD0vRSGoxY8QIoa6"

# Hard-coded preset contracts
PRESET_CONTRACTS = {
    "6UTMKBD4V4xGmTFtu77ni2dRjrdcvnqcnDkkmBq4pump",
    "6FEXNNT5ygU7MzJtfL29t7uKNssKjLHmyhWtFGtxpump",
    "ContractAddress3",
    # Add more addresses as needed
}

def calculate_wallet_score(wallet_address):
    """
    Calculate the wallet score based on matching contracts and return matching addresses.
    """
    url = SOLANA_RPC_URL
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [
            wallet_address,
            {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
            {"encoding": "jsonParsed"}
        ]
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()

        if "result" not in response_data or "value" not in response_data["result"]:
            return {"score": 0, "matches": []}

        # Extract unique mint addresses
        unique_tokens = {
            account["account"]["data"]["parsed"]["info"]["mint"]
            for account in response_data["result"]["value"]
        }

        # Calculate matches with preset contracts
        matches = unique_tokens.intersection(PRESET_CONTRACTS)
        score = len(matches)

        return {"score": score, "matches": list(matches)}

    except Exception as e:
        raise ValueError(f"Error fetching wallet tokens: {e}")
    