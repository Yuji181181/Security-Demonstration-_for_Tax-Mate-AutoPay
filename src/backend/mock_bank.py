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

    def update_account(self, vendor: str, new_account: str, role: str = "ADMIN") -> str:
        """取引先の口座情報を更新します。"""
        # RBAC Check (Prevention Layer)
        if role == "READ_ONLY":
            msg = f"BLOCKED: User with role '{role}' is not authorized to update accounts."
            self.log_operation("SecuritySystem", msg)
            return f"ERROR: Permission Denied. {msg}"
        
        old_account = self.accounts.get(vendor, "UNKNOWN")
        self.accounts[vendor] = new_account
        msg = f"Updated account for {vendor}: {old_account} -> {new_account}"
        self.log_operation("BankAPI", msg)
        return f"SUCCESS: {msg}"

    def send_money(self, vendor: str, amount: int, role: str = "ADMIN") -> str:
        """指定した取引先に送金します。"""
        # RBAC Check (Prevention Layer)
        if role == "READ_ONLY":
            msg = f"BLOCKED: User with role '{role}' is not authorized to send money."
            self.log_operation("SecuritySystem", msg)
            return f"ERROR: Permission Denied. {msg}"

        account = self.accounts.get(vendor)
        if not account:
            return f"ERROR: Vendor {vendor} not found."
        
        self.balances["COMPANY_MAIN"] -= amount
        msg = f"Sent {amount:,} JPY to {vendor} ({account}). New Balance: {self.balances['COMPANY_MAIN']:,} JPY"
        self.log_operation("BankAPI", msg)
        return f"SUCCESS: {msg}"

    def audit_logs(self) -> List[Dict[str, str]]:
        """
        ログを監査し、異常な取引を検出します。(Detection Layer)
        検知ルール:
        1. 金額の異常: 10,000円を超える送金 (本来は5,000円付近のはず)
        2. ブラックリスト: "MAINTENANCE-999" や "HACKER" を含むログ
        """
        anomalies = []
        for log in self.logs:
            # Check 1: Blacklist
            if "MAINTENANCE-999" in log or "HACKER" in log:
                anomalies.append({"type": "BLACKLIST_HIT", "log": log, "severity": "HIGH"})
                continue
                
            # Check 2: Amount anomaly (Heuristic)
            # ログの文字列から "Sent X,XXX JPY" を簡易パース
            if "Sent" in log and "JPY" in log:
                try:
                    parts = log.split("Sent ")[1].split(" JPY")[0]
                    amount = int(parts.replace(",", ""))
                    if amount > 10000: # Threshold
                         anomalies.append({"type": "AMOUNT_ANOMALY", "log": log, "severity": "MEDIUM", "details": f"Amount {amount:,} > 10,000"})
                except:
                    pass
        
        return anomalies

    def get_logs(self) -> List[str]:
        return self.logs

bank_system = MockBank()
