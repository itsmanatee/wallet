import requests

SOLANA_RPC_URL = "https://rpc.shyft.to?api_key=uD0vRSGoxY8QIoa6"

# Hard-coded preset contracts
PRESET_CONTRACTS = {
    "FaP5jTTWfN77U4HR8PkWcxChvQAqqkbrsKvd6WDQpump",
    "34D7VCSA7uKsCHe5rRs5NpnkGRy7PW4g41asJnZ9pump",
    "4S91kAoRXRGCRBvfPzyHatbo2aD9uJ5gNQox16k1pump",
    "66neDuoXESwZtVNDN3176b6JtjUeh5cgk9fzM5sBpump",
    "61yG5LCoeoqzBdopXPy6BsVPTGdRXht95L68hj5ipump",
    "CSwKoBoFpoxfZbob9WZgc5fc6TE47b3CD8DugFfspump",
    "4vfcfjAz1tSA6tWe7cP6Lj7fR8y7VactzTKPxof7pump",
    "7g4T6qBN5H7g4FFA9F7HY9ndUrkUEqVg7KdtxV55pump",
    "Am17SgVwo9yLi7J3oAbeGVnSbXYCtbcz6eDT6P7Apump",
    "9xZTbcX1o2DvdGKQLheHmodc4bCskhfG4uVgy831pump",
    "9umkdJdE555ZFMyYbi1AXK2VC2Ge6qUwuLH6bwXPpump",
    "E4P5qPoqedZPnHk8xKUvoD2aj3QAjWaQ9H36kcirpump",
    "8hVzPgFopqEQmNNoghr5WbPY1LEjW8GzgbLRwuwHpump"
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
    