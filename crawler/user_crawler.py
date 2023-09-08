# Copyright (C) 2023 Xian Chen

import re
import requests
import json
import config
from tqdm import tqdm
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from helper import Helper
from database import MySQLConnector

class User_Detailed_Profiles():
    """
    The User_Detailed_Profiles class visits each user's profile website and scrapes their data.
    Germania has implemented a security function that resets the session, when crawling through those profiles.
    Thus this function demands for INTERACTION.
    It implements a captcha_handler, in which a user input is necessary to pass on valid cookies.
    """
    def __init__(self, start_page: int, helper: Helper, db: MySQLConnector = None):
        """
        Initialize variables important throughout the function

        Args:
            start_page (int): The number at which page we start crawling the userlists
            helper (Helper): The logger
            db (MySQLConnector, optional): Database in which crawled users will be saved. Defaults to None.
        """
        # The logger
        self.log = helper.log
        self.log.info("Detailed user_info crawl: Starting to crawl all users including their profiles.")
        # Keep track of already visited urls
        self.visited = set()
        # The current userlist page to be visisted
        self.current_page = config.CRAWLER_USERLIST_LINKS[start_page]
        # Initialize an empty list to store user information
        self.users = []
        # Status flag that determines the continuation of crawling
        self.status = False
        # The session cookie (okay if not valid, we handle captcha's in this class)
        self.cookies = { 'PHPSESSID': config.CRAWLER_COOKIE }
        # Number of rows already processed, needed for debugging
        self.sum_row = 0

        self.crawled_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # While there's still a page to crawl and the status flag is not set, we crawl the website
        while self.current_page and not self.status:
            self.crawl_profiles()
            
        time_now = datetime.now().strftime("%Y-%m-%d_%H-%M")
        # Save the collected user information to a JSON file
        with open(f"./data/user_detailed_information_{time_now}.json", 'w') as json_file:
            json.dump(self.users, json_file, indent=4)
        self.log.info("User information saved to 'user_detailed_information.json'")
        # If a MySQLConnector Object is given and exists, load collected data into that DB
        if db:
            db.bulk_load_user_detailed(self.users)
    
    def get_profile_details(self, soup):
        """
        This method purely deals with the profiles and returns a dictionary with all scraped data of a profile.
        It contains several sub-methods in which each data-container is scraped for its specific categorized information (like only profile info, trade related info, etc.)

        Args:
            soup (BeautifulSoup): BeautifulSoup object of a user profile

        Returns:
            dict: Detailed data of each user found on their profile
        """
        def scrape_Handlesaktivitaet():
            """
            Sub-Method scrapes the trading activity of a user. Returns None, if no information in relation to trading activity exists

            Returns:
                dict: trading activity 
            """
            # Funktion zum Finden des gewünschten Elements
            def find_target_element(tag):
                return tag.name == 'li' and 'first-item' in tag.get('class', []) and 'Handelspunkte' in tag.get_text()
            # By passing this function, the beauifulsoup library can find the element in which all the requirements are true
            # So in this case we are trying to find a <li> element with the 'first-item' class and the text equals 'Handelspunkte'
            trade_activity_element = soup.find(find_target_element)
            # Since not all users have this element, we have to check whether that exists
            if trade_activity_element:
                trade_activity_element = trade_activity_element.parent.find_all("li")
            else:
                # If it does not exist, we simply return None, to represent a Null element in the DB later
                return None
            self.log.debug(f"Trading activity information exists! Now scraping...")
            # If the element exists, we want to extract the information regarding the trade activity
            trade_activity = trade_activity_element[0].find("strong").text
            positive_feedbacks = trade_activity_element[1].find("strong").text
            neutral_feedbacks = trade_activity_element[2].find("strong").text
            negative_feedbacks = trade_activity_element[3].find("strong").text

            # This function returns the information found as a dictionary
            return {
                "Handelspunkte": int(trade_activity),
                "Positive Feedbacks": int(positive_feedbacks),
                "Neutrale Feedbacks": int(neutral_feedbacks),
                "Negative Feedbacks": int(negative_feedbacks),
            }
            
        def scrape_Feedback():
            """
            This method is similar to the method before, it first tries to find the element and scrapes if it exists

            Returns:
                dict: Feedback on product packaging, contact, delivery and product itself
            """
            # Funktion zum Finden des gewünschten Elements
            def find_target_element(tag):
                return tag.name == 'h4' and 'ct-legend' in tag.get('class', []) and 'Feedback-Durchschnittswerte' in tag.get_text()
            feedback_reviews = soup.find(find_target_element)
            if feedback_reviews:
                feedback_reviews = feedback_reviews.next_sibling.find_all("li")
            else:
                return None
            self.log.debug(f"Trading Feedback exists! Now scraping...")
            review_packaging = feedback_reviews[0].find("strong").text
            review_transfer = feedback_reviews[1].find("strong").text
            review_product = feedback_reviews[2].find("strong").text

            return {
                "Produktverpackung": review_packaging,
                "Kontakt & Lieferung": review_transfer,
                "Produkt/Dienstleistung": review_product
            }

        def scrape_Feedback_Entries():
            """
            Each user that is a trader has the possibility of customer reviews shown on their profile. Usually it is several reviews of different customers.
            For each review we scraped the relevant information (Author, comment, date, grading/mark) and statistics (positive, neutral, negative feedbacks nr.)

            Returns:
                List: Returns a list of dictionaries. Each dictionary represents a review left on the user's page
            """
            # Funktion zum Finden des gewünschten Elements
            def find_target_element(tag):
                return tag.name == 'h3' and 'ct-legend' in tag.get('class', []) and 'Feedback zum Verkäufer' in tag.get_text()
            # Find an element <h3> that has '.ct-legend' as class name and "Feedback zum Verkäufer" as text
            feedback_rows = soup.find(find_target_element)
            if feedback_rows:
                feedback_rows = feedback_rows.parent.select('div#trade-scroll tbody tr')
            else:
                return None
            self.log.debug(f"Trading Feedback Table exists! Now scraping...")
            feedback_reviews = []
            for row in feedback_rows:
                columns = row.find_all('td')
                if len(columns) >= 4:
                    mark = columns[1].text.strip().lower()
                    # Adding a comma between the feedback and status in the grading/mark
                    if 'positiv' in mark:
                        mark = "Positiv, " + mark.split("positiv")[-1]
                    elif 'negativ' in mark:
                        mark = "Negativ, " + mark.split("negativ")[-1]
                    elif 'neutral' in mark:
                        mark = "Neutral, " + mark.split("neutral")[-1]
                    
                    # If there's no ID, then there's nothing to replace in the date (some reviews have an ID, some do not)
                    if columns[0].span:
                        date = columns[0].text.strip().replace(columns[0].span.text.strip(), "").replace("(Einzelheiten)", "")
                    else:
                        date = columns[0].text.strip().replace("(Einzelheiten)", "")
                    feedback = {
                        'date': date,
                        'mark': mark,
                        'comment': columns[2].text.strip(),
                        'author': columns[3].find_next('a', href=True).find_next('a', href=True).text.strip()
                    }
                    feedback_reviews.append(feedback)

            return feedback_reviews
        
        def scrape_Badge():
            """
            Not each user has a badge, therefore only scrape if exists, otherwise return None
            """
            def find_target_element(tag):
                return tag.name == 'h4' and 'ct-legend' in tag.get('class', []) and 'Abzeichen' in tag.get_text()
            badge = soup.find(find_target_element)
            if badge:
                self.log.debug(f"Badge exists! Now scraping...")
                badge = re.findall("[a-zA-Z]+", badge.next_sibling.select("li a")[0].text)[0]
            return badge

        # Now we call each function to scrape the whole profile information
        badge = scrape_Badge()

        trading_activity = scrape_Handlesaktivitaet()
        feedback_stats = scrape_Feedback()
        feedback_reviews = scrape_Feedback_Entries()

        fingerprint = soup.find('pre')
        if fingerprint:
            fingerprint = fingerprint.text.strip()
        else:
            fingerprint = None
        public_key = soup.find('pre', style='line-height:15px;user-select:all')
        if public_key:
            public_key = public_key.text.strip()
        else:
            public_key = None
        # Then we return all informations for later usage to save
        return badge, trading_activity, feedback_stats, feedback_reviews, fingerprint, public_key

    def get_data(self, link):
        """
         Create a new session to connect to the given link. Use cookies, when set

        Args:
            link (String): Link .onion website that the request should be sent to

        Returns:
            requests.Response: The Response to the request sent prior
        """
        session = requests.session()
        session.proxies = {'http':  'socks5h://localhost:9050',
                        'https': 'socks5h://localhost:9050'}
        if self.cookies:
            return session.get(link, cookies=self.cookies)
        return session.get(link)
        
    def solve_captcha(self, url, response):
        """
        This method is called on each request that is sent to handle a captcha.
        It returns the given soup, if we cannot find a captcha in the response. Therefore, there are no new requests sent, if the response already contains the information we're looking for (AKA NOT the captcha)
        
        Once a captcha is detected, the while-loop will be entered and won't be left unless the response is not a captcha, or the user decides to save the current users it has accumulated.
        3. Options are given: Continue with existing cookies, enter a new cookie or save current user data.
        The user has to input either 
            1.'continue', 
            2.'save' 
            or a new cookie in this format : 
            3."cookie:[NEW COOKIE]" 
            
            WITHOUT any spaces!

        Args:
            url (String): The current (user profile) link which captcha needs to be solved for
            response (requests.Response): The response that potentially has a captcha
            
        Returns:
            BeautifulSoup: soup of website without captcha

        """
        soup = BeautifulSoup(response.content, features='html.parser')
        while soup.find("iframe", {"name":"captcha"}):
            self.log.debug(f"Captcha detected when visiting {url}! Current cookie(s): {self.cookies}")
            user_input = input("Captcha detected!\n3. Options: Continue by typing 'continue', give me a new cookie or save current data. Please enter the information in the following format:\ncookie:[THE COOKIE]\n(NO SPACES!)\nOr simply type 'save'\n")
            self.log.debug(f"User input: {user_input}")
            if user_input.lower() == "continue":
                self.log.debug(f"Continuing with same cookie as before: {self.cookies}")
                new_response = self.get_data(url)
            elif "cookie" in user_input.lower():
                user_input = user_input.split(":")
                self.cookies = { 'PHPSESSID': user_input[1].strip()}
                new_response = self.get_data(url)
            elif user_input.lower() == "save":
                self.log.debug(f"Saving crawled data.")
                self.status = True
                break
            else:
                self.log.debug(f"Input invalid.")
                continue
            if new_response.status_code == 200:
                soup = BeautifulSoup(new_response.content, 'html.parser')

        return soup

    def crawl_profiles(self):
        """
        This method crawls all users on the current userlist page. It also visits each user profile to scrape the detailed information and then saves the data into a DB
        """
        # self.log.debug(f"")
        # self.log.info(f"")
        # self.log.error(f"")
        # self.log.warning(f"")

        # Send an HTTP GET request to the URL
        self.log.debug(f"Now connecting to {self.current_page}.")
        response = self.get_data(self.current_page)

        # Check if the response is successful
        if response.status_code == 200:
            self.log.info(f"Succesful connection! Scraping Users from {self.current_page}!")
            if not self.current_page in self.visited:
                
                # Parse the HTML content using BeautifulSoup
                soup = self.solve_captcha(self.current_page, response)
                if self.status:
                    return
                # Find the <tbody> element containing user information
                tbody = soup.find('tbody')

                # Iterate through each user's <tr> element within the <tbody>
                try:
                    user_rows = tbody.find_all('tr')
                except:
                    # If we cannot find any users on the current page, we simply skip this page and hop on the new one...
                    self.log.error(f"Can't find user list on {self.current_page}. Skipping...")
                    user_rows = []
                    
                for user_row in tqdm(user_rows):
                    # Extract user information from <td> elements within the row
                    columns = user_row.find_all('td')
                    name = columns[0].find('a').text.strip()
                    profile_link = columns[0].find('a')['href']
                    title = columns[1].text.strip()
                    num_posts = columns[2].text.strip().split()[0]
                    points = columns[3].text.strip().split()[0]
                    reg_date = columns[4].text.strip()
                    # Sometimes the users have 'Heute' or 'Gestern' as their registration date instead the actual date, so we change that into the actual date
                    if reg_date=="Heute":
                        reg_date = datetime.today().strftime('%Y-%m-%d')
                    if reg_date=="Gestern":
                        yesterday = datetime.now() - timedelta(1)
                        reg_date = datetime.strftime(yesterday, '%Y-%m-%d')
                    # Send an HTTP GET request to the each profile to get detailed information
                    self.log.debug(f"Connecting to {name}'s profile on {profile_link}.")
                    response_detailed = self.get_data(profile_link)
                    if response_detailed.status_code == 200:
                        self.log.debug(f"Succesfully connected to {name}'s profile.")
                        detailed_soup = self.solve_captcha(profile_link, response_detailed)
                        if self.status:
                            return
                        badge, trade_activity, feedback_stats, feedback_reviews, fingerprint, pk = self.get_profile_details(detailed_soup)

                    # Duplicated, so the entry won't be infected with an _id from pymongo
                    self.users.append({
                        'name': name,
                        'title': title,
                        'number_of_posts': int(num_posts),
                        'points': int(points),
                        'registration_date': reg_date,
                        'badge': badge,
                        'trade_activity': trade_activity,
                        'feedback_statistic': feedback_stats,
                        'feedback_reviews': feedback_reviews,
                        'fingerprint': fingerprint,
                        'public_key': pk,
                        'crawled_datetime': self.crawled_datetime
                    })
                    # Append user information to the list
                    self.log.debug(f"{len(self.users)-self.sum_row}/{len(user_rows)} users crawled.")
            else:
                self.log.debug(f"{self.current_page} already visited! Skipping.")
            # Finished scraping current website, add to visited and look for next one
            self.visited.add(self.current_page)
            # Count the users already added, for debugging purposes
            self.sum_row += len(user_rows)

            # Find the "next" link in the header
            next_link = soup.find('link', rel='next')
            if next_link:
                self.current_page = next_link['href']  # Update the current URL
            else:
                self.current_page = None  # No more "next" link found, exit the loop
        else:
            # If the userlist returns an error, we stop crawling and sent out a warning.
            self.log.warning(f"Failed to retrieve the current URL: {self.current_page}!")
            self.status = True

class User_Profiles():
    """
    This class if practically the same as the class before, without crawling detailed profile information 
    (NO INTERACTION needed)

    Difference: We expect a valid cookie to be given.
    """
    def __init__(self, start_page: int, helper: Helper, db: MySQLConnector = None):
        # Keep track of already visited urls
        self.log = helper.log
        self.log.info("General user_info crawl: Starting to crawl the general user information.")
        self.visited = set()
        self.current_page = config.CRAWLER_USERLIST_LINKS[start_page]
        # Initialize an empty list to store user information
        self.users = []
        # Determine whether to already save currently crawled data
        self.status = False
        self.sum_row = 0
        self.cookies = { 'PHPSESSID': config.CRAWLER_COOKIE }

        self.crawled_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        while self.current_page and not self.status:
            self.crawl_profiles()
            
        # Save the collected user information to a JSON file
        time_now = datetime.now().strftime("%Y-%m-%d_%H-%M")
        with open(f"./data/user_information_{time_now}.json", 'w') as json_file:
            json.dump(self.users, json_file, indent=4)
        self.log.info("User information saved to 'user_information.json'")
        
        # If a MySQLConnector Object is given and exists, load collected data into that DB
        if db:
            db.bulk_load_user_general(self.users)


    def get_data(self, link):
        session = requests.session()
        session.proxies = {'http':  'socks5h://localhost:9050',
                        'https': 'socks5h://localhost:9050'}
        if self.cookies:
            return session.get(link, cookies=self.cookies)
        return session.get(link)

    def crawl_profiles(self):
        # Send an HTTP GET request to the URL
        self.log.debug(f"Now connecting to {self.current_page}.")
        response = self.get_data(self.current_page)

        # Check if the response is successful
        if response.status_code == 200:
            self.log.info(f"Succesful connection! Scraping Users from {self.current_page}!")
            if not self.current_page in self.visited:
                
                # Parse the HTML content using BeautifulSoup
                soup = BeautifulSoup(response.content, features='html.parser')
                if self.status:
                    return
                # Find the <tbody> element containing user information
                tbody = soup.find('tbody')

                # Iterate through each user's <tr> element within the <tbody>
                try:
                    user_rows = tbody.find_all('tr')
                    if not user_rows:
                        self.log.error("Cannot find user list. Probably invalid cookie!")
                        self.status = True
                        return
                except:
                    self.log.error(f"Can't find user list on {self.current_page}.")
                    pass
                
                for user_row in tqdm(user_rows):
                    # Extract user information from <td> elements within the row
                    columns = user_row.find_all('td')
                    name = columns[0].find('a').text.strip()
                    profile_link = columns[0].find('a')['href']
                    title = columns[1].text.strip()
                    num_posts = columns[2].text.strip().split()[0]
                    points = columns[3].text.strip().split()[0]
                    reg_date = columns[4].text.strip()
                    if reg_date=="Heute":
                        reg_date = datetime.today().strftime('%Y-%m-%d')
                    if reg_date=="Gestern":
                        yesterday = datetime.now() - timedelta(1)
                        reg_date = datetime.strftime(yesterday, '%Y-%m-%d')

                    curr_user = {
                        'name': name,
                        'title': title,
                        'link': profile_link,
                        'number_of_posts': int(num_posts),
                        'points': int(points),
                        'registration_date': reg_date,
                        'crawled_datetime': self.crawled_datetime
                    }
                    self.users.append(curr_user)
                    # Append user information to the list
                    self.log.debug(f"{len(self.users)-self.sum_row}/{len(user_rows)} users crawled.")
            else:
                self.log.debug(f"{self.current_page} already visited! Skipping.")
            # Finished scarping, add to visited
            self.visited.add(self.current_page)
            self.sum_row += len(user_rows)

            # Find the "next" link in the header
            next_link = soup.find('link', rel='next')
            if next_link:
                self.current_page = next_link['href']  # Update the current URL
            else:
                self.current_page = None  # No more "next" link found, exit the loop
        else:
            self.log.warning(f"Failed to retrieve the current URL: {self.current_page}!")
            self.status = True
