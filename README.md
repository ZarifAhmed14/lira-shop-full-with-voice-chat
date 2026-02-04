# My AI Project: Lira Cosmetics Assistant

For my project, I built an AI-powered customer service system for a real company called Lira Cosmetics. I wanted to see how LLMs (Large Language Models) could help a business manage customer questions while also keeping track of exactly how much the AI costs to run.

## Project Overview

My system has two main parts:
1.  **Backend (Python/Flask)**: This is the "brain" that connects to AI models like Llama 3 (via Groq), GPT-4, and Gemini. I focused a lot on the cost calculation logic here.
2.  **Frontend (React/Vite)**: I built a dashboard where you can see all the stats, charts, and even generate PDF reports.

## How to Run My Project
## Copy/Paste Commands (Windows PowerShell)
### Backend (Flask)
```powershell
cd d:\lira-shop-full\lira-shop-full-main\project
d:\lira-shop-full\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

### Frontend (Vite)
```powershell
cd d:\lira-shop-full\lira-shop-full-main\frontend
npm install
npm run dev
```

### Setting up the Backend
1.  Open a terminal.
2.  Navigate to the project folder:
    ```bash
    cd d:/lira-shop-full/lira-shop-full-main/project
    ```
3.  Install dependencies:
    ```bash
    pip install --upgrade groq httpx httpcore openai
    pip install -r requirements.txt
    ```
4.  Start the server:
    ```bash
    python app.py
    ```

### Setting up the Frontend
1.  Open a **NEW** terminal.
2.  Navigate to the frontend folder:
    ```bash
    cd d:/lira-shop-full/lira-shop-full-main/frontend
    ```
3.  Install the packages:
    ```bash
    npm install
    ```
4.  Start the dev server:
    ```bash
    npm run dev
    ```
5.  Open `http://localhost:5173` to view the dashboard.
4.  Open `http://localhost:5173` to view the dashboard.

## New: OpenAI Voice Integration
The system now supports **OpenAI Whisper (STT)** and **OpenAI TTS**.
- To use OpenAI, add `OPENAI_API_KEY` to your `project/.env`.
- To verify both Groq and OpenAI, run: `python project/test_openai_voice.py`.

## Key Parts I Worked On
-   **Multi-Model Support**: Switch between Groq, OpenAI, and Gemini.
-   **Voice AI**: Integrated both Free (Edge TTS/Groq) and Paid (OpenAI) voice providers.
-   **Cost Tracking**: Accurate 2025 pricing calculation per token/character.
-   **PDF Reports**: Automated generation using `reportlab`.
-   **Admin Dashboard**: Data visualization with `recharts`.
