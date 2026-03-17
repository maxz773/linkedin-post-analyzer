from fastapi import FastAPI, HTTPException
from config import get_api_key
from dotenv import load_dotenv
import uvicorn
import pandas as pd
from schemas import EvaluationResult, UserRequest, UserResponse
from llm_interface import AihubmixClient
from services import analyze_post_potential, CommentAnalyzer, ICPScorer, DataExtractor
from utils import load_post_text, load_comments_text

def create_app() -> FastAPI:
    get_api_key()

    app = FastAPI(title="LinkedIn Post Analyzer API")

    @app.post("/api/analyze", response_model='UserResponse')
    async def analyze_post(request: UserRequest):
        try:
            url_str = str(request.post_url)
            cookie_str = request.li_at_cookie

            extractor = DataExtractor(headless=True)
            
            
            # 1. Call the extractor, passing in the URL and Cookie
            post_text = scrape_post(url_str, cookie_str)
            
            if not post_text:
                raise HTTPException(status_code=400, detail="Scraping failed, please check if the URL or Cookie is valid.")

            # 2. Feed the scraped plain text to the LLM for analysis
            # result = await evaluate_post_with_llm(post_text)
            
            # Mock return
            return EvaluationResult(
                score=8,
                reason=f"Analysis successful. The length of the extracted text is {len(post_text)} characters."
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error occurred during analysis: {str(e)}")

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)