import requests
from solana.rpc.api import Client
from solders.pubkey import Pubkey

SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"  # Switch to official Solana RPC endpoint

# Initialize Solana client
solana_client = Client(SOLANA_RPC_URL)

def manual_rpc_call(wallet_address):
    """
    Fetch all tokens owned by the given Solana wallet using manual RPC call.
    """
    url = "https://api.mainnet-beta.solana.com"
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
    response = requests.post(url, json=payload, headers=headers)
    print("Manual RPC Response:", response.json())  # Debugging: Print the raw response
    return response.json()

def get_wallet_tokens(wallet_address):
    """
    Fetch all tokens owned by the given Solana wallet using solana-py client.
    """
    wallet_pubkey = Pubkey.from_string(wallet_address)  # Convert wallet address to Pubkey
    try:
        # Debugging: Print wallet_pubkey
        print("Wallet Pubkey:", wallet_pubkey)

        response = solana_client.get_token_accounts_by_owner(
            wallet_pubkey, {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"}
        )
        
        # Debugging: Print raw response
        print("Raw Solana-Py Response:", response)

        # Check if the response has the expected structure
        if not response or "result" not in response or not response["result"].get("value"):
            return []  # Handle cases where no tokens are found or the response is malformed

        # Extract mint addresses of tokens
        tokens = []
        for account in response["result"]["value"]:
            mint_address = account["account"]["data"]["parsed"]["info"]["mint"]
            tokens.append(mint_address)
        
        return tokens
    except Exception as e:
        # Print error for debugging
        print(f"Error during Solana-Py call: {e}")
        raise

# Test Functionality
if __name__ == "__main__":
    wallet_address = input("Enter the Solana wallet address: ").strip()
    try:
        print("Using Solana-Py Client...")
        tokens = get_wallet_tokens(wallet_address)
        if tokens:
            print(f"Tokens owned by the wallet ({wallet_address}):")
            for token in tokens:
                print(token)
        else:
            print(f"No tokens found for wallet: {wallet_address}")
    except Exception as e:
        print(f"Error using Solana-Py client: {e}")
        print("Falling back to manual RPC call...")
        try:
            manual_response = manual_rpc_call(wallet_address)
            if manual_response.get("result") and manual_response["result"].get("value"):
                tokens = [
                    account["account"]["data"]["parsed"]["info"]["mint"]
                    for account in manual_response["result"]["value"]
                ]
                print(f"Tokens owned by the wallet ({wallet_address}):")
                for token in tokens:
                    print(token)
            else:
                print(f"No tokens found for wallet: {wallet_address}")
        except Exception as manual_e:
            print(f"Error during manual RPC call: {manual_e}")
