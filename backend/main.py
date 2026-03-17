from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.concurrency import run_in_threadpool
import uvicorn
import json
import os
import shutil
import traceback
import pandas as pd

from config import get_api_key
from schemas import UserRequest, UserResponse
from llm_interface import AihubmixClient
from services import analyze_post_potential, CommentAnalyzer, ICPScorer, DataExtractor

def create_app() -> FastAPI:
   api_key = get_api_key()
   
   print("Initializing global AI models and clients...")
   # Global singleton initialization
   ai_client = AihubmixClient(api_key=api_key)
   comment_analyzer = CommentAnalyzer()
   icp_scorer = ICPScorer()
   print("Initialization complete.")

   app = FastAPI(title="LinkedIn Post Analyzer API")

   # ==========================================
   # Helper functions: Synchronous scraper and core analysis flow
   # ==========================================
   def extract_data_sync(url_str: str):
      """Encapsulate the synchronous scraping logic to put into the thread pool later"""
      with DataExtractor(headless=True) as extractor:
         post_data, comments_data = extractor.scrape_post(url_str)
         profiles_data = extractor.scrape_profiles(comments_data)
         extractor.save_data(post_data, comments_data, profiles_data, output_dir='data')

   def run_analysis_pipeline(reference_icp: str) -> UserResponse:
      """Core analysis pipeline (shared by URL scraping and file upload)"""
      try:
         # 1. Read Post
         post_df = pd.read_csv('data/post_data.csv')
         post_text = post_df['post_text'].iloc[0] if not post_df.empty and 'post_text' in post_df else None
         if not post_text:
            raise ValueError("Could not retrieve post text from data.")

         # 2. Post Potential Score & Reason
         llm_response_str = analyze_post_potential(ai_client, post_text)
         try:
            clean_json_str = llm_response_str.strip().strip('```json').strip('```')
            llm_result = json.loads(clean_json_str)
            post_score = int(llm_result.get('score', 0))
            advice = llm_result.get('reason', 'No specific advice provided by LLM.')
         except Exception as e:
            print(f"Failed to parse LLM response: {e}")
            post_score = 0
            advice = "Analysis completed, but failed to parse LLM strict JSON output."

         # 3. Comment Score
         comment_score = 0
         comments_df = pd.read_csv('data/comments_data.csv')
         if 'text' in comments_df.columns:
            comment_texts = comments_df['text'].dropna().astype(str).tolist()
            if comment_texts:
               comment_score = int(comment_analyzer.analyze(comments=comment_texts))

         # 4. ICP score
         icp_score = 0
         comments_csv_path = 'data/comments_data.csv'
         if not comments_df.empty:
            # Pass the user-provided reference_icp during the call
            icp_score = round(icp_scorer.evaluate_batch(comments_csv_path, reference_icp))

         # 5. Return the 3 scores and 1 reason according to the Schema
         return UserResponse(
            post_score=post_score,
            comment_score=comment_score,
            ICP_score=icp_score,
            advice=advice
         )

      except Exception as e:
         traceback.print_exc()
         raise HTTPException(status_code=500, detail=f"Analysis pipeline error: {str(e)}")


   # ==========================================
   # API Routes
   # ==========================================
   
   @app.post("/api/analyze/url", response_model=UserResponse)
   async def analyze_by_url(request: UserRequest):
      """Scenario 1: User provides a LinkedIn post URL and Reference ICP to trigger the scraper and analyze"""
      try:
         url_str = str(request.post_url)
         reference_icp = request.reference_icp

         # Asynchronously schedule the scraper to extract data (prevent blocking the main thread)
         await run_in_threadpool(extract_data_sync, url_str)
         
         # Enter the common analysis flow
         return run_analysis_pipeline(reference_icp)

      except Exception as e:
         traceback.print_exc()
         raise HTTPException(status_code=500, detail=f"Error processing URL: {str(e)}")

   @app.post("/api/analyze/files", response_model=UserResponse)
   async def analyze_by_files(
      reference_icp: str = Form(..., description="The Ideal Customer Profile description"),
      post_file: UploadFile = File(...),
      comments_file: UploadFile = File(...)
   ):
      """Scenario 2: User directly uploads post_data and comments_data CSV files"""
      try:
         os.makedirs('data', exist_ok=True)
         
         # Overwrite and save the user-uploaded CSV files to the specified directory
         with open('data/post_data.csv', 'wb') as f:
            shutil.copyfileobj(post_file.file, f)
         with open('data/comments_data.csv', 'wb') as f:
            shutil.copyfileobj(comments_file.file, f)
               
         # Enter the common analysis flow directly
         return run_analysis_pipeline(reference_icp)
         
      except Exception as e:
         traceback.print_exc()
         raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")

   return app

app = create_app()

if __name__ == "__main__":
   uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)