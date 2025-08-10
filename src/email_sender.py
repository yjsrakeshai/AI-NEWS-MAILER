#!/usr/bin/env python3
"""
Email Sender Module
Handles Gmail SMTP email sending functionality
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from typing import List, Dict
import pytz

def generate_html_email(articles: List[Dict]) -> str:
    """
    Generate HTML email content from articles
    
    Args:
        articles: List of article dictionaries
    
    Returns:
        HTML email content as string
    """
    
    # Get current IST date
    ist = pytz.timezone('Asia/Kolkata')
    current_date = datetime.now(ist).strftime('%B %d, %Y')
    
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily AI Insights</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            background-color: #f8f9fa;
        }}
        
        .container {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 700;
        }}
        
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 16px;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .summary {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 30px;
            border-left: 4px solid #667eea;
        }}
        
        .article {{
            border: 1px solid #e9ecef;
            border-radius: 8px;
            margin: 20px 0;
            padding: 20px;
            background: white;
            transition: box-shadow 0.2s ease;
        }}
        
        .article:hover {{
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .rank {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 50%;
            width: 32px;
            height: 32px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            font-weight: bold;
            font-size: 14px;
            float: left;
        }}
        
        .article-content {{
            margin-left: 50px;
        }}
        
        .article h3 {{
            margin: 0 0 10px 0;
            color: #2c3e50;
        }}
        
        .article h3 a {{
            color: #2c3e50;
            text-decoration: none;
        }}
        
        .article h3 a:hover {{
            color: #667eea;
            text-decoration: underline;
        }}
        
        .article p {{
            margin: 10px 0;
            color: #6c757d;
        }}
        
        .source {{
            color: #868e96;
            font-size: 12px;
            margin-top: 10px;
            font-weight: 500;
        }}
        
        .source::before {{
            content: "📰 ";
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            color: #6c757d;
            font-size: 14px;
            border-top: 1px solid #e9ecef;
        }}
        
        .footer a {{
            color: #667eea;
            text-decoration: none;
        }}
        
        .clearfix {{
            clear: both;
        }}
        
        @media (max-width: 600px) {{
            .header {{
                padding: 20px;
            }}
            .header h1 {{
                font-size: 24px;
            }}
            .content {{
                padding: 20px;
            }}
            .article {{
                padding: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Daily AI Insights</h1>
            <p>{current_date} | Top {len(articles)} AI Advancements</p>
        </div>
        
        <div class="content">
            <div class="summary">
                <strong>Today's AI Landscape:</strong> 
                {"Latest breakthroughs in artificial intelligence, machine learning innovations, and industry developments from trusted sources worldwide." if articles else "No significant AI developments found today. Check back tomorrow for the latest updates."}
            </div>
    """
    
    # Add articles
    for i, article in enumerate(articles, 1):
        article_html = f"""
            <div class="article">
                <div class="rank">{i}</div>
                <div class="article-content">
                    <h3><a href="{article['link']}" target="_blank">{article['title']}</a></h3>
                    <p>{article['summary']}</p>
                    <div class="source">
                        {article['source']} 
                        {f"• {article['published_str']}" if article.get('published_str') else ""}
                    </div>
                </div>
                <div class="clearfix"></div>
            </div>
        """
        html_template += article_html
    
    # Close HTML
    html_template += f"""
        </div>
        
        <div class="footer">
            <p>
                🚀 Powered by AI News Aggregator | 
                <a href="mailto:{os.environ.get('GMAIL_USER', 'your-email@gmail.com')}">Send Feedback</a>
            </p>
            <p style="margin-top: 10px; font-size: 12px;">
                This digest is generated automatically from RSS feeds of trusted AI news sources.
            </p>
        </div>
    </div>
</body>
</html>
    """
    
    return html_template

def generate_plain_text_email(articles: List[Dict]) -> str:
    """
    Generate plain text version of email
    
    Args:
        articles: List of article dictionaries
    
    Returns:
        Plain text email content
    """
    ist = pytz.timezone('Asia/Kolkata')
    current_date = datetime.now(ist).strftime('%B %d, %Y')
    
    text_content = f"""
🤖 DAILY AI INSIGHTS - {current_date}
{"=" * 50}

Today's Top {len(articles)} AI Developments:

"""
    
    for i, article in enumerate(articles, 1):
        text_content += f"""
{i}. {article['title']}

   {article['summary']}
   
   Source: {article['source']}
   Link: {article['link']}
   {"Published: " + article['published_str'] if article.get('published_str') else ""}

{"─" * 50}
"""
    
    text_content += f"""

🚀 Powered by AI News Aggregator
📧 Send feedback: {os.environ.get('GMAIL_USER', 'your-email@gmail.com')}

This digest is generated automatically from RSS feeds of trusted AI news sources.
"""
    
    return text_content

def send_daily_digest(articles: List[Dict], recipients: List[str]) -> bool:
    """
    Send daily AI digest via Gmail SMTP
    
    Args:
        articles: List of article dictionaries
        recipients: List of recipient email addresses
    
    Returns:
        True if email sent successfully, False otherwise
    """
    
    # Check for required environment variables
    gmail_user = os.environ.get('GMAIL_USER')
    gmail_pass = os.environ.get('GMAIL_PASS')
    
    if not gmail_user or not gmail_pass:
        print("❌ Gmail credentials not found in environment variables")
        return False
    
    try:
        # Get current IST date for subject
        ist = pytz.timezone('Asia/Kolkata')
        current_date = datetime.now(ist).strftime('%B %d, %Y')
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🤖 Daily AI Insights - {current_date}"
        msg['From'] = f"AI News Digest <{gmail_user}>"
        msg['Reply-To'] = gmail_user
        
        # Generate email content
        html_content = generate_html_email(articles)
        text_content = generate_plain_text_email(articles)
        
        # Create message parts
        text_part = MIMEText(text_content, 'plain', 'utf-8')
        html_part = MIMEText(html_content, 'html', 'utf-8')
        
        # Attach parts
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Setup Gmail SMTP
        print("📧 Connecting to Gmail SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Enable encryption
        server.login(gmail_user, gmail_pass)
        
        # Send to each recipient
        successful_sends = 0
        for recipient in recipients:
            try:
                msg['To'] = recipient
                text = msg.as_string()
                server.sendmail(gmail_user, recipient, text)
                print(f"✅ Email sent to {recipient}")
                successful_sends += 1
                
                # Remove To header for next recipient
                del msg['To']
                
            except Exception as e:
                print(f"❌ Failed to send to {recipient}: {str(e)}")
        
        server.quit()
        
        print(f"📊 Successfully sent to {successful_sends}/{len(recipients)} recipients")
        return successful_sends > 0
        
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        return False

def test_email_connection() -> bool:
    """
    Test Gmail SMTP connection
    
    Returns:
        True if connection successful
    """
    gmail_user = os.environ.get('GMAIL_USER')
    gmail_pass = os.environ.get('GMAIL_PASS')
    
    if not gmail_user or not gmail_pass:
        print("❌ Gmail credentials not found")
        return False
    
    try:
        print("🔍 Testing Gmail SMTP connection...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, gmail_pass)
        server.quit()
        print("✅ Gmail SMTP connection successful")
        return True
    
    except Exception as e:
        print(f"❌ Gmail SMTP connection failed: {str(e)}")
        return False
