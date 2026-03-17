from transformers import pipeline
import numpy as np
import gc

class CommentAnalyzer:
    def __init__(self, default_model: str = "nlptown/bert-base-multilingual-uncased-sentiment"):
        """
        Prepare a dictionary to act as a 'cache pool' of models for faster import.
        Use gc to clear up unused models.
        """
        self.default_model = default_model
        self._pipelines = {}
        self.max_cache_size = 2 

    def _get_pipeline(self, model_name: str):
        # 1. If the model is already in the cache, return it directly (fastest route)
        if model_name in self._pipelines:
            return self._pipelines[model_name]

        # 2. If the model is not in the cache, prepare to load it...
        print(f"Preparing to load new model '{model_name}'...")

        # Safety mechanism: If the cache reaches its maximum capacity
        if len(self._pipelines) >= self.max_cache_size:
            # Evict the oldest model (the first one inserted into the dictionary)
            oldest_model_name = next(iter(self._pipelines))
            print(f"Cache limit reached! Unloading old model '{oldest_model_name}' from memory...")
            
            # Remove the reference from the dictionary
            del self._pipelines[oldest_model_name]
            
            # Force Python to run garbage collection immediately
            gc.collect() 

        # 3. With space freed up, safely load the new model and store it in the cache
        self._pipelines[model_name] = pipeline(
            "sentiment-analysis", 
            model=model_name, 
            device=-1
        )   # type: ignore
        return self._pipelines[model_name]
    
    def analyze(self, comments: list[str], model: str = None) -> float | list[dict]:
        """
        Batch analyze the sentiment of comments. If no model is provided, the default model is used.
        """
        target_model = model or self.default_model 
        # Retrieve the corresponding Pipeline from the cache pool
        classifier = self._get_pipeline(target_model)
        # Execute batch inference
        results = classifier(comments, batch_size=8)

        if target_model == self.default_model:
            # Logic processing: Map 1-5 stars to a 1-10 score
            # Each result has the format: {'label': '4 stars', 'score': 0.61}
            scores = []
            for result in results:
                star_rating = int(result['label'].split()[0])
                score = round((star_rating - 1) * 2.25 + 1)
                scores.append(score)   
                
            return np.mean(scores)
        
        return results

# ================= Testing =================
if __name__ == "__main__":
    test_comments = [
        "This is the worst experience of my life, completely broken!",
        "Not bad, but could be improved. Has some bugs.",
        "Absolutely phenomenal! Changed my workflow completely."
    ]

    analyzer = CommentAnalyzer()
    
    print("--- Scenario 1: Pass nothing, use the default model ---")
    print(analyzer.analyze(test_comments))

    print("\n--- Scenario 2: Still pass nothing ---")
    print(analyzer.analyze(["Not bad, could be better."]))

    print("\n--- Scenario 3: Explicitly pass the optional parameter, switch to a new model ---")
    financial_scores = analyzer.analyze(
        comments=["The stock price is crashing!"], 
        model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
    )
    print(financial_scores)