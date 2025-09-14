from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timedelta
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import pandas as pd

class CologneRecommender:
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        self.scaler = StandardScaler()
        self.cologne_features = None
        self.wear_patterns = None
        
    def build_features(self, colognes: List[Any], wear_history: List[Any]) -> None:
        """Build feature matrices for recommendations"""
        if not colognes:
            return
            
        # Create cologne feature matrix
        cologne_data = []
        for cologne in colognes:
            # Combine notes and classifications into text features
            notes = ' '.join([str(note.name) for note in cologne.notes])
            classifications = ' '.join([str(c.name) for c in cologne.classifications])
            text_features = f"{notes} {classifications}".strip()
            
            cologne_data.append({
                'id': int(cologne.id),
                'name': str(cologne.name),
                'brand': str(cologne.brand),
                'text_features': text_features if text_features else 'unknown',
                'notes_count': len(cologne.notes),
                'classifications_count': len(cologne.classifications)
            })
        
        if not cologne_data:
            return
            
        # Convert to DataFrame for easier manipulation
        self.cologne_df = pd.DataFrame(cologne_data)
        
        # Build TF-IDF features for content-based similarity
        if cologne_data and any(item['text_features'] != 'unknown' for item in cologne_data):
            text_features = [item['text_features'] for item in cologne_data]
            self.cologne_features = self.tfidf_vectorizer.fit_transform(text_features)
        
        # Build wear pattern features
        self._build_wear_patterns(wear_history)
    
    def _build_wear_patterns(self, wear_history: List[Any]) -> None:
        """Analyze wear patterns for behavioral recommendations"""
        if not wear_history:
            self.wear_patterns = {}
            return
            
        patterns = {}
        current_date = datetime.now()
        
        for wear in wear_history:
            cologne_id = int(wear.cologne_id)
            if cologne_id not in patterns:
                patterns[cologne_id] = {
                    'total_wears': 0,
                    'avg_rating': 0.0,
                    'ratings': [],
                    'seasons': {},
                    'occasions': {},
                    'last_worn': None,
                    'days_since_worn': float('inf')
                }
            
            pattern = patterns[cologne_id]
            pattern['total_wears'] += 1
            
            # Rating tracking
            if wear.rating:
                pattern['ratings'].append(wear.rating)
                pattern['avg_rating'] = sum(pattern['ratings']) / len(pattern['ratings'])
            
            # Season/occasion tracking
            season = str(wear.season).lower()
            occasion = str(wear.occasion).lower()
            pattern['seasons'][season] = pattern['seasons'].get(season, 0) + 1
            pattern['occasions'][occasion] = pattern['occasions'].get(occasion, 0) + 1
            
            # Recency tracking
            if not pattern['last_worn'] or wear.date_worn > pattern['last_worn']:
                pattern['last_worn'] = wear.date_worn
                days_since = (current_date - wear.date_worn).days
                pattern['days_since_worn'] = days_since
        
        self.wear_patterns = patterns
    
    def get_content_recommendations(self, cologne_id: int, n_recommendations: int = 5) -> List[Tuple[int, float]]:
        """Get recommendations based on cologne similarity (notes, classifications)"""
        if self.cologne_features is None or self.cologne_df is None:
            return []
            
        try:
            # Find the cologne index
            cologne_idx = self.cologne_df[self.cologne_df['id'] == cologne_id].index[0]
        except IndexError:
            return []
        
        # Compute cosine similarity
        # Extract single row feature vector safely
        try:
            import numpy as np
            from typing import Any
            
            # Force convert to dense array using getattr to avoid type checker issues
            features_matrix: Any = self.cologne_features
            if hasattr(features_matrix, 'toarray'):
                # Use getattr to bypass type checking
                toarray_method = getattr(features_matrix, 'toarray')
                features_array = np.array(toarray_method())
            else:
                features_array = np.array(features_matrix)
            
            # Extract single cologne features safely
            cologne_feature = features_array[cologne_idx:cologne_idx+1]
            similarities = cosine_similarity(cologne_feature, features_array).flatten()
            
        except (IndexError, AttributeError, ImportError) as e:
            # Fallback: return empty if matrix operations fail
            return []
        
        # Get similar colognes (excluding the input cologne)
        similar_indices = similarities.argsort()[::-1][1:n_recommendations+1]
        
        recommendations = []
        for idx in similar_indices:
            if similarities[idx] > 0:  # Only recommend if there's some similarity
                cologne_id_rec = int(self.cologne_df.iloc[idx]['id'])
                recommendations.append((cologne_id_rec, similarities[idx]))
        
        return recommendations
    
    def get_behavioral_recommendations(self, season: Optional[str] = None, 
                                    occasion: Optional[str] = None,
                                    n_recommendations: int = 5) -> List[Tuple[int, float]]:
        """Get recommendations based on wear patterns and preferences"""
        if not self.wear_patterns:
            return []
        
        current_season = season or self._get_current_season()
        
        recommendations = []
        for cologne_id, pattern in self.wear_patterns.items():
            score = 0.0
            
            # Base score from average rating
            if pattern['avg_rating'] > 0:
                score += pattern['avg_rating'] / 5.0  # Normalize to 0-1
            
            # Season preference boost
            if current_season in pattern['seasons']:
                season_freq = pattern['seasons'][current_season] / pattern['total_wears']
                score += season_freq * 0.5
            
            # Occasion preference boost
            if occasion and occasion in pattern['occasions']:
                occasion_freq = pattern['occasions'][occasion] / pattern['total_wears']
                score += occasion_freq * 0.3
            
            # Recency penalty (haven't worn in a while = higher score)
            days_since = pattern['days_since_worn']
            if days_since < float('inf'):
                # Boost score for colognes not worn recently
                recency_boost = min(days_since / 30.0, 1.0) * 0.4  # Max 30 days = full boost
                score += recency_boost
            else:
                score += 0.4  # Never worn = high boost
            
            recommendations.append((cologne_id, score))
        
        # Sort by score and return top N
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:n_recommendations]
    
    def get_hybrid_recommendations(self, cologne_id: Optional[int] = None,
                                 season: Optional[str] = None,
                                 occasion: Optional[str] = None,
                                 n_recommendations: int = 5) -> List[Tuple[int, float]]:
        """Combine content-based and behavioral recommendations"""
        content_recs = []
        behavioral_recs = []
        
        # Get content-based recommendations if cologne_id provided
        if cologne_id:
            content_recs = self.get_content_recommendations(cologne_id, n_recommendations * 2)
        
        # Get behavioral recommendations
        behavioral_recs = self.get_behavioral_recommendations(season, occasion, n_recommendations * 2)
        
        # Combine and weight recommendations
        combined_scores = {}
        
        # Add content-based scores (weight: 0.4)
        for rec_id, score in content_recs:
            combined_scores[rec_id] = combined_scores.get(rec_id, 0) + score * 0.4
        
        # Add behavioral scores (weight: 0.6)
        for rec_id, score in behavioral_recs:
            combined_scores[rec_id] = combined_scores.get(rec_id, 0) + score * 0.6
        
        # Sort and return top recommendations
        recommendations = [(rec_id, score) for rec_id, score in combined_scores.items()]
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return recommendations[:n_recommendations]
    
    def get_seasonal_recommendations(self, n_recommendations: int = 5) -> List[Tuple[int, float]]:
        """Get recommendations optimized for current season"""
        current_season = self._get_current_season()
        return self.get_behavioral_recommendations(season=current_season, n_recommendations=n_recommendations)
    
    def get_discovery_recommendations(self, n_recommendations: int = 5) -> List[Tuple[int, float]]:
        """Recommend colognes that haven't been worn recently or at all"""
        if not self.wear_patterns or self.cologne_df is None:
            return []
        
        # Get all cologne IDs
        all_cologne_ids = set(self.cologne_df['id'].tolist())
        worn_cologne_ids = set(self.wear_patterns.keys())
        
        # Colognes never worn get highest priority
        never_worn = list(all_cologne_ids - worn_cologne_ids)
        
        recommendations = []
        
        # Add never worn colognes with high scores
        for cologne_id in never_worn[:n_recommendations]:
            recommendations.append((cologne_id, 1.0))
        
        # Fill remaining slots with least recently worn
        if len(recommendations) < n_recommendations:
            worn_colognes = [(cid, pattern['days_since_worn']) 
                           for cid, pattern in self.wear_patterns.items()]
            worn_colognes.sort(key=lambda x: x[1], reverse=True)  # Most days since worn first
            
            remaining = n_recommendations - len(recommendations)
            for cologne_id, days_since in worn_colognes[:remaining]:
                # Score based on how long it's been since worn
                score = min(days_since / 60.0, 1.0)  # Max 60 days = full score
                recommendations.append((cologne_id, score))
        
        return recommendations
    
    def _get_current_season(self) -> str:
        """Determine current season based on month"""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'fall'
    
    def get_recommendation_explanation(self, cologne_id: int, score: float, 
                                    recommendation_type: str = "hybrid") -> str:
        """Generate human-readable explanation for why a cologne was recommended"""
        if self.cologne_df is None:
            return f"Recommended (score: {score:.2f})"
        
        try:
            cologne_info = self.cologne_df[self.cologne_df['id'] == cologne_id].iloc[0]
            cologne_name = cologne_info['name']
        except (IndexError, KeyError):
            cologne_name = f"Cologne ID {cologne_id}"
        
        explanations = []
        
        if self.wear_patterns and cologne_id in self.wear_patterns:
            pattern = self.wear_patterns[cologne_id]
            
            if pattern['avg_rating'] > 4.0:
                explanations.append("highly rated by you")
            elif pattern['avg_rating'] > 3.0:
                explanations.append("you've rated this positively")
            
            if pattern['days_since_worn'] > 30:
                explanations.append("haven't worn recently")
            elif pattern['days_since_worn'] == float('inf'):
                explanations.append("never worn before")
            
            # Season preference
            current_season = self._get_current_season()
            if (current_season in pattern['seasons'] and 
                pattern['seasons'][current_season] / pattern['total_wears'] > 0.3):
                explanations.append(f"good for {current_season}")
        
        else:
            explanations.append("new discovery")
        
        if explanations:
            return f"{cologne_name}: {', '.join(explanations)} (score: {score:.2f})"
        else:
            return f"{cologne_name}: recommended (score: {score:.2f})"