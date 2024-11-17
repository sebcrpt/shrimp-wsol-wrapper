# shrimp-wsol-wrapper
Actually working code for wrap and unwrap SOL 


If this helped you, don't hesitate to leave a tip. Thanks, brother!
send it : 8HFS8kCoet55YjyLEzUar6hPQA4dGgAweKNzRdwoZR9H



# Solana WSOL Wrapper by little Shrimp

A Python project for interacting with the Solana blockchain to wrap SOL into WSOL (Wrapped SOL) and unwrap WSOL back into SOL. This project simplifies the process of managing WSOL accounts and transactions using Python.

---

## Features

- **Wrap SOL into WSOL**: Converts your native SOL into WSOL for use in SPL token programs.
- **Unwrap WSOL back into SOL**: Reclaims your SOL from a WSOL account.
- **Fully automated transactions**: Handles transaction signing, sending, and confirmation.
- **Lightweight and fast**: Leverages Solana's async client for optimal performance.

---

## Prerequisites

Before running the project, ensure you have the following:

1. **Python 3.8 or higher**.
2. **Solana account with sufficient SOL balance**.
3. **Access to a Solana RPC endpoint**.

---

## Installation

Follow these steps to set up the project:

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/solana-wsol-wrapper.git
cd solana-wsol-wrapper

2. Install Dependencies
Install all required dependencies using pip:
pip install -r requirements.txt

3. Configure the Project
Edit the config.py file to add your settings:

RPC_URL: Your Solana RPC endpoint.
PRIVATE_KEY: Your wallet private key in Base58 format.
AMOUNT_TO_WRAP: The amount of SOL to wrap into WSOL.
Example config.py:
   RPC_URL = "https://api.mainnet-beta.solana.com"  # Replace with your Solana RPC endpoint
   PRIVATE_KEY = "<YOUR_BASE58_PRIVATE_KEY>"        # Replace with your private key in Base58 format
   AMOUNT_TO_WRAP = 1.0                             # Amount of SOL to wrap (e.g., 1.0 SOL)


Usage
Wrap SOL into WSOL
To wrap your SOL into WSOL:
python wrap_sol.py
This script will:

Check if you already have a WSOL account.
Create a WSOL account if necessary.
Transfer the specified amount of SOL into WSOL.


Unwrap WSOL back into SOL
To unwrap your WSOL back into SOL:
python unwrap_sol.py
This script will:

Check if you have an existing WSOL account.
Close the WSOL account.
Transfer the SOL balance back to your wallet.

If this helped you, don't hesitate to leave a tip. Thanks, brother!
send it : 8HFS8kCoet55YjyLEzUar6hPQA4dGgAweKNzRdwoZR9H
