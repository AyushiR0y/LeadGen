import time
import logging
from typing import List, Dict, Optional
import random
from datetime import datetime, timedelta
import pandas as pd
from playwright.sync_api import sync_playwright

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_mock_events(location: str) -> List[Dict]:
    """Generate mock events as fallback."""
    events = []
    titles = ["Cultural Festival", "Music Night", "Art Exhibition", "Food Carnival", "Traditional Dance"]
    
    for i in range(5):
        date = datetime.now() + timedelta(days=random.randint(1, 30))
        events.append({
            "name": f"{location} {titles[i]}",
            "date": date.strftime("%d %b %Y"),
            "location": location,
            "description": f"A wonderful {titles[i].lower()} happening in {location}. Come and enjoy!",
            "url": "https://utsav.gov.in",
            "image": "https://utsav.gov.in/public/images/landing-logo2.png.png",
            "categories": ["Art & Culture", "Music"],
            "source": "Mock Data"
        })
    return events

def get_area_events(location: str, start_date: str = "", end_date: str = "") -> List[Dict]:
    """
    Scrapes events from utsav.gov.in using Playwright.
    Falls back to mock data if scraping fails.
    
    Args:
        location (str): Location to search for.
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.
        
    Returns:
        List[Dict]: List of event dictionaries.
    """
    events = []
    
    try:
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=True)
            # Create a new context with user agent to look more like a real browser
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            page = context.new_page()
            
            logger.info("Navigating to utsav.gov.in/all-events")
            response = page.goto("https://utsav.gov.in/all-events", timeout=60000)
            
            if response.status != 200:
                logger.warning(f"Page returned status {response.status}")
            
            # Handle Location Filter
            if location:
                logger.info(f"Filtering by location: {location}")
                # Wait for input to be available
                page.wait_for_selector("input[name='location']")
                page.fill("input[name='location']", location)
            
            # Handle Date Filter
            if start_date:
                logger.info(f"Setting start date: {start_date}")
                page.evaluate(f"document.getElementById('startdate').value = '{start_date}'")
                
            if end_date:
                logger.info(f"Setting end date: {end_date}")
                page.evaluate(f"document.getElementById('enddate').value = '{end_date}'")
            
            # Click Search
            logger.info("Clicking search")
            page.click("#filter_search_btn")
            
            # Wait for results
            logger.info("Waiting for results...")
            try:
                # The loader has id "whole_page_loader". Wait for it to be hidden.
                # Sometimes it might not appear if response is too fast, so catching timeout is fine.
                page.wait_for_selector("#whole_page_loader", state="hidden", timeout=10000)
                
                # Give a little extra time for rendering
                time.sleep(2)
                
            except Exception as e:
                logger.warning(f"Wait for loader failed (might be fast load): {e}")
            
            # Extract events
            # We use .cardarea selector which wraps each event card
            event_cards = page.query_selector_all(".cardarea")
            logger.info(f"Found {len(event_cards)} event cards")
            
            for card in event_cards:
                try:
                    title_elem = card.query_selector(".eventtitle a")
                    title = title_elem.inner_text().strip() if title_elem else "N/A"
                    link = title_elem.get_attribute("href") if title_elem else "N/A"
                    
                    img_elem = card.query_selector(".imgcontainer img")
                    image_url = img_elem.get_attribute("src") if img_elem else None
                    
                    desc_elem = card.query_selector(".cardcontent p")
                    description = desc_elem.inner_text().strip() if desc_elem else ""
                    
                    date_elem = card.query_selector(".cardbottom .event-date + span")
                    date = date_elem.inner_text().strip() if date_elem else "N/A"
                    
                    category_elems = card.query_selector_all(".category_inline ul li a")
                    categories = [cat.inner_text().strip() for cat in category_elems]
                    
                    # Basic validation to ensure we have a real event
                    if title == "N/A" or not link:
                        continue

                    events.append({
                        "name": title,
                        "date": date,
                        "location": location if location else "India",
                        "description": description,
                        "url": link,
                        "image": image_url,
                        "categories": categories,
                        "source": "utsav.gov.in"
                    })
                except Exception as e:
                    logger.error(f"Error extracting event card: {e}")
            
            browser.close()
            
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        # Continue to return mock data if list is empty
    
    if not events:
        logger.info("No events found or scraping failed, using mock data")
        return get_mock_events(location if location else "India")
        
    return events
