import requests
from bs4 import BeautifulSoup
import csv
import json
import time
from urllib.parse import urljoin, urlparse
import os

class WebScraper:
    def __init__(self, base_url, delay=1):
        """
        Initialize the web scraper
        
        Args:
            base_url: The starting URL to scrape
            delay: Delay between requests in seconds (be respectful to servers)
        """
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        # Set a user agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.scraped_data = []
        
    def fetch_page(self, url):
        """
        Fetch a web page and return BeautifulSoup object
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object or None if error
        """
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()  # Raise exception for bad status codes
            
            # Add delay to be respectful
            time.sleep(self.delay)
            
            return BeautifulSoup(response.content, 'html.parser')
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_links(self, soup, filter_internal=True):
        """
        Extract all links from a page
        
        Args:
            soup: BeautifulSoup object
            filter_internal: If True, only return links from the same domain
            
        Returns:
            List of URLs
        """
        if not soup:
            return []
        
        links = []
        for link in soup.find_all('a', href=True):
            url = urljoin(self.base_url, link['href'])
            
            # Filter internal links if requested
            if filter_internal:
                if urlparse(url).netloc == urlparse(self.base_url).netloc:
                    links.append(url)
            else:
                links.append(url)
        
        # Remove duplicates
        return list(set(links))
    
    def extract_text(self, soup, tag='p'):
        """
        Extract text from specific HTML tags
        
        Args:
            soup: BeautifulSoup object
            tag: HTML tag to extract (default: 'p' for paragraphs)
            
        Returns:
            List of text content
        """
        if not soup:
            return []
        
        elements = soup.find_all(tag)
        return [elem.get_text(strip=True) for elem in elements if elem.get_text(strip=True)]
    
    def extract_images(self, soup):
        """
        Extract all image URLs from a page
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List of image URLs with alt text
        """
        if not soup:
            return []
        
        images = []
        for img in soup.find_all('img'):
            img_url = img.get('src', '')
            if img_url:
                full_url = urljoin(self.base_url, img_url)
                images.append({
                    'url': full_url,
                    'alt': img.get('alt', 'No alt text')
                })
        
        return images
    
    def extract_metadata(self, soup):
        """
        Extract page metadata (title, description, keywords)
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Dictionary of metadata
        """
        if not soup:
            return {}
        
        metadata = {}
        
        # Extract title
        title = soup.find('title')
        metadata['title'] = title.get_text(strip=True) if title else 'No title'
        
        # Extract meta description
        description = soup.find('meta', attrs={'name': 'description'})
        metadata['description'] = description.get('content', 'No description') if description else 'No description'
        
        # Extract meta keywords
        keywords = soup.find('meta', attrs={'name': 'keywords'})
        metadata['keywords'] = keywords.get('content', 'No keywords') if keywords else 'No keywords'
        
        return metadata
    
    def scrape_custom(self, url, selectors):
        """
        Scrape specific elements using CSS selectors
        
        Args:
            url: URL to scrape
            selectors: Dictionary of {name: css_selector}
            
        Returns:
            Dictionary of scraped data
        """
        soup = self.fetch_page(url)
        if not soup:
            return {}
        
        data = {'url': url}
        
        for name, selector in selectors.items():
            elements = soup.select(selector)
            data[name] = [elem.get_text(strip=True) for elem in elements]
        
        return data
    
    def scrape_table(self, url, table_index=0):
        """
        Scrape HTML table from a page
        
        Args:
            url: URL to scrape
            table_index: Index of table to scrape (default: first table)
            
        Returns:
            List of dictionaries representing table rows
        """
        soup = self.fetch_page(url)
        if not soup:
            return []
        
        tables = soup.find_all('table')
        if not tables or table_index >= len(tables):
            print("Table not found")
            return []
        
        table = tables[table_index]
        headers = []
        rows = []
        
        # Extract headers
        header_row = table.find('tr')
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
        
        # Extract data rows
        for row in table.find_all('tr')[1:]:  # Skip header row
            cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
            if cells:
                if headers:
                    rows.append(dict(zip(headers, cells)))
                else:
                    rows.append({'data': cells})
        
        return rows
    
    def save_to_csv(self, data, filename='scraped_data.csv'):
        """
        Save scraped data to CSV file
        
        Args:
            data: List of dictionaries
            filename: Output filename
        """
        if not data:
            print("No data to save")
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            print(f"Data saved to {filename}")
        except Exception as e:
            print(f"Error saving to CSV: {e}")
    
    def save_to_json(self, data, filename='scraped_data.json'):
        """
        Save scraped data to JSON file
        
        Args:
            data: Data to save (list or dict)
            filename: Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Data saved to {filename}")
        except Exception as e:
            print(f"Error saving to JSON: {e}")
    
    def scrape_multiple_pages(self, urls, extract_func):
        """
        Scrape multiple pages using a custom extraction function
        
        Args:
            urls: List of URLs to scrape
            extract_func: Function that takes soup object and returns data
            
        Returns:
            List of scraped data from all pages
        """
        all_data = []
        
        for url in urls:
            soup = self.fetch_page(url)
            if soup:
                data = extract_func(soup)
                data['url'] = url
                all_data.append(data)
        
        return all_data


# Example usage functions
def example_basic_scraping():
    """Example: Basic page scraping"""
    print("\n=== Example 1: Basic Page Scraping ===")
    
    scraper = WebScraper("https://example.com")
    soup = scraper.fetch_page("https://example.com")
    
    if soup:
        # Extract metadata
        metadata = scraper.extract_metadata(soup)
        print(f"Title: {metadata['title']}")
        
        # Extract all paragraphs
        paragraphs = scraper.extract_text(soup, 'p')
        print(f"Found {len(paragraphs)} paragraphs")
        
        # Extract all links
        links = scraper.extract_links(soup)
        print(f"Found {len(links)} internal links")


def example_table_scraping():
    """Example: Scrape HTML table"""
    print("\n=== Example 2: Table Scraping ===")
    
    # Example URL with tables (replace with actual URL)
    scraper = WebScraper("https://example.com")
    table_data = scraper.scrape_table("https://example.com/table-page")
    
    if table_data:
        print(f"Scraped {len(table_data)} rows from table")
        scraper.save_to_csv(table_data, 'table_data.csv')


def example_custom_scraping():
    """Example: Custom CSS selector scraping"""
    print("\n=== Example 3: Custom Selector Scraping ===")
    
    scraper = WebScraper("https://example.com")
    
    # Define CSS selectors for specific elements
    selectors = {
        'headings': 'h1, h2',
        'articles': 'article',
        'prices': '.price'
    }
    
    data = scraper.scrape_custom("https://example.com", selectors)
    scraper.save_to_json(data, 'custom_data.json')


def example_multi_page_scraping():
    """Example: Scrape multiple pages"""
    print("\n=== Example 4: Multi-Page Scraping ===")
    
    scraper = WebScraper("https://example.com", delay=2)
    
    urls = [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3"
    ]
    
    # Custom extraction function
    def extract_data(soup):
        return {
            'title': scraper.extract_metadata(soup)['title'],
            'paragraphs': len(scraper.extract_text(soup, 'p')),
            'images': len(scraper.extract_images(soup))
        }
    
    results = scraper.scrape_multiple_pages(urls, extract_data)
    scraper.save_to_json(results, 'multi_page_data.json')


if __name__ == "__main__":
    print("Web Scraper - Intermediate Level")
    print("=" * 50)
    print("\nThis scraper includes:")
    print("- HTML parsing with BeautifulSoup")
    print("- Multiple data extraction methods")
    print("- CSV and JSON export")
    print("- Rate limiting and error handling")
    print("- Custom CSS selector support")
    print("\nUncomment example functions to test!")
    
    # Uncomment the examples you want to run:
    # example_basic_scraping()
    # example_table_scraping()
    # example_custom_scraping()
    # example_multi_page_scraping()
