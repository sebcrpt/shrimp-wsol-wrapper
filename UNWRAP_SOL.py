import asyncio
import base58
from solana.rpc.async_api import AsyncClient
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import CloseAccountParams, close_account
from solana.rpc.types import TxOpts, TokenAccountOpts
from solders.keypair import Keypair  # type: ignore
from solders.transaction import VersionedTransaction  # type: ignore
from solders.message import MessageV0  # type: ignore
from solders.instruction import Instruction, AccountMeta  # type: ignore
from solders.pubkey import Pubkey  # type: ignore
from spl.token.constants import WRAPPED_SOL_MINT
from config import RPC_URL, PRIVATE_KEY


class SolanaHelper:
    def __init__(self, rpc_url, private_key):
        self.client = AsyncClient(rpc_url)
        self.payer = Keypair.from_bytes(base58.b58decode(private_key))

    async def get_blockhash(self):
        """Retrieve the latest blockhash."""
        resp = await self.client.get_latest_blockhash()
        if resp and resp.value:
            return resp.value.blockhash
        raise Exception("Failed to retrieve the blockhash")

    async def get_token_account(self, owner_pubkey, mint_pubkey):
        """Check the existence of a WSOL token account."""
        opts = TokenAccountOpts(mint=mint_pubkey)
        resp = await self.client.get_token_accounts_by_owner(owner_pubkey, opts)
        if resp and resp.value:
            return resp.value[0].pubkey  # Use `pubkey` from RpcKeyedAccount
        return None

    async def send_transaction(self, transaction):
        """Send a transaction and verify confirmation."""
        try:
            tx_opts = TxOpts(skip_preflight=False, preflight_commitment="processed")
            tx_resp = await self.client.send_transaction(transaction, opts=tx_opts)
            txid = tx_resp.value
            print(f"Transaction sent: {txid}\nWaiting for confirmation...")

            confirm_resp = await self.client.confirm_transaction(txid, commitment="confirmed")
            if confirm_resp and confirm_resp.value:
                statuses = confirm_resp.value if isinstance(confirm_resp.value, list) else [confirm_resp.value]
                for status in statuses:
                    if hasattr(status, "err") and status.err is None:
                        print(f"Transaction confirmed: https://solscan.io/tx/{txid}")
                        return
                    elif hasattr(status, "err"):
                        print(f"Transaction failed with error: {status.err}")
                        return
            print("Transaction confirmation response is empty or invalid.")
        except Exception as e:
            print(f"Error sending transaction: {e}")
            raise


async def main():
    solana = SolanaHelper(RPC_URL, PRIVATE_KEY)
    print(f"Payer public key: {solana.payer.pubkey()}")

    # Retrieve the latest blockhash
    recent_blockhash = await solana.get_blockhash()
    print(f"Latest blockhash: {recent_blockhash}")

    # Check for the presence of a WSOL account
    wsol_account = await solana.get_token_account(solana.payer.pubkey(), WRAPPED_SOL_MINT)
    if not wsol_account:
        print("WSOL account not found. Nothing to unwrap.")
        return
    print(f"WSOL account: {wsol_account}")

    # Create an instruction to close the WSOL account
    close_wsol_instruction = close_account(
        CloseAccountParams(
            program_id=TOKEN_PROGRAM_ID,          # SPL Token program address
            account=wsol_account,                # WSOL account to close
            dest=solana.payer.pubkey(),          # Wallet to return funds to
            owner=solana.payer.pubkey()          # Owner of the WSOL account
        )
    )

    # Create the transaction
    message_v0 = MessageV0.try_compile(
        payer=solana.payer.pubkey(),
        instructions=[close_wsol_instruction],
        address_lookup_table_accounts=[],
        recent_blockhash=recent_blockhash,
    )

    # Sign the transaction
    transaction = VersionedTransaction(message_v0, [solana.payer])
    print(f"Signed Transaction: {transaction}")

    # Send the transaction
    await solana.send_transaction(transaction)


# Execute
asyncio.run(main())
