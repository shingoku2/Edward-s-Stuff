"""
Information Scraper Module
Scrapes gaming wikis, forums, and guides for real-time information
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, List, Any
import json
import re
import time
import logging
from urllib.parse import quote

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GameInfoScraper:
    """Scrapes information about games from various sources"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum 1 second between requests

        # Game wiki mappings
        self.wiki_urls = {
            "League of Legends": "https://leagueoflegends.fandom.com/wiki/",
            "Dota 2": "https://dota2.fandom.com/wiki/",
            "VALORANT": "https://valorant.fandom.com/wiki/",
            "Elden Ring": "https://eldenring.wiki.fextralife.com/",
            "Dark Souls 3": "https://darksouls3.wiki.fextralife.com/",
            "Minecraft": "https://minecraft.fandom.com/wiki/",
            "World of Warcraft": "https://wowpedia.fandom.com/wiki/",
            "Final Fantasy XIV": "https://ffxiv.consolegameswiki.com/wiki/",
            "The Witcher 3": "https://witcher.fandom.com/wiki/",
            "Skyrim Special Edition": "https://elderscrolls.fandom.com/wiki/",
            "Cyberpunk 2077": "https://cyberpunk.fandom.com/wiki/",
        }

    def search_game_info(self, game_name: str, query: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for information about a game

        Args:
            game_name: Name of the game
            query: Specific search query (optional)

        Returns:
            Dictionary with search results
        """
        results = {
            'game': game_name,
            'wiki_info': None,
            'web_results': [],
            'error': None
        }

        try:
            # Try to get wiki information
            wiki_info = self._search_wiki(game_name, query)
            if wiki_info:
                results['wiki_info'] = wiki_info

            # DISABLED: Web scraping can be unreliable and cause crashes
            # If needed, enable this after testing
            # web_results = self._search_web(game_name, query)
            # if web_results:
            #     results['web_results'] = web_results

        except Exception as e:
            logger.error(f"Error in search_game_info: {e}", exc_info=True)
            results['error'] = str(e)

        return results

    def _rate_limit(self):
        """Implement rate limiting to avoid getting banned"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _search_wiki(self, game_name: str, query: Optional[str] = None) -> Optional[Dict]:
        """Search game-specific wiki"""
        try:
            # Rate limiting
            self._rate_limit()

            # Check if we have a known wiki for this game
            wiki_base = self.wiki_urls.get(game_name)

            if not wiki_base:
                # Try generic fandom search
                wiki_base = f"https://{game_name.lower().replace(' ', '')}.fandom.com/wiki/"

            if query:
                # Search for specific topic
                search_url = f"{wiki_base}{quote(query.replace(' ', '_'))}"
            else:
                # Get main page
                search_url = wiki_base

            response = self.session.get(search_url, timeout=5)  # Shorter timeout to prevent hanging

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract main content
                content = self._extract_wiki_content(soup)

                return {
                    'url': search_url,
                    'content': content,
                    'source': 'wiki'
                }

        except requests.exceptions.Timeout:
            logger.warning(f"Wiki search timeout for {game_name}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Wiki search request error: {e}")
        except Exception as e:
            logger.error(f"Wiki search error: {e}", exc_info=True)

        return None

    def _extract_wiki_content(self, soup: BeautifulSoup) -> str:
        """Extract relevant content from wiki page - with extra safety"""
        content_parts = []

        try:
            if not soup:
                return ""

            # Try to find main content area
            main_content = soup.find('div', {'class': ['mw-parser-output', 'page-content', 'content']})

            if main_content:
                # Get first few paragraphs - with safety checks
                try:
                    paragraphs = main_content.find_all('p', limit=5)
                    for p in paragraphs:
                        try:
                            if p:
                                text = p.get_text().strip()
                                if text and len(text) > 50:  # Skip very short paragraphs
                                    content_parts.append(text)
                        except (AttributeError, TypeError) as e:
                            logger.debug(f"Error extracting paragraph: {e}")
                            continue
                except Exception as e:
                    logger.debug(f"Error finding paragraphs: {e}")

                # Get any lists (tips, strategies, etc.) - with safety checks
                try:
                    lists = main_content.find_all(['ul', 'ol'], limit=3)
                    for lst in lists:
                        try:
                            if lst:
                                items = lst.find_all('li', limit=10)
                                list_items = []
                                for item in items:
                                    try:
                                        if item:
                                            text = item.get_text().strip()
                                            if text:
                                                list_items.append(f"• {text}")
                                    except (AttributeError, TypeError):
                                        continue
                                if list_items:
                                    content_parts.append('\n'.join(list_items))
                        except (AttributeError, TypeError) as e:
                            logger.debug(f"Error extracting list: {e}")
                            continue
                except Exception as e:
                    logger.debug(f"Error finding lists: {e}")

        except Exception as e:
            logger.error(f"Content extraction error: {e}", exc_info=True)

        # Safely join content with length limit
        try:
            result = '\n\n'.join(content_parts[:3]) if content_parts else ""
            return result[:2000]  # Limit to 2000 chars
        except Exception as e:
            logger.error(f"Error joining content: {e}")
            return ""

    def _search_web(self, game_name: str, query: Optional[str] = None) -> List[Dict]:
        """
        Search web for game information
        Note: This is a placeholder for web search integration
        In production, you might use Google Custom Search API or similar
        """
        results = []

        # For now, we'll search popular gaming sites directly
        search_query = f"{game_name}"
        if query:
            search_query += f" {query}"

        # Try to scrape from popular gaming resources
        gaming_sites = [
            f"https://www.ign.com/search?q={quote(search_query)}",
            f"https://www.gamespot.com/search/?q={quote(search_query)}",
        ]

        for site_url in gaming_sites[:1]:  # Limit to avoid too many requests
            try:
                # Rate limiting
                self._rate_limit()

                response = self.session.get(site_url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # This is simplified - actual implementation would parse search results
                    results.append({
                        'url': site_url,
                        'source': 'web_search',
                        'snippet': 'Search results available'
                    })

            except requests.exceptions.Timeout:
                logger.warning(f"Web search timeout for {site_url}")
                continue
            except requests.exceptions.RequestException as e:
                logger.warning(f"Web search request error: {e}")
                continue
            except Exception as e:
                logger.error(f"Web search error: {e}", exc_info=True)
                continue

        return results

    def get_game_guide(self, game_name: str, topic: str) -> str:
        """
        Get a specific guide or information about a topic in the game

        Args:
            game_name: Name of the game
            topic: Specific topic (e.g., "beginner guide", "best builds")

        Returns:
            Formatted text with information
        """
        results = self.search_game_info(game_name, topic)

        output = []

        if results.get('wiki_info'):
            wiki = results['wiki_info']
            output.append(f"=== Wiki Information ===")
            output.append(f"Source: {wiki['url']}\n")
            output.append(wiki['content'])

        if results.get('web_results'):
            output.append(f"\n=== Additional Resources ===")
            for result in results['web_results']:
                output.append(f"• {result['url']}")

        if results.get('error'):
            output.append(f"\nNote: {results['error']}")

        return '\n'.join(output) if output else "No information found."

    def get_quick_tips(self, game_name: str) -> str:
        """Get quick tips for a game"""
        return self.get_game_guide(game_name, "tips and tricks")

    def search_character_build(self, game_name: str, character: str) -> str:
        """Search for character build information"""
        return self.get_game_guide(game_name, f"{character} build guide")

    def search_walkthrough(self, game_name: str, quest_or_level: str) -> str:
        """Search for quest or level walkthrough"""
        return self.get_game_guide(game_name, f"{quest_or_level} walkthrough")


class RedditScraper:
    """Scrapes gaming subreddits for community tips"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.last_request_time = 0
        self.min_request_interval = 2.0  # Reddit is more strict

        # Common gaming subreddits
        self.game_subreddits = {
            "League of Legends": "leagueoflegends",
            "Dota 2": "DotA2",
            "VALORANT": "VALORANT",
            "Elden Ring": "Eldenring",
            "Minecraft": "Minecraft",
            "World of Warcraft": "wow",
        }

    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def get_hot_posts(self, game_name: str, limit: int = 5) -> List[Dict]:
        """Get hot posts from game's subreddit"""
        subreddit = self.game_subreddits.get(game_name, game_name.replace(' ', ''))

        try:
            # Rate limiting
            self._rate_limit()

            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                posts = []

                for post in data['data']['children']:
                    post_data = post['data']
                    posts.append({
                        'title': post_data['title'],
                        'url': f"https://reddit.com{post_data['permalink']}",
                        'score': post_data['score'],
                        'comments': post_data['num_comments']
                    })

                return posts
            elif response.status_code == 429:
                logger.warning(f"Reddit rate limit exceeded for r/{subreddit}")
            else:
                logger.warning(f"Reddit returned status code {response.status_code}")

        except requests.exceptions.Timeout:
            logger.warning(f"Reddit request timeout for r/{subreddit}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Reddit request error: {e}")
        except Exception as e:
            logger.error(f"Reddit scraping error: {e}", exc_info=True)

        return []


if __name__ == "__main__":
    # Test the scraper
    scraper = GameInfoScraper()

    print("Testing Game Info Scraper...")
    print("\nSearching for League of Legends tips...")

    results = scraper.get_quick_tips("League of Legends")
    print(results)

    print("\n" + "="*50)
    print("\nTesting Reddit Scraper...")

    reddit = RedditScraper()
    posts = reddit.get_hot_posts("League of Legends")

    if posts:
        print("Hot posts:")
        for post in posts:
            print(f"\n• {post['title']}")
            print(f"  Score: {post['score']} | Comments: {post['comments']}")
    else:
        print("No posts found")
