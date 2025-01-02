import requests

# Solana RPC URL
SOLANA_RPC_URL = "https://rpc.shyft.to?api_key=uD0vRSGoxY8QIoa6"

# Hard-coded preset contracts
PRESET_CONTRACTS = {
    "ContractAddress1",
    "ContractAddress2",
    "ContractAddress3",
    # Add more addresses as needed
}

def calculate_wallet_score(wallet_address):
    """
    Calculate the score of a wallet based on the number of matching contracts
    in the hard-coded preset contract list.
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
            print("No tokens found for this wallet.")
            return 0  # No tokens found

        # Extract unique mint addresses
        unique_tokens = {
            account["account"]["data"]["parsed"]["info"]["mint"]
            for account in response_data["result"]["value"]
        }

        # Calculate score based on matches with PRESET_CONTRACTS
        score = len(unique_tokens.intersection(PRESET_CONTRACTS))
        return score

    except Exception as e:
        print(f"Error fetching wallet tokens: {e}")
        return 0

def main():
    """
    Main function to interact with the user and calculate wallet scores.
    """
    print("Welcome to the Solana Wallet Scoring Tool!")
    wallet_address = input("Enter the Solana wallet address: ").strip()

    if not wallet_address:
        print("Wallet address is required.")
        return

    print("Calculating wallet score...")
    score = calculate_wallet_score(wallet_address)
    print(f"Wallet Score: {score} (out of {len(PRESET_CONTRACTS)} possible matches)")

if __name__ == "__main__":
    main()
