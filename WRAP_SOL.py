import asyncio
import base58
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts, TokenAccountOpts
from solders.keypair import Keypair  # type: ignore
from solders.transaction import VersionedTransaction  # type: ignore
from solders.message import MessageV0  # type: ignore
from solders.instruction import Instruction, AccountMeta  # type: ignore
from solders.pubkey import Pubkey  # type: ignore
from solders.compute_budget import set_compute_unit_price, set_compute_unit_limit  # type: ignore
from solders.system_program import transfer, TransferParams
from spl.token.instructions import create_associated_token_account, SyncNativeParams, sync_native
from spl.token.constants import WRAPPED_SOL_MINT, TOKEN_PROGRAM_ID
from config import RPC_URL, PRIVATE_KEY, AMOUNT_TO_WRAP


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
        """Check the existence of a token account for WSOL."""
        opts = TokenAccountOpts(mint=mint_pubkey)
        resp = await self.client.get_token_accounts_by_owner(owner_pubkey, opts)
        if resp and resp.value:
            return resp.value[0].pubkey  # Use `pubkey` from RpcKeyedAccount
        return None

    async def send_transaction(self, transaction):
        """Send a transaction with confirmation verification."""
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

    # Check or create a WSOL account
    wsol_account = await solana.get_token_account(solana.payer.pubkey(), WRAPPED_SOL_MINT)
    create_wsol_instructions = []
    if not wsol_account:
        print("WSOL account not found, creating it...")
        create_wsol_instruction = create_associated_token_account(
            payer=solana.payer.pubkey(),
            owner=solana.payer.pubkey(),
            mint=WRAPPED_SOL_MINT,
        )
        wsol_account = create_wsol_instruction.accounts[1].pubkey
        create_wsol_instructions.append(create_wsol_instruction)
    else:
        print(f"WSOL account already exists: {wsol_account}")

    # Prepare instructions
    lamports_to_wrap = int(AMOUNT_TO_WRAP * 10**9)
    main_instructions = [
        set_compute_unit_price(1_000_000),  # Set the price for compute units
        set_compute_unit_limit(200_000),  # Set the limit for compute units
        transfer(TransferParams(from_pubkey=solana.payer.pubkey(), to_pubkey=wsol_account, lamports=lamports_to_wrap)),
        sync_native(SyncNativeParams(program_id=TOKEN_PROGRAM_ID, account=wsol_account)),
    ]

    # Compile instructions
    all_instructions = create_wsol_instructions + main_instructions
    compiled_instructions = [
        Instruction(
            program_id=instr.program_id,
            accounts=[
                AccountMeta(pubkey=acc.pubkey, is_signer=acc.is_signer, is_writable=acc.is_writable)
                for acc in instr.accounts
            ],
            data=instr.data,
        )
        for instr in all_instructions
    ]

    # Create and sign the transaction
    message_v0 = MessageV0.try_compile(
        payer=solana.payer.pubkey(),
        instructions=compiled_instructions,
        address_lookup_table_accounts=[],
        recent_blockhash=recent_blockhash,
    )
    transaction = VersionedTransaction(message_v0, [solana.payer])
    print(f"Signed Transaction: {transaction}")

    # Send the transaction
    await solana.send_transaction(transaction)


# Execution
asyncio.run(main())
