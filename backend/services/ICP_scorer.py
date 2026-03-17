import pandas as pd
from sentence_transformers import SentenceTransformer
from sentence_transformers import util

class ICPScorer:
    def __init__(self, reference_icp_text: str):
        """
        Initialize the scorer and load the lightweight vector model.
        """
        self.reference_icp_text = reference_icp_text
        print("Loading SentenceTransformer vector model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        # Pre-calculate the embedding for the Reference ICP
        self.ref_embedding = self.model.encode([self.reference_icp_text])

    def _score_rules(self, row) -> int:
        """Part 1: Rule-based scoring (Max 50 points)"""
        score = 0
        
        # 1. Followers scoring (Max 20 points)
        followers = pd.to_numeric(row.get('followers', 0), errors='coerce')
        if pd.notna(followers):
            if followers >= 5000: score += 20
            elif followers >= 1000: score += 10
            elif followers >= 500: score += 5
            
        # 2. Likes scoring (Max 15 points)
        likes = pd.to_numeric(row.get('likes', 0), errors='coerce')
        if pd.notna(likes):
            if likes >= 5: score += 15
            elif likes >= 1: score += 5
            
        # 3. Account Type scoring (Max 15 points)
        account_type = str(row.get('account_type', '')).strip().lower()
        if account_type == 'individual':
            score += 15
        elif account_type == 'company':
            score += 5
            
        return score

    def _score_semantic(self, row) -> int:
        """Part 2: Vector semantic similarity scoring (Max 50 points)"""
        # Extract text features
        features = [
            str(row.get('position', '')), 
            str(row.get('occupation', '')), 
            str(row.get('industry', ''))
        ]
        # Filter out 'nan' strings and empty values
        clean_features = [f for f in features if f.lower() != 'nan' and f.strip()]
        combined_text = " | ".join(clean_features)
        
        # If the person has no professional info, assign 0 points directly
        if not combined_text:
            return 0
            
        # Calculate the embedding for the user's professional text
        user_embedding = self.model.encode([combined_text])
        # Calculate cosine similarity (between -1 and 1)
        sim = util.cos_sim(user_embedding, self.ref_embedding).item()
        
        # Map the similarity to a 0 - 50 point range
        # Similarity usually fluctuates between 0.1 and 0.8; apply a slight amplification mechanism
        sim_score = max(0, min(50, int((sim * 1.5) * 50))) 
        return sim_score

    def evaluate_batch(self, csv_path: str):
        """Batch evaluate all commenters"""
        print(f"Reading data: {csv_path}")
        df = pd.read_csv(csv_path)
        
        rule_scores = []
        semantic_scores = []
        total_scores = []
        
        print("Performing ICP match scoring...")
        for _, row in df.iterrows():
            r_score = self._score_rules(row)
            s_score = self._score_semantic(row)
            
            rule_scores.append(r_score)
            semantic_scores.append(s_score)
            total_scores.append(r_score + s_score)
            
        # Append the scoring results to the original dataframe
        df['score_rules'] = rule_scores
        df['score_semantic'] = semantic_scores
        df['icp_match_score'] = total_scores
        
        # Sort by total score in descending order and save as csv
        df.sort_values(by='icp_match_score', ascending=False).to_csv('data/comments_with_scores.csv', index=False)
        print("CSV successfully exported!")

        return df['icp_match_score'].mean()
