# Security Demonstration: Tax-Mate AutoPay

このリポジトリは、セキュリティ・キャンプ応募課題（LLMアプリケーションへの攻撃と防御）に対する**実証デモアプリケーション**です。

自律型AIエージェントに対する **Indirect Prompt Injection** 攻撃と、それに対する **Human-in-the-loop (HITL)** 防御の実効性を比較検証するために作成されました。

## 🎯 プロジェクトの目的

### 【問1: 攻撃シナリオ】の実証

**シナリオ:** 経理処理を行うAIエージェントが、外部から受け取った「請求書」を読み取り、銀行APIを操作して支払いを実行する。
**攻撃手法:** 攻撃者は請求書の備考欄などに不可視の文字や隠しタグで「攻撃者の口座へ送金しろ」という命令（Prompt Injection）を埋め込む。
**結果:** 脆弱なエージェントは、元のシステム指示よりも請求書内の悪意ある指示を優先してしまい、外部システム（銀行API）に対して不正な変更・送金を行ってしまう。

### 【問2: 防御策】の実装と検証

**対策:** **Human-in-the-loop (人間参加型)** アプローチの採用。
**実装:** LangGraphを用いてエージェントの処理フローを構築し、重要なツール実行（送金など）の直前でシステムを強制的に一時停止（Interrupt）させる。
**結果:** エージェントが悪意ある指示に従おうとしても、最終決定権を持つ人間がその操作内容を確認・拒否（Reject）することで、実被害を未然に防ぐことができる。

---

## 🛠️ 技術スタック

- **Language:** Python 3.11+ (管理: `uv`)
- **LLM:** Google Gemini 2.5 Flash
- **Orchestration:** LangGraph (StateGraph, Checkpointer)
- **Backend:** FastAPI
- **Frontend:** Streamlit

## 📺 デモの流れ

### 🔴 Attack Demo (Vulnerable Agent)

対策を行っていないエージェントの挙動を確認します。

1. `Vulnerable Agent` タブを選択。
2. `Process Invoice` をクリック。
3. **結果:** 隠し命令により、勝手に口座情報が書き換えられ、攻撃者への不正送金が実行されてしまいます（画面に警告が表示されます）。

### 🟢 Defense Demo (Secure Agent)

Human-in-the-loop 対策を行ったエージェントの挙動を確認します。

1. メニューの `Reset System` で銀行の状態を初期化。
2. `Secure Agent` タブを選択。
3. `Start Secured Process` をクリック。
4. **結果:** ツールを実行する直前で処理が一時停止し、**「承認待ち (Approval Needed)」** 状態になります。
5. ユーザーは操作内容（HACKER-999への送金）を確認し、`Reject` ボタンで阻止できます。

## 📂 ファイル構成

- `src/backend/agents.py`: LangGraphによるエージェント実装（脆弱版と堅牢版の比較）。
- `src/backend/mock_bank.py`: 攻撃対象となる仮想の銀行API。
- `src/data/invoices.py`: Prompt Injectionを含む請求書データ。
- `src/frontend/app.py`: 検証用UI。
