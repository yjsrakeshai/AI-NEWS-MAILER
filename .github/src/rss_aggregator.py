#!/usr/bin/env python3
"""
RSS Feed Aggregator for AI News
Fetches and processes RSS feeds from multiple AI news sources
"""

import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from urllib.parse import urlparse
import hashlib
import pytz

def fetch_rss_feed(source: Dict) -> List[Dict]:
    """
    Fetch and parse RSS feed from a single source
    
    Args:
        source: Dictionary containing 'name', 'rss_url', and 'weight'
    
    Returns:
        List of article dictionaries
    """
    articles = []
    
    try:
        # Set timeout and user agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; AI-News-Aggregator/1.0)'
        }
        
        # Parse RSS feed
        feed = feedparser.parse(source['rss_url'], request_headers=headers)
        
        if feed.bozo and hasattr(feed, 'bozo_exception'):
            print(f"⚠️  RSS parsing warning for {source['name']}: {feed.bozo_exception}")
        
        # Process entries
        for entry in feed.entries[:8]:  # Limit to 8 articles per source
            article = parse_rss_entry(entry, source)
            if article and is_recent_article(article):
                articles.append(article)
    
    except Exception as e:
        print(f"❌ Error fetching {source['name']}: {str(e)}")
    
    return articles

def parse_rss_entry(entry, source: Dict) -> Optional[Dict]:
    """
    Parse individual RSS entry into article format
    
    Args:
        entry: RSS entry object
        source: Source information
    
    Returns:
        Article dictionary or None
    """
    try:
        # Extract basic information
        title = getattr(entry, 'title', 'No Title').strip()
        link = getattr(entry, 'link', '').strip()
        
        # Get summary/description
        summary = ''
        if hasattr(entry, 'summary'):
            summary = clean_html(entry.summary)
        elif hasattr(entry, 'description'):
            summary = clean_html(entry.description)
        
        # Truncate summary
        summary = summary[:300] + '...' if len(summary) > 300 else summary
        
        # Parse published date
        published = None
        published_str = ''
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6])
            published_str = published.strftime('%Y-%m-%d %H:%M')
        elif hasattr(entry, 'published'):
            published_str = entry.published
        
        # Check if article is AI-related
        if not is_ai_related(title, summary):
            return None
        
        # Create article object
        article = {
            'title': title,
            'link': link,
            'summary': summary,
            'source': source['name'],
            'source_weight': source.get('weight', 5),
            'published': published,
            'published_str': published_str,
            'hash': generate_article_hash(title, link)
        }
        
        return article
    
    except Exception as e:
        print(f"Error parsing RSS entry: {str(e)}")
        return None

def clean_html(text: str) -> str:
    """Remove HTML tags and clean up text"""
    if not text:
        return ''
    
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', ' ', text)
    # Clean up whitespace
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    # Remove common RSS artifacts
    clean_text = re.sub(r'\[…\]|\[...\]', '', clean_text)
    
    return clean_text

def is_ai_related(title: str, summary: str) -> bool:
    """
    Check if article is AI-related based on keywords
    
    Args:
        title: Article title
        summary: Article summary
    
    Returns:
        True if article is AI-related
    """
    ai_keywords = [
        'artificial intelligence', 'ai', 'machine learning', 'ml', 'deep learning',
        'neural network', 'chatgpt', 'openai', 'anthropic', 'claude', 'llm',
        'large language model', 'generative ai', 'computer vision', 'nlp',
        'natural language processing', 'robotics', 'automation', 'algorithm',
        'tensorflow', 'pytorch', 'hugging face', 'transformer', 'gpt',
        'artificial general intelligence', 'agi', 'foundation model'
    ]
    
    text = (title + ' ' + summary).lower()
    return any(keyword in text for keyword in ai_keywords)

def is_recent_article(article: Dict) -> bool:
    """
    Check if article is from the last 48 hours
    
    Args:
        article: Article dictionary
    
    Returns:
        True if article is recent
    """
    if not article.get('published'):
        return True  # Include if we can't determine age
    
    try:
        now = datetime.now()
        cutoff = now - timedelta(hours=48)
        return article['published'] >= cutoff
    except:
        return True

def generate_article_hash(title: str, link: str) -> str:
    """Generate hash for duplicate detection"""
    content = f"{title}{link}".encode('utf-8')
    return hashlib.md5(content).hexdigest()

def remove_duplicates(articles: List[Dict]) -> List[Dict]:
    """
    Remove duplicate articles based on title similarity and URL
    
    Args:
        articles: List of article dictionaries
    
    Returns:
        List of unique articles
    """
    seen_hashes = set()
    seen_titles = set()
    unique_articles = []
    
    for article in articles:
        # Check hash-based duplicates
        article_hash = article.get('hash', '')
        if article_hash in seen_hashes:
            continue
        
        # Check title-based duplicates (fuzzy matching)
        title_words = set(article['title'].lower().split())
        is_duplicate = False
        
        for seen_title in seen_titles:
            seen_words = set(seen_title.lower().split())
            # If 70% of words match, consider it duplicate
            if len(title_words & seen_words) / max(len(title_words), len(seen_words)) > 0.7:
                is_duplicate = True
                break
        
        if not is_duplicate:
            seen_hashes.add(article_hash)
            seen_titles.add(article['title'])
            unique_articles.append(article)
    
    return unique_articles

def rank_articles(articles: List[Dict], limit: int = 10) -> List[Dict]:
    """
    Rank articles by relevance and importance
    
    Args:
        articles: List of article dictionaries
        limit: Maximum number of articles to return
    
    Returns:
        Top ranked articles
    """
    def calculate_score(article: Dict) -> float:
        score = 0.0
        
        # Source weight (40% of score)
        score += article.get('source_weight', 5) * 0.4
        
        # Recency bonus (30% of score)
        if article.get('published'):
            hours_old = (datetime.now() - article['published']).total_seconds() / 3600
            recency_score = max(0, 5 - (hours_old / 12))  # Decay over 2.5 days
            score += recency_score * 0.3
        
        # Title keywords bonus (20% of score)
        title_lower = article['title'].lower()
        high_value_keywords = ['breakthrough', 'launch', 'release', 'announce', 'new', 'first']
        keyword_score = sum(2 for kw in high_value_keywords if kw in title_lower)
        score += min(keyword_score, 5) * 0.2
        
        # Length bonus (10% of score) - prefer substantial articles
        summary_length = len(article.get('summary', ''))
        length_score = min(summary_length / 50, 5)  # Max 5 points
        score += length_score * 0.1
        
        return score
    
    # Calculate scores and sort
    for article in articles:
        article['score'] = calculate_score(article)
    
    # Sort by score (descending) and return top articles
    ranked_articles = sorted(articles, key=lambda x: x['score'], reverse=True)
    return ranked_articles[:limit]

def fetch_all_news(sources: List[Dict]) -> List[Dict]:
    """
    Fetch news from all configured RSS sources
    
    Args:
        sources: List of source dictionaries
    
    Returns:
        Combined list of all articles
    """
    all_articles = []
    
    for source in sources:
        print(f"📡 Fetching from {source['name']}...")
        articles = fetch_rss_feed(source)
        print(f"   Found {len(articles)} relevant articles")
        all_articles.extend(articles)
    
    return all_articles
