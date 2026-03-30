# LinkMetrics - A LinkedIn Post Analyzer

> LinkMetrics is an AI-powered toolkit designed for **growth hackers** and **B2B marketers**. It forecasts the **virality potential** of a LinkedIn post, decodes **audience sentiment**, and identifies high-value leads against your **Ideal Customer Profile (ICP)**.

## ✨ Features

### 📤 Dual-Mode Input

- #### *via URL*

  Input the `URL` of a LinkedIn post and an `ICP description`. The system will automatically extract the post, comments, and commenters' profiles, then run a multi-dimensional analysis.
  
- #### *via CSV*

  Upload your own `post_data.csv` and `comments_data.csv` files along with an `ICP description` to bypass the scraping phase and directly run the analysis.

### 💯 Three-Dimensional Scoring Engine

- #### *Post Potential Score* <kbd>1-10</kbd>
   Evaluates the hook, readability, value, and CTA of the post's text using an external LLM. Includes actionable advice for improvement.
   
- #### *Comment Sentiment Score* <kbd>1-10</kbd>
   A batch sentiment analysis pipeline powered by a local BERT model to gauge the overall audience reaction.
   
- #### *ICP Match Score* <kbd>1-10</kbd>
   A hybrid scoring engine combining rule-based heuristics (followers, likes, account type) and semantic vector similarity (SentenceTransformers) to determine how well the commenters match your target audience.

## 🛠️ Tech Stack

- ***Backend:***
  - Python
  - Pydantic
  - FastAPI
  - Uvicorn
- ***AI & NLP:***
  - AIHubMix
  - HuggingFace Transformers
  - SentenceTransformers
- ***Data Scraping:***
  - Selenium
  - BeautifulSoup4
- ***Frontend:***
  - Vanilla HTML
  - CSS
  - JavaScript

## 💡 Engineering Highlights

This project is built with production-readiness and scalability in mind, incorporating several software engineering best practices:

* ***Asynchronous Non-Blocking I/O:*** \
  Leverages `run_in_threadpool` to offload synchronous Selenium scraping tasks. This prevents the FastAPI event loop from freezing, ensuring high responsiveness and concurrent request handling.

* ***Hot-Swappable Model Integration:*** \
  Decouples core logic from specific models. Both the LLM and BERT pipelines support **dynamic model parameters**, allowing seamless **hot-swapping of models** within their operational contexts.

* ***Smart In-Memory LRU Caching:*** \
  Optimizes inference speed by maintaining a custom LRU cache that keeps high-frequency local models **resident in RAM**, eliminating **cold-start latencies** from disk I/O. \
  To ensure system stability, a strict capacity limit automatically evicts the oldest models and triggers `gc.collect()`, preventing Out-Of-Memory (OOM) errors even under heavy workloads.

* ***Secure Config Management:*** \
  Leverages **Docker Secrets** for file-based credential injection at `/run/secrets/`, managed via a dedicated `config.py` module. This ensures API keys are decoupled from the codebase and shielded from environment variable leakage.

* ***Safe Resource Lifecycle:*** \
  Implements the `DataExtractor` as a Python Context Manager (`__enter__`/`__exit__`). This guarantees that Selenium browser instances are always terminated and system resources are cleaned up, even if an exception occurs.

* ***Resilient Web Scraping:*** \
  Uses `WebDriverWait` with dynamic explicit waits instead of static `time.sleep()`. This makes the scraping process robust against network latency and fluctuating page load speeds.


## 📂 Project Structure

```text
linkmetrics/
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
