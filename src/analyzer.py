import json
import os
import glob
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
import re

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')

class LinkedInAnalyzer:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        # Add common contractions and LinkedIn filler words
        self.stop_words.update({
            "im", "youre", "theyre", "weve", "ive", "dont", "doesnt", "didnt", "cant", "couldnt", "wouldnt", "shouldnt", "wont", "isnt", "arent", "wasnt", "werent", "linkedin", "get", "got", "new", "work", "great", "like", "just", "one", "us", "make", "see", "use", "using", "used", "also", "even", "still", "much", "many", "may", "might", "well", "really", "need", "want", "way", "time", "now", "today", "next", "last", "year", "years", "day", "days", "week", "weeks", "month", "months", "etc"
        })
        self.posts_data = []
        self.df = None

    def load_data(self, data_dir='data/raw'):
        """Load all JSON files from the data directory."""
        json_files = glob.glob(os.path.join(data_dir, '*.json'))
        for file in json_files:
            with open(file, 'r', encoding='utf-8') as f:
                self.posts_data.extend(json.load(f))
        
        # Convert to DataFrame
        self.df = pd.DataFrame(self.posts_data)

    def preprocess_text(self, text):
        """Clean and preprocess text data, keeping only nouns/proper nouns."""
        text = text.lower()
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\d+', '', text)
        tokens = word_tokenize(text)
        # POS tagging
        tagged = nltk.pos_tag(tokens)
        # Keep only nouns and proper nouns
        tokens = [word for word, pos in tagged if pos in ("NN", "NNS", "NNP", "NNPS")]
        # Remove stopwords and short words
        tokens = [token for token in tokens if token not in self.stop_words and len(token) > 2]
        return ' '.join(tokens)

    def analyze_topics(self, top_n=10):
        """Analyze and extract top topics from posts."""
        if self.df is None or len(self.df) == 0:
            return []

        # Preprocess all posts
        processed_texts = self.df['text'].apply(self.preprocess_text)
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(max_features=1000)
        tfidf_matrix = vectorizer.fit_transform(processed_texts)
        
        # Get feature names
        feature_names = vectorizer.get_feature_names_out()
        
        # Calculate average TF-IDF scores for each term
        avg_tfidf = tfidf_matrix.mean(axis=0).A1
        
        # Create a dictionary of terms and their scores
        term_scores = dict(zip(feature_names, avg_tfidf))
        
        # Get top N terms
        top_terms = sorted(term_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        return top_terms

    def analyze_engagement(self):
        """Analyze engagement patterns."""
        if self.df is None or len(self.df) == 0:
            return {}

        # Calculate average engagement metrics
        avg_engagement = {
            'likes': self.df['engagement'].apply(lambda x: x['likes']).mean(),
            'comments': self.df['engagement'].apply(lambda x: x['comments']).mean(),
            'shares': self.df['engagement'].apply(lambda x: x['shares']).mean()
        }

        # Find posts with highest engagement
        self.df['total_engagement'] = self.df['engagement'].apply(
            lambda x: x['likes'] + x['comments'] + x['shares']
        )
        top_posts = self.df.nlargest(5, 'total_engagement')

        return {
            'average_engagement': avg_engagement,
            'top_posts': top_posts[['text', 'total_engagement']].to_dict('records')
        }

    def generate_insights(self):
        """Generate comprehensive insights from the data."""
        if self.df is None or len(self.df) == 0:
            return {}

        insights = {
            'top_topics': self.analyze_topics(),
            'engagement_analysis': self.analyze_engagement(),
            'total_posts_analyzed': len(self.df),
            'date_range': {
                'start': self.df['timestamp'].min(),
                'end': self.df['timestamp'].max()
            }
        }

        return insights

    def save_insights(self, insights, filename=None):
        """Save analysis insights to a JSON file."""
        if filename is None:
            filename = f"data/analysis_insights_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(insights, f, ensure_ascii=False, indent=2)

def main():
    analyzer = LinkedInAnalyzer()
    try:
        print("Loading LinkedIn data...")
        analyzer.load_data()
        
        print("Generating insights...")
        insights = analyzer.generate_insights()
        
        print("Saving insights...")
        analyzer.save_insights(insights)
        
        print("Analysis complete!")
        print(f"\nTop Topics:")
        for topic, score in insights['top_topics']:
            print(f"- {topic}: {score:.3f}")
        
        print(f"\nAverage Engagement:")
        for metric, value in insights['engagement_analysis']['average_engagement'].items():
            print(f"- {metric}: {value:.2f}")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 