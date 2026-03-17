from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
import os

class DataExtractor:
    def __init__(self, headless=True):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--window-size=1920,1080")

        self.driver = webdriver.Chrome(options=chrome_options)
        
        if not headless:
            self.driver.maximize_window()

        self.wait = WebDriverWait(self.driver, 20)

    # Context Manager methods for safe resource teardown
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print('Closing browser safely...')
        self.driver.quit()

    def _get_num(self, text):
        '''
        Helper function to extract digits
        '''
        match = re.search(r'\d+', text.replace(',','').replace('.',''))
        return int(match.group()) if match else 0

    def _get_position(self, soup):
        '''
        Helper function to extract job title
        FIXME: Needs more robust solution for nested role detection 
        '''
        main_selector = 'section:has(#experience) li' 
        main_container = soup.select_one(main_selector)

        if not main_container:
            return None
        
        # Check for multiple (nested) roles
        # If a <ul> exists without a job description, it's inferred as a nested role
        is_nested = False
        sub_components = main_container.select_one('div[class*="sub-components"]')
        if sub_components:
            nested_ul = sub_components.select_one('ul')
            if nested_ul and len(nested_ul.select('li')) > 0:
                is_nested = True
        
        if is_nested:
            # Nested Role
            print('Detected Nested Role!')
            target_span = sub_components.select_one('ul > li span[aria-hidden="true"]')
            return target_span.get_text(strip=True) if target_span else None
        else:
            # Single Role
            target_span = main_container.select_one('span[aria-hidden="true"]')
            return target_span.get_text(strip=True) if target_span else None

    def scrape_post(self, post_url):
        '''
        Scrape the static HTML of the post
        '''
        
        # Access the page
        print("Navigating to URL...")
        self.driver.get(post_url)

        # Manual Login
        print("\n--- ACTION REQUIRED ---")
        print("Please log in manually in the opened browser window.")
        print("Once the post is fully visible, press ENTER in this terminal to continue...")
        input()

        # Ensure the browser is at the target page
        print("Re-navigating to the target post after login...")
        
        self.driver.get(post_url)

        try:
            # Wait for the main post container to ensure content is loaded
            print("Waiting for post content to load...")
            post_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='feed-shared-update'], div[data-urn]")))

            # Scroll a bit to trigger lazy loading
            self.driver.execute_script("arguments[0].scrollIntoView();", post_element)

            # Retrieve static HTML source
            page_source = self.driver.page_source
            print("HTML retrieved successfully.")

            data_post, data_comments = self._parse_post(page_source)
            time.sleep(random.randint(2,5))
            return data_post, data_comments

        except Exception as e:
            print(f'Failed retrieving HTML. Error code: {e}')
            raise e
    
    def _parse_post(self, page_source):
        '''
        Parse the post and return the extracted dictionaries
        '''
        soup = BeautifulSoup(page_source, 'html.parser')

        data_post = {}
        data_comments = []

        # 1. Inspect the post section
        # 1.1. Extract Post Text
        text_div = soup.find('div', class_='update-components-text')
        data_post['post_text'] = text_div.get_text(separator='\n', strip=True) if text_div else None

        # 1.2. Extract Author/Company Name
        author_span = soup.select_one('span[class=actor__title] span[aria-hidden="true"]')
        data_post['post_author'] = author_span.get_text(strip=True) if author_span else None

        # 1.4. Extract Likes, Comments, and Reposts Stats
        stat_lists = soup.find_all('li', class_=re.compile(r'social-details-social-counts'))

        if len(stat_lists) >= 1:
            data_post['post_likes'] = self._get_num(stat_lists[0].get_text(strip=True))

        if len(stat_lists) >= 2:
            data_post['post_comments'] = self._get_num(stat_lists[1].get_text(strip=True))

        if len(stat_lists) >= 3:
            data_post['post_reposts'] = self._get_num(stat_lists[2].get_text(strip=True))

        # 2. Inspect the comment section
        # Find all comment containers. 
        comments = soup.select('article')
        print(f"Found {len(comments)} visible comments.")

        # Iterate through each comment
        for comment in comments:
            comment_data = {}
            
            # 2.1 Extract Comment Text
            comment_text_span = comment.select_one('[class*="comment-item"][class*="main-content"]')
            comment_data['text'] = comment_text_span.get_text(strip=True) if comment_text_span else None

            # 2.2 Extract Comment Likes
            like_btn = comment.select_one('button[class*="reactions-count"]')
            comment_data['likes'] = self._get_num(like_btn.get_text(strip=True)) if like_btn else 0

            # 2.3 Extract Commenter Name
            name_span = comment.select_one('span[class*="description"][class*="meta"]')
            comment_data['commenter_name'] = name_span.get_text(strip=True) if name_span else None

            # 2.4 Extract Commenter LinkedIn URL
            link_a = comment.select_one('a[class*="comment"][class*="meta"]')
            link = link_a['href'] if link_a else None
            comment_data['commenter_url'] = link

            # 2.5 Distinguish between company and individual accounts
            if link:
                if re.search(r'^(https://www\.linkedin\.com)?/company/', link):
                    comment_data['account_type'] = "Company"
                else:
                    comment_data['account_type'] = "Individual"

            # Only append if we found at least some text or an author
            if comment_data['text'] or comment_data['commenter_name']:
                data_comments.append(comment_data)

        return data_post, data_comments

    def scrape_profiles(self, data_comments):
        '''
        Scrape commenter profiles
        '''
        if not data_comments:
            print('No comments extracted. Skipping profile scraping.')
            return []
        
        p_details_list = []

        # Deduplicate URLs while preserving account type
        profiles_to_scrape = {
            c['commenter_url']: c['account_type'] 
            for c in data_comments 
            if c.get('commenter_url') and c.get('account_type')
        }

        # Iterate through profiles
        for i, (url, account_type) in enumerate(profiles_to_scrape.items()):
            print(f"[{i+1}/{len(profiles_to_scrape)}] Visiting [{account_type}]: {url}")
            
            # Access the profile page
            try:
                self.driver.get(url)

                if account_type == 'Company':
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "section[class*='org-top-card'], .org-top-card")))
                else:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".pv-top-card, [class*='profile-top-card'], main > section:first-of-type")))
                
                time.sleep(random.randint(2,5))
                
                # Parse the profile page
                try:
                    p_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                    p_details = {'commenter_url' : url}

                    # 1. Company Profiles
                    if account_type == 'Company':
                        # 1.1 Industry
                        indust_div = p_soup.select('div[class*="summary-info"][class*="item"]')[0]
                        p_details['industry'] = indust_div.get_text(strip=True) if indust_div else None
                        
                        # 1.2. Location
                        loc_div = p_soup.select('div[class*="summary-info"][class*="item"]')[1]
                        p_details['location'] = loc_div.get_text().split(',')[-1].strip() if loc_div else None

                        # 1.3. Followers
                        followers_p = p_soup.select_one('section[class*="company-info"] p')
                        p_details['followers'] = self._get_num(followers_p.get_text(strip=True)) if followers_p else None
                            
                        # 1.4. Size
                        size_span = p_soup.select_one('a[class*="summary-info"][class*="item"]')
                        p_details['size'] = size_span.get_text(strip=True).split()[0] if size_span else None

                    # 2. Personal Profiles
                    else:
                        # 2.1. Occupation
                        occupation_btn = p_soup.select_one('button[class*="text-align-left"]:nth-of-type(1)')
                        p_details['occupation'] = occupation_btn.get_text(strip=True) if occupation_btn else None
                        
                        # 2.2. Followers
                        followers_span = p_soup.select_one('#content_collections + div p span[aria-hidden="true"]')
                        p_details['followers'] = self._get_num(followers_span.get_text(strip=True)) if followers_span else None

                        # 2.3. Location
                        location_selector = 'ul:has(button[class*="text-align-left"]) + div span:nth-of-type(1)'
                        location_span = p_soup.select_one(location_selector)
                        p_details['location'] = location_span.get_text().split(',')[-1].strip() if location_span else None

                        # 2.4. Posiiton
                        p_details['position'] = self._get_position(p_soup)

                    p_details_list.append(p_details)

                except Exception as e:
                    print(f"Error when parsing profile {url} \n Error code: {e}")
                    p_details_list.append(p_details)

            except Exception as e:
                print(f"Failed to access profile {url} \n Error code: {e}")
                
            time.sleep(random.randint(2,5))

        return p_details_list

    def save_data(self, data_post, data_comments, p_details_list, output_dir='data'):
        '''
        Save extracted data as csv                  
        '''
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        df_post = pd.DataFrame([data_post])
        df_comments = pd.DataFrame(data_comments)
        df_p_details = pd.DataFrame(p_details_list)

        if not df_comments.empty and not df_p_details.empty:
            df_comments_with_details = pd.merge(df_comments, df_p_details, on='commenter_url', how='left')
        else:
            df_comments_with_details = df_comments

        post_data_path = os.path.join(output_dir, 'post_data.csv')
        comments_data_path = os.path.join(output_dir, 'comments_data.csv')

        df_post.to_csv(post_data_path, index=False, encoding='utf-8-sig')
        df_comments_with_details.to_csv(comments_data_path, index=False, encoding='utf-8-sig')
        
        print(f"Data saved to {output_dir}/")

# ================= Testing =================
if __name__ == "__main__":
    post_url = 'https://www.linkedin.com/posts/klarna_klarnas-climate-resilience-program-activity-7346877091532959746-748v/'
    
    with DataExtractor(headless=False) as extractor:
        post_data, comments_data = extractor.scrape_post(post_url)
        profiles_data = extractor.scrape_profiles(comments_data)
        extractor.save_data(post_data, comments_data, profiles_data)