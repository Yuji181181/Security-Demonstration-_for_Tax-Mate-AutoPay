from contextvars import ContextVar

# ユーザーの権限レベルを保持するコンテキスト変数
# デフォルトは "ADMIN" (全権限)
# "READ_ONLY" の場合は送金などの書き込み操作をブロックする
user_role_var: ContextVar[str] = ContextVar("user_role", default="ADMIN")
