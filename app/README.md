# Shopping List Demo

A minimal Streamlit application that calls OpenAI's Responses API to extract a structured shopping list and display it in a user-friendly interface.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r app/requirements.txt
cp app/.env.example .env  # put your key
streamlit run app/app.py
```

## Environment variables

Create a `.env` file with your OpenAI API key:

```dotenv
OPENAI_API_KEY=sk-...
```

## Extending the app

- Replace `tools/cart_stub.py` with a real integration (e.g., Playwright, MCP, or AgentKit) to add items to a cart.
- To stream model output, adapt `services.llm.extract_items` to yield incremental responses and render them with `st.write_stream`.
