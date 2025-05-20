# LinkedIn Content Analyzer

A web application that analyzes LinkedIn feed content to provide insights and content suggestions based on trending topics and engagement metrics.

## Features

- LinkedIn feed scraping and analysis
- Topic trend analysis
- Engagement metrics tracking
- Content suggestions based on top-performing posts
- Modern web interface with real-time updates

## Tech Stack

- Python 3.9+
- Flask
- Selenium
- NLTK
- scikit-learn
- Tailwind CSS
- Vercel (Deployment)

## Prerequisites

- Python 3.9 or higher
- Chrome browser (for Selenium)
- LinkedIn account

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/linkedin-content-analyzer.git
cd linkedin-content-analyzer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your LinkedIn credentials:
```
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
```

## Development

1. Start the Flask development server:
```bash
python src/app.py
```

2. Open your browser and navigate to `http://localhost:5000`

## Deployment

This application is configured for deployment on Vercel. To deploy:

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy:
```bash
vercel
```

4. Set up environment variables in the Vercel dashboard:
   - `LINKEDIN_EMAIL`
   - `LINKEDIN_PASSWORD`
   - `FLASK_ENV=production`

## Project Structure

```
linkedin-content-analyzer/
├── src/
│   ├── app.py              # Flask application
│   ├── scraper.py          # LinkedIn feed scraper
│   ├── analyzer.py         # Content analysis
│   ├── suggestions.py      # Content suggestions generator
│   └── templates/
│       └── index.html      # Web interface
├── data/                   # Analysis results
├── requirements.txt        # Python dependencies
├── vercel.json            # Vercel configuration
└── README.md              # Project documentation
```

## Security Notes

- Never commit your `.env` file
- Keep your LinkedIn credentials secure
- The application uses HTTPS in production
- API endpoints are rate-limited

## License

MIT License

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request 