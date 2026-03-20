# LinkedIn Post Analyzer

A full-stack AI application designed for growth hackers and B2B marketers. This tool evaluates the virality potential of a LinkedIn post, analyzes the sentiment of the audience, and scores commenters against your Ideal Customer Profile (ICP).

## ✨ Features

### Dual-Mode Input 📤

- #### *via URL*

  Input the `URL` of a LinkedIn post and an `ICP description`. The system will automatically extract the post, comments, and commenters' profiles, then run a multi-dimensional analysis.
  
- #### *via CSV*

  Upload your own `post_data.csv` and `comments_data.csv` files along with an `ICP description` to bypass the scraping phase and directly run the analysis.

### Three-Dimensional Scoring Engine 💯

- #### *Post Potential Score* <kbd>1-10</kbd>
   Evaluates the hook, readability, value, and CTA of the post's text using an LLM. Includes actionable advice for improvement.
   
- #### *Comment Sentiment Score* <kbd>1-10</kbd>
   A batch sentiment analysis pipeline powered by a local BERT model to gauge the overall audience reaction.
   
- #### *ICP Match Score* <kbd>1-10</kbd>
   A hybrid scoring engine combining rule-based heuristics (followers, likes, account type) and semantic vector similarity (SentenceTransformers) to determine how well the commenters match your target audience.

## 🛠️ Tech Stack

- **Backend:**
  - Python
  - Pydantic
  - FastAPI
  - Uvicorn
- **AI & NLP:**
  - AIHubMix
  - HuggingFace Transformers
  - SentenceTransformers
- **Data Scraping:**
  - Selenium
  - BeautifulSoup4
- **Frontend:**
  - Vanilla HTML
  - CSS
  - JavaScript

## 💡 Engineering Highlights

This project is built with production-readiness and scalability in mind, incorporating several software engineering best practices:

* **Non-Blocking Asynchronous Architecture:** Data scraping with Selenium is inherently a synchronous, I/O-blocking operation. To prevent this from freezing the FastAPI ASGI event loop, the scraper is encapsulated and dispatched to a separate thread using `run_in_threadpool`. This ensures the API remains highly responsive and capable of handling concurrent requests.
* **Smart Memory Management & Custom LRU Cache:** Loading large HuggingFace Transformer models for sentiment analysis can quickly lead to Out-Of-Memory (OOM) errors. The `CommentAnalyzer` implements a custom LRU-style (Least Recently Used) caching mechanism with a strict memory limit. When the cache is full, it automatically evicts the oldest model and forces garbage collection (`gc.collect()`) to safely free up RAM/VRAM.
* **Model Agnosticism & Flexibility:** The system is designed to avoid vendor lock-in. Both the LLM for `Post Potential` and the NLP pipeline for `Comment Sentiment` accept dynamic `model` parameters. You can easily hot-swap the default `gpt-4.1-free` or `nlptown/bert-base...` models for domain-specific fine-tuned alternatives without altering the core logic.
* **Secure Configuration Management:** Sensitive credentials, such as LLM API keys, are strictly decoupled from the codebase. They are securely loaded via `.env` files using a dedicated `config.py` module, preventing accidental leaks of hardcoded secrets into version control.
* **Safe Resource Teardown (Context Managers):** The Selenium-based `DataExtractor` is implemented as a Python Context Manager (`__enter__` and `__exit__` magic methods). This guarantees that the browser driver safely quits and cleans up background processes, even if a fatal exception occurs during the scraping phase, preventing zombie Chrome processes from consuming server resources.
* **Hybrid Scoring Engine:** The ICP (Ideal Customer Profile) Scorer doesn't rely blindly on AI. It uses a robust hybrid approach: combining a deterministic **Rule-Based Engine** (scoring by followers, likes, and account type) with a **Semantic Vector Engine** (using SentenceTransformers to calculate cosine similarity between user professional traits and the reference ICP). This makes the final score both intelligent and highly explainable. 
* **Resilient DOM Parsing:** The web scraper relies on dynamic explicit waits (`WebDriverWait(driver, 20).until(...)`) rather than static `time.sleep()`. This makes data extraction highly resilient to network latency and fluctuating page load times.

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
