# SaveUp

SaveUp is an AI-powered financial planning assistant that helps users create personalized financial plans based on their goals, income, expenses, and savings.

## Features

- Conversational chatbot for financial planning
- Gathers user financial information interactively
- Generates actionable, personalized financial plans
- Downloadable PDF report of your financial plan
- Built with Streamlit, Langranph, LangChain, and OpenAI
- Applied Langgraph concepts, including ReAct agents, tool integration, human-in-the-loop workflows, interruption handling, and management of short-term and long-term memory.

## Getting Started

### Prerequisites

- Python 3.12
- [uv](https://github.com/astral-sh/uv) (for environment management)

### Installation

1. **Create and activate a virtual environment:**
   ```powershell
   uv venv --python 3.12
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .venv\Scripts\Activate.ps1
   ```

2. **Install dependencies:**
   ```bash
   uv pip install -r requirements.txt
   ```

3. **Set your OpenAI API keys:**
   - Add your `OPENAI_MODEL` and `OPENAI_KEY` to Streamlit secrets (`.streamlit/secrets.toml`).

### Running the App

```bash
streamlit run app.py
```

## Usage

- Start the app and chat with the assistant.
- Provide your financial goal, amount, savings, time period, monthly expenses, and salary.
- Review and confirm your information.
- Download your personalized financial plan as a PDF.

## File Structure

- `app.py` – Streamlit web app
- `agent/agent.py` – Chatbot logic and LangGraph agent
- `file_helper.py` – PDF generation utilities
- `requirements.txt` – Python dependencies

## License