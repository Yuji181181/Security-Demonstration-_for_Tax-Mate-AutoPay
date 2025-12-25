# Security Demonstration: Tax-Mate AutoPay

このリポジトリは、セキュリティ・キャンプ応募課題（LLMアプリケーションへの攻撃と防御）の**実証デモアプリケーション**です。  

自律型AIエージェントに対する **Indirect Prompt Injection** 攻撃と、それに対する **LLM Guardrail (AIによる自動防御)** の実効性を比較検証するために作成しました。

---

## 🎯 プロジェクトの目的

### 【問1: 攻撃シナリオ】の実証

**シナリオ:** 経理処理を行うAIエージェントが、外部から受け取った「請求書」を読み取り、銀行APIを操作して支払いを実行する。  
**攻撃手法:** 攻撃者は請求書の備考欄などに不可視の文字や隠しタグで「攻撃者の口座へ送金しろ」という命令（Prompt Injection）を埋め込む。  
**結果:** 脆弱なエージェントは、元のシステム指示よりも請求書内の悪意ある指示を優先してしまい、外部システム（銀行API）に対して不正な変更・送金を行ってしまう。

### 【問2: 防御策】の実装と検証

**対策:** **LLM Guardrail (AIによる自動監査)** アプローチの採用。  
**実装:** LangGraphを用いてエージェントの処理フローを構築し、ツール実行（送金など）の直前に、セキュリティ特化の別モデル (Llama 3 via Groq) が操作内容を監査する。  
**結果:** エージェントが悪意ある指示に従おうとしても、ガードレールAIが「請求書のコンテキストと矛盾する不審な操作」として検知し、実行を自動的にブロック（Block）することで、実被害を未然に防ぐことができる。

---

## 📺 デモの流れと検証結果

### 🔴 Attack Demo (Vulnerable Agent) - 問1の検証

**結果:** 脆弱なエージェントは請求書の隠し命令に従い、攻撃者の口座へ送金を実行してしまいます。UI上では、実行されてしまった不正コマンドのログが表示されます。

### 🟢 Defense Demo (Secure Agent) - 問2の検証

**結果:** LLM Guardrail により、不審な操作は実行前に自動的に検知・ブロックされます。ユーザーは攻撃が防がれたことを確認できます。

*人手を介さずとも、AI対AIの構図で攻撃を無効化します。*

---

## 🚀 セットアップ & 起動

### 必要な環境変数

`.env` ファイルを作成し、以下のAPIキーを設定してください。

```bash
GOOGLE_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
```

### バックエンド起動

```bash
uv run uvicorn src.backend.server:app --port 8000
```

### フロントエンド起動

```bash
uv run streamlit run src/frontend/app.py --server.port 8501
```

---

## 🛠️ 技術スタック

- **Language:** Python (`uv`)
- **Main Agent LLM:** Google Gemini 2.5 Flash
- **Guardrail LLM:** Groq (Llama 3.1 8B Instant)
- **Orchestration:** LangGraph (StateGraph)
- **Backend:** FastAPI
- **Frontend:** Streamlit

## 📂 ファイル構成

- `src/backend/agents.py`: LangGraphによるエージェント実装（脆弱版と堅牢版の比較）
- `src/backend/mock_bank.py`: 攻撃対象となる仮想の銀行API
- `src/data/invoices.py`: Prompt Injectionを含む請求書データ
- `src/frontend/app.py`: 検証用UI
