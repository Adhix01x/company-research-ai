# 🤖 Company Research AI — Intelligent Assistant

A premium, state-of-the-art **AI Company Research Assistant** designed to automatically research any company by name or URL. The platform crawls official websites, searches organic web results for context and contact details, identifies competitor intelligence, generates structured insights, notifies team pipelines via Discord embeds, and renders download-ready PDF reports with beautiful corporate styling.

---

## ✨ Features (Hackathon Requirements & Enhancements)

### 1. **Intelligent Company Search & Resolution**
- Supports both **Company Name** (e.g. `Linear`, `Figma`) and **Website URL** (e.g. `stripe.com`, `https://tesla.com`).
- Resolves official domains using **Serper.dev** Google Search API queries when a name is input.

### 2. **Intelligent Web Crawling & Content Extraction**
- Crawls up to 5 pages of the target website (e.g. About, Pricing, Solutions).
- Identifies and strips non-content HTML structures (`script`, `style`, `nav`, `footer`, `aside`, `header`, `noscript`) for optimal AI parsing.
- Uses rate-limiting protection with a professional `User-Agent` (`AIHiringResearchBot/1.0`).

### 3. **Structured AI Synthesis (OpenRouter)**
- Prompts OpenRouter models (Gemini, Claude, GPT-4o, etc.) to evaluate company data and return **structured JSON**.
- Generates: Overview/Summary, Contact details (Phone, Address), Products & Services, AI-Generated Pain Points, and Direct Competitors.
- Supports client-side key override and custom model dropdown selection.

### 4. **Professional PDF Generation (FPDF2)**
- Generates styled corporate research reports from structured JSON.
- Includes margins, titles, headers, footers with page numbers, layout panels, and clickable website links.
- Uses sanitized filenames and safe resolution rules to eliminate path-traversal vulnerabilities.

### 5. **Rich Discord Pipeline Notifications**
- Integrates Discord notification channels using webhooks or bot token/channel credentials.
- Auto-sends **rich colored embeds** formatted with emojis, applicant metadata, company details, products, pain points, and competitor links.

### 6. **Stunning Dark Glassmorphic Interface**
- Implements custom CSS variables, animated gradient shifts, glass panel layouts, keyboard shortcuts, welcome chips, collapsible mobile overlays, and visual research progress pipeline indicators (simulated steps).
- Clean, responsive design for desktop, tablet, and mobile.

---

## 🛠️ Technology Stack

- **Frontend**: React (Vite) + Lucide Icons + custom CSS
- **Backend**: Python (FastAPI) + Uvicorn
- **AI Integrations**: OpenRouter + Serper.dev
- **PDF Generation**: FPDF2
- **Crawling/Scraping**: BeautifulSoup4 + HTTPX

---

## 🚀 Setup & Execution

### 1. Environment Configuration

Copy the backend example file to configure variables (or you can enter them directly in the UI settings sidebar!):
```bash
cd backend
cp .env.example .env
```

Set up API keys in `backend/.env`:
```ini
SERPER_API_KEY=your_serper_key
OPENROUTER_API_KEY=your_openrouter_key

# Optional Discord Integration
DISCORD_WEBHOOK_URL=your_webhook
# Or Bot API:
DISCORD_BOT_TOKEN=your_bot_token
DISCORD_CHANNEL_ID=your_channel_id
```

### 2. Run Backend (FastAPI)

Prerequisites: Python 3.9+
```bash
cd backend
# (Optional) Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server (default port: 8000)
uvicorn main:app --reload
```

Verify backend health at: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### 3. Run Frontend (React+Vite)

Prerequisites: Node.js 18+
```bash
cd frontend

# Install package dependencies
npm install

# Run Vite dev server
npm run dev

# Or build for production
npm run build
npm run preview
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🔒 Security Enhancements

- **Path Traversal Protection**: Sanitizes filename inputs on `/api/download_pdf` by resolving absolute canonical paths to ensure they remain inside the dedicated secure `reports/` subdirectory.
- **Client Configuration Isolation**: Allows users to override API keys at runtime via the browser state (persisted to localStorage), preventing server exposure of keys in multi-user settings.
- **Dependency Cleanups**: Replaced insecure and unmaintained libraries (like `pdfkit`, which requires OS-level wkhtmltopdf binaries) with pure-python `fpdf2` and `markdown` generators.
