#!/usr/bin/env python3
"""
AI News Daily Mailer - Zero Cost Implementation
Aggregates AI news from RSS feeds and sends daily email digest
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import List, Dict
import pytz

# Add src directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rss_aggregator import fetch_all_news, rank_articles, remove_duplicates
from email_sender import send_daily_digest
from utils import setup_logging, load_config

def main():
    """Main function to orchestrate the daily AI news email"""
    
    # Setup logging
    logger = setup_logging()
    logger.info("Starting AI News Daily Mailer")
    
    try:
        # Set timezone to IST
        ist = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(ist)
        logger.info(f"Current IST time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Load configuration
        config = load_config()
        sources = config.get('sources', [])
        recipients = config.get('recipients', [])
        
        if not recipients:
            logger.error("No recipients configured!")
            return
        
        logger.info(f"Loaded {len(sources)} sources and {len(recipients)} recipients")
        
        # Fetch news from all RSS sources
        logger.info("Fetching news from RSS sources...")
        all_articles = fetch_all_news(sources)
        logger.info(f"Fetched {len(all_articles)} articles total")
        
        if not all_articles:
            logger.warning("No articles found! Check RSS sources.")
            return
        
        # Remove duplicates
        unique_articles = remove_duplicates(all_articles)
        logger.info(f"After deduplication: {len(unique_articles)} unique articles")
        
        # Rank articles and get top 10
        top_articles = rank_articles(unique_articles, limit=10)
        logger.info(f"Selected top {len(top_articles)} articles")
        
        # Log the top articles for debugging
        for i, article in enumerate(top_articles, 1):
            logger.info(f"{i}. {article['title']} - {article['source']}")
        
        # Send email digest
        logger.info("Sending email digest...")
        success = send_daily_digest(top_articles, recipients)
        
        if success:
            logger.info("✅ Daily AI news email sent successfully!")
            print("✅ Email sent successfully!")
        else:
            logger.error("❌ Failed to send email")
            print("❌ Failed to send email")
            
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        print(f"❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
