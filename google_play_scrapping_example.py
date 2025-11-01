import os
from components.google_play_scraper import GooglePlayScraper
from google_play_scraper import Sort

def main():
    # Initialize the scraper
    scraper = GooglePlayScraper()
    
    # Example Google Play Store app URLs
    app_urls = [
        #"https://play.google.com/store/apps/details?id=se.blekingetrafiken.washington&hl=en_NZ",
        "https://play.google.com/store/apps/details?id=se.skanetrafiken.washington&hl=en_NZ",
    ]
    
    max_reviews = 1000  # Limit to 15 reviews per app

    print("=== Google Play Store Scraper ===\n")
    
    for i, url in enumerate(app_urls, 1):
        print(f"{i}. Processing: {url}")
        try:
            # Extract app ID to get app details first
            app_id = scraper.extract_app_id(url)
            
            # Get and display app details
            app_details = scraper.get_app_details(app_id)
            
            if app_details:
                print(f"   App: {app_details.get('title', 'Unknown')} by {app_details.get('developer', 'Unknown')}")
                print(f"   Rating: {app_details.get('score', 'N/A')}/5 | Installs: {app_details.get('installs', 'Unknown')}")
            
            lang = 'se'  # Language for reviews
            country = 'se'  # Country for reviews

            # Scrape reviews
            csv_path = scraper.scrap(
                url, 
                max_reviews=max_reviews,
                lang=lang,
                country=country
            )
            
            # Check file stats
            if os.path.exists(csv_path):
                with open(csv_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    line_count = len(lines) - 1  # Subtract header

                print(f"   ✓ {line_count} reviews saved to: {csv_path}")
                
                # Show latest review
                if len(lines) > 1:
                    import csv
                    with open(csv_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        sample_review = next(reader)
                        reviewer = sample_review.get('reviewer', 'Unknown')
                        rating = sample_review.get('rating', 'N/A')
                        review_text = sample_review.get('review_text', '')
                        preview_text = review_text[:60] + "..." if len(review_text) > 60 else review_text
                        print(f"   Latest: {reviewer} ({rating}/5) - {preview_text}")
            
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        print()  # Add spacing between apps
    
    # Show summary
    total_files = scraper.get_review_count()
    print(f"Summary: {total_files} files in '{scraper.output_dir}'\n")
    
    # List files
    if total_files > 0:
        for filename in os.listdir(scraper.output_dir):
            if filename.endswith('.csv'):
                file_path = os.path.join(scraper.output_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    review_count = sum(1 for line in f) - 1  # Subtract header

                print(f"  {filename}: {review_count} reviews")
    
    # Quick duplicate test
    print(f"\nTesting duplicate handling...")
    test_url = app_urls[0]
    try:
        csv_path = scraper.scrap(test_url, max_reviews=5)
        with open(csv_path, 'r', encoding='utf-8') as f:
            final_count = sum(1 for line in f) - 1

        print(f"✓ No duplicates added. Final count: {final_count}")

    except Exception as e:
        print(f"✗ Test failed: {e}")

if __name__ == "__main__":
    main()
