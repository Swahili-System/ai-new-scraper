# Swahili News Dataset Creator

This project creates a high-quality Swahili news dataset by scraping and processing articles from major Tanzanian news sources.

## 🎯 Features

- Scrapes articles from multiple Tanzanian news sources
- Cleans and preprocesses text
- Removes duplicates and non-Swahili content
- Outputs a clean JSONL dataset ready for fine-tuning

## 📋 Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## 🚀 Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the scraper:
```bash
python scraper.py
```

## 📊 Dataset Structure

The output dataset will be saved as `dataset/swahili_news.jsonl` with the following format:

```json
{"text": "article text here"}
```

## 🔍 Data Sources

- Mwananchi (https://www.mwananchi.co.tz)
- Habari Leo (https://www.habarileo.co.tz)
- IPP Media (https://www.ippmedia.com)
- BBC Swahili (https://www.bbc.com/swahili)
- VOA Swahili (https://www.voaswahili.com)

