# 🚀 LinkedIn Post Analyzer

A full-stack AI application designed for growth hackers and B2B marketers. This tool evaluates the virality potential of a LinkedIn post, analyzes the sentiment of the audience, and scores commenters against your Ideal Customer Profile (ICP).

## ✨ Features

The system supports two primary modes of operation:
- **Mode 1: Analyze by URL**: Input a LinkedIn post URL and an ICP description. The system will automatically extract the post, comments, and commenters' profiles, then run the multi-dimensional analysis.
- **Mode 2: Analyze by Files**: Upload your own `post_data.csv` and `comments_data.csv` files along with an ICP description to bypass the scraping phase and directly run the analysis.

### 📊 Three-Dimensional Scoring Engine
1. **Post Potential Score (1-10):** Evaluates the hook, readability, value, and CTA of the post's text using an LLM. Includes actionable advice for improvement.
2. **Comment Sentiment Score (1-10):** A batch sentiment analysis pipeline powered by a local BERT model to gauge the overall audience reaction.
3. **ICP Match Score (1-10):** A hybrid scoring engine combining rule-based heuristics (followers, likes, account type) and semantic vector similarity (SentenceTransformers) to determine how well the commenters match your target audience.

## 🛠️ Tech Stack

- **Backend:** FastAPI, Python, Pydantic, Uvicorn
- **AI & ML:** - LLM Integration (AihubmixClient / GPT models)
  - HuggingFace Transformers (`nlptown/bert-base-multilingual-uncased-sentiment`)
  - SentenceTransformers (`all-MiniLM-L6-v2`)
- **Data Scraping & Processing:** Selenium, BeautifulSoup4, Pandas, NumPy
- **Frontend:** Vanilla HTML, CSS, JavaScript (Fetch API)

## 📂 Project Structure

```text
linkedin-post-analyzer/
├── backend/
│   ├── main.py                 # FastAPI application and routing
│   ├── schemas.py              # Pydantic models for request/response validation
│   ├── config.py               # Configuration and API key management
│   ├── llm_interface/          # LLM client wrappers
│   ├── services/
│   │   ├── data_extractor.py   # Selenium & BS4 scraper
│   │   ├── analyze_post.py     # LLM evaluation prompt and logic
│   │   ├── comment_analyzer.py # BERT-based sentiment analysis with LRU caching
│   │   └── ICP_scorer.py       # Rule-based + Semantic vector ICP matching
│   └── data/                   # Directory for storing generated CSV files
├── frontend/
│   ├── index.html              # Clean, minimalist UI
│   ├── style.css               # Vanilla CSS styling
│   └── app.js                  # Frontend logic and API integration
└── README.md
```
## ⚠️ Disclaimer

> [!IMPORTANT]
> **This project is for personal educational and research purposes only. Do not use it for commercial purposes.**
>
> 1.  **Compliance Notice**: LinkedIn's Terms of Service strictly prohibit unauthorized automated data scraping. Using this tool to crawl LinkedIn data may result in your account being restricted, banned, or lead to legal consequences.
> 2.  **Liability**: The developer assumes no responsibility for any account loss, data breaches, or legal disputes arising from the use of this tool. Please conduct your technical research in a local environment while strictly adhering to relevant laws and platform regulations.
> 3.  **Data Privacy**: Please respect the privacy of others. Do not redistribute, sell, or illegally store any data extracted through this tool.
