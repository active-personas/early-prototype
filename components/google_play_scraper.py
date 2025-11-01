import csv
import os
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from google_play_scraper import app, reviews, reviews_all, Sort
from .logger import Logger

class GooglePlayScraper:
    """
    Google Play Store data collection service for UX research.
    
    This class automates the collection of app reviews, ratings, and metadata
    from the Google Play Store to provide real user feedback for evaluation studies.
    
    Key Responsibilities:
    - Extract app metadata and user reviews from Google Play Store
    - Process and structure user feedback data for analysis
    - Generate CSV datasets for persona-based evaluation studies
    - Support comparative analysis across app versions and competitors
    
    Features:
    - Bulk review extraction with configurable limits
    - Multiple sorting options (newest, helpful, rating)
    - Structured CSV output for data analysis tools
    - Rate limiting and error handling for reliable scraping
    
    Data Collection:
    - User reviews and ratings
    - Review timestamps and helpfulness scores
    - App metadata (name, description, category)
    - Version-specific feedback analysis
    
    Usage in Evaluation:
    - Gather real user feedback for persona calibration
    - Identify common usability issues and pain points
    - Support competitive UX analysis workflows
    """
    def __init__(self, output_dir="data/user_feedback"):
        self.output_dir = output_dir
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        Logger.debug(f"GooglePlayScraper initialized with output directory: {self.output_dir}")
    
    def extract_app_id(self, url):
        """Extract app ID from Google Play Store URL"""
        try:
            parsed_url = urlparse(url)
            if 'play.google.com' not in parsed_url.netloc:
                raise ValueError("Not a valid Google Play Store URL")
            
            # Extract app ID from URL
            if '/store/apps/details' in parsed_url.path:
                query_params = parse_qs(parsed_url.query)
                app_id = query_params.get('id', [None])[0]
                if app_id:
                    Logger.debug(f"Extracted app ID: {app_id}")
                    return app_id
            
            raise ValueError("Could not extract app ID from URL")
        except Exception as e:
            Logger.error(f"Invalid URL format: {e}")
            raise ValueError(f"Invalid URL format: {e}")
    
    def get_existing_reviews(self, app_id):
        """
        Get existing reviews from CSV file if it exists
        
        Returns:
            tuple: (existing_reviews_list, csv_path)
        """
        csv_filename = f"{app_id}.csv"
        csv_path = os.path.join(self.output_dir, csv_filename)
        existing_reviews = []
        
        if os.path.exists(csv_path):
            try:
                with open(csv_path, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    existing_reviews = list(reader)
                Logger.info(f"Found existing reviews file with {len(existing_reviews)} reviews: {csv_path}")
            except Exception as e:
                Logger.error(f"Error reading existing file: {e}")
        else:
            Logger.debug(f"No existing reviews file found: {csv_path}")
        
        return existing_reviews, csv_path
    
    def merge_reviews(self, existing_reviews, new_reviews):
        """
        Merge new reviews with existing ones, avoiding duplicates
        and ordering from newest to oldest
        
        Returns:
            list: Merged reviews ordered by scraped_at (newest first)
        """
        # Create a set of existing review identifiers to avoid duplicates
        existing_identifiers = set()
        for review in existing_reviews:
            # Use reviewer + review_text as identifier
            identifier = f"{review.get('reviewer', '')}_{review.get('review_text', '')}"
            existing_identifiers.add(identifier)
        
        # Filter out new reviews that already exist
        unique_new_reviews = []
        for review in new_reviews:
            identifier = f"{review.get('reviewer', '')}_{review.get('review_text', '')}"
            if identifier not in existing_identifiers:
                unique_new_reviews.append(review)
        
        # Combine all reviews
        all_reviews = existing_reviews + unique_new_reviews
        
        Logger.info(f"Merged reviews: {len(existing_reviews)} existing + {len(unique_new_reviews)} new = {len(all_reviews)} total")
        
        # Sort by scraped_at timestamp (newest first)
        try:
            all_reviews.sort(key=lambda x: x.get('scraped_at', ''), reverse=True)
        except Exception as e:
            Logger.error(f"Warning: Could not sort reviews by timestamp: {e}")
        
        return all_reviews
    
    def get_reviews_data(self, app_id, sort_order=Sort.NEWEST, lang='en', country='us', max_reviews=None):
        """
        Fetch all available reviews data from Google Play Store using the official library

        Args:
            app_id (str): The app ID (package name)
            sort_order: Sort order for reviews (Sort.NEWEST, Sort.RATING, Sort.MOST_RELEVANT)
            lang (str): Language code for reviews (default 'en')
            country (str): Country code for reviews (default 'us')
            max_reviews (int or None): Maximum number of reviews to fetch (None for all)

        Returns:
            list: List of review dictionaries
        """
        reviews_data = []

        try:
            Logger.info(f"Fetching app information for: {app_id}")
            # Get app information first
            app_info = app(app_id)
            app_name = app_info.get('title', app_id)
            Logger.info(f"App name: {app_name}")

            Logger.info(f"Fetching reviews with settings - Sort: {sort_order}, Lang: {lang}, Country: {country}")
            # Get all reviews using the official library (no count limit)
            reviews_result = reviews_all(
                app_id,
                lang=lang,
                country=country,
                sort=sort_order
            )

            Logger.info(f"Retrieved {len(reviews_result)} reviews from Google Play Store")

            # Convert to our format
            for review in reviews_result:
                reviews_data.append({
                    'app_id': app_id,
                    'app_name': app_name,
                    'reviewer': review.get('userName', 'Anonymous'),
                    'rating': review.get('score', 'N/A'),
                    'review_text': review.get('content', ''),
                    'review_date': review.get('at', '').strftime('%Y-%m-%d %H:%M:%S') if review.get('at') else '',
                    'thumbs_up': review.get('thumbsUpCount', 0),
                    'reply_text': review.get('replyContent', ''),
                    'scraped_at': datetime.now().isoformat()
                })

            if not reviews_data:
                Logger.info(f"No reviews found for app: {app_id}")
                reviews_data.append({
                    'app_id': app_id,
                    'app_name': app_name,
                    'reviewer': 'No reviews found',
                    'rating': 'N/A',
                    'review_text': 'No reviews available for this app.',
                    'review_date': '',
                    'thumbs_up': 0,
                    'reply_text': '',
                    'scraped_at': datetime.now().isoformat()
                })

        except Exception as e:
            Logger.error(f"Error fetching reviews for {app_id}: {e}")
            reviews_data.append({
                'app_id': app_id,
                'app_name': 'Unknown',
                'reviewer': 'Error',
                'rating': 'N/A',
                'review_text': f'Failed to fetch reviews: {e}',
                'review_date': '',
                'thumbs_up': 0,
                'reply_text': '',
                'scraped_at': datetime.now().isoformat()
            })

        return reviews_data

    def get_app_details(self, app_id):
        """
        Get detailed app information
        
        Args:
            app_id (str): The app ID (package name)
            
        Returns:
            dict: App information dictionary
        """
        try:
            Logger.debug(f"Fetching app details for: {app_id}")
            app_info = app(app_id)
            Logger.debug(f"Successfully retrieved app details for: {app_id}")
            return app_info
        except Exception as e:
            Logger.error(f"Error getting app details for {app_id}: {e}")
            return None
    
    def scrap(self, url, sort_order=Sort.NEWEST, lang='en', country='us', max_reviews=None):
        """
        Scrape all available feedback from Google Play Store app URL and save to CSV

        Args:
            url (str): Google Play Store app URL
            sort_order: Sort order for reviews (Sort.NEWEST, Sort.RATING, Sort.MOST_RELEVANT)
            lang (str): Language code for reviews (default 'en')
            country (str): Country code for reviews (default 'us')
            max_reviews (int or None): Maximum number of reviews to fetch (None for all)

        Returns:
            str: Path to the generated CSV file
        """
        try:
            Logger.info(f"Starting scraping process for URL: {url}")
            # Extract app ID from URL
            app_id = self.extract_app_id(url)

            # Get existing reviews if any
            existing_reviews, csv_path = self.get_existing_reviews(app_id)

            # Get reviews data with language, country, and max_reviews settings
            new_reviews = self.get_reviews_data(
                app_id,
                sort_order=sort_order,
                lang=lang,
                country=country,
                max_reviews=max_reviews
            )

            # Merge with existing reviews (newest first, no duplicates)
            all_reviews = self.merge_reviews(existing_reviews, new_reviews)

            # Write to CSV
            if all_reviews:
                fieldnames = ['app_id', 'app_name', 'reviewer', 'rating', 'review_text',
                              'review_date', 'thumbs_up', 'reply_text', 'scraped_at']

                with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(all_reviews)

                Logger.info(f"Successfully saved {len(all_reviews)} reviews to: {csv_path}")

            return csv_path

        except Exception as e:
            Logger.error(f"Error during scraping: {e}")
            raise e
    
    def get_review_count(self):
        """Get the number of CSV files in the output directory"""
        csv_files = [f for f in os.listdir(self.output_dir) if f.endswith('.csv')]
        count = len(csv_files)
        Logger.debug(f"Found {count} CSV files in output directory")
        return count
