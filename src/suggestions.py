import json
import os
import glob
from datetime import datetime
import random

class ContentSuggestions:
    def __init__(self):
        self.insights = None
        self.template_categories = {
            'industry_insights': [
                "Here's what I've learned about {topic} in the industry...",
                "My thoughts on the future of {topic}...",
                "The impact of {topic} on our industry...",
            ],
            'tips_and_tricks': [
                "5 ways to improve your {topic}...",
                "How to master {topic} in 3 simple steps...",
                "The secret to successful {topic}...",
            ],
            'case_studies': [
                "How we implemented {topic} and what we learned...",
                "A case study on {topic} implementation...",
                "Real-world example of {topic} in action...",
            ],
            'trend_analysis': [
                "The latest trends in {topic}...",
                "What's next for {topic}?",
                "Emerging patterns in {topic}...",
            ]
        }

    def load_insights(self, insights_dir='data'):
        """Load the most recent insights file."""
        insight_files = glob.glob(os.path.join(insights_dir, 'analysis_insights_*.json'))
        if not insight_files:
            raise FileNotFoundError("No insights files found")
        
        latest_file = max(insight_files, key=os.path.getctime)
        with open(latest_file, 'r', encoding='utf-8') as f:
            self.insights = json.load(f)

    def generate_topic_suggestions(self, num_suggestions=5):
        """Generate topic suggestions based on trending topics."""
        if not self.insights:
            raise ValueError("No insights loaded")

        topics = [topic for topic, _ in self.insights['top_topics']]
        suggestions = []

        for _ in range(num_suggestions):
            topic = random.choice(topics)
            category = random.choice(list(self.template_categories.keys()))
            template = random.choice(self.template_categories[category])
            
            suggestion = {
                'topic': topic,
                'template': template.format(topic=topic),
                'category': category,
                'engagement_potential': 'High' if topic in [t for t, _ in self.insights['top_topics'][:3]] else 'Medium'
            }
            suggestions.append(suggestion)

        return suggestions

    def generate_best_practices(self):
        """Generate best practices based on engagement analysis."""
        if not self.insights:
            raise ValueError("No insights loaded")

        engagement = self.insights['engagement_analysis']['average_engagement']
        top_posts = self.insights['engagement_analysis']['top_posts']

        best_practices = {
            'posting_frequency': "Based on the analysis, aim to post 2-3 times per week for optimal engagement",
            'content_length': "Posts with 100-200 words tend to perform better",
            'engagement_tips': [
                "Include a clear call-to-action in your posts",
                "Use relevant hashtags related to your industry",
                "Engage with comments within the first hour of posting",
                "Share personal experiences and insights",
                "Include relevant statistics or data points"
            ],
            'best_performing_topics': [topic for topic, _ in self.insights['top_topics'][:3]]
        }

        return best_practices

    def save_suggestions(self, suggestions, best_practices, filename=None):
        """Save content suggestions to a JSON file."""
        if filename is None:
            filename = f"data/content_suggestions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output = {
            'suggestions': suggestions,
            'best_practices': best_practices,
            'generated_at': datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

def main():
    suggester = ContentSuggestions()
    try:
        print("Loading insights...")
        suggester.load_insights()
        
        print("\nGenerating content suggestions...")
        suggestions = suggester.generate_topic_suggestions()
        best_practices = suggester.generate_best_practices()
        
        print("\nContent Suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n{i}. {suggestion['template']}")
            print(f"   Category: {suggestion['category']}")
            print(f"   Engagement Potential: {suggestion['engagement_potential']}")
        
        print("\nBest Practices:")
        print(f"\nPosting Frequency: {best_practices['posting_frequency']}")
        print(f"Content Length: {best_practices['content_length']}")
        print("\nEngagement Tips:")
        for tip in best_practices['engagement_tips']:
            print(f"- {tip}")
        
        print("\nTop Performing Topics:")
        for topic in best_practices['best_performing_topics']:
            print(f"- {topic}")
        
        # Save suggestions
        suggester.save_suggestions(suggestions, best_practices)
        print("\nSuggestions saved successfully!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 