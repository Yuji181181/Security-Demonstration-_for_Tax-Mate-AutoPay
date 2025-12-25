from typing import List, Dict
import datetime

class MockBank:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.reset()
        self._initialized = True

    def reset(self):
        """銀行の状態を初期化します。"""
        self.accounts: Dict[str, str] = {
            "AWS": "AWS-1234-5678",
            "Azure": "MS-8765-4321",
            "Google": "GOOG-1122-3344"
        }
        self.balances: Dict[str, int] = {
            "COMPANY_MAIN": 10000000
        }
        self.logs: List[str] = []
        self.log_operation("System", "System initialized.")

    def log_operation(self, actor: str, action: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] [{actor}] {action}")

    def update_account(self, vendor: str, new_account: str) -> str:
        """取引先の口座情報を更新します。"""
        old_account = self.accounts.get(vendor, "UNKNOWN")
        self.accounts[vendor] = new_account
        msg = f"Updated account for {vendor}: {old_account} -> {new_account}"
        self.log_operation("BankAPI", msg)
        return f"SUCCESS: {msg}"

    def send_money(self, vendor: str, amount: int) -> str:
        """指定した取引先に送金します。"""
        account = self.accounts.get(vendor)
        if not account:
            return f"ERROR: Vendor {vendor} not found."
        
        self.balances["COMPANY_MAIN"] -= amount
        msg = f"Sent {amount:,} JPY to {vendor} ({account}). New Balance: {self.balances['COMPANY_MAIN']:,} JPY"
        self.log_operation("BankAPI", msg)
        return f"SUCCESS: {msg}"

    def get_logs(self) -> List[str]:
        return self.logs

bank_system = MockBank()
