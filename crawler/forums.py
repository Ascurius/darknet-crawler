# Copyright (C) 2023 Martin Pretz

import requests
from lxml import html
from datetime import datetime, timedelta
from helper import Helper
from database import MySQLConnector

class Forums():
    
    def __init__(self, base_link, cookie, helper: Helper, db: MySQLConnector):
        self.log = helper.log
        self.db = db
        self.base_link = base_link
        self.log.debug("Forum crawler base link: {}".format(self.base_link))
        self.log.debug("Forum crawler cookie: {}".format(cookie))

        self.session = requests.session()
        self.session.proxies = {'http':  'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}
        self.session.cookies.update({'PHPSESSID': cookie})
        
    def get_forum_info(self, crawling_date, tree=None, html_content=None):
        """
        Extracts forum information from the index page.

        Args:
            tree (ElementTree, optional): The parsed HTML tree of the index page.
            html_content (str, optional): The raw HTML content of the index page.

        Returns:
            list: A list of dictionaries containing forum information.

        Example:
            scraper = ForumScraper()
            forum_info = scraper.get_forum_info(html_content=index_page_content)
        """
        self.log.debug("Started extracting forum information")
        if html_content:
            tree = html.fromstring(html_content)
        div_elements = tree.xpath('//div[contains(@class, "main-item")]')

        result_divs = []
        for idx, div in enumerate(div_elements):
            self.log.debug("Extracting forum information [{} of {}]"
                           .format(idx+1, len(div_elements)))
            try:
                forum_description = div.xpath('.//div[@class="item-subject"]/h3/a/span')[0].text_content()
                forum_link = div.xpath('.//div[@class="item-subject"]/h3/a/@href')[0]
                topics_count = div.xpath('.//li[@class="info-topics"]/strong')[0].text_content()
                posts_count = div.xpath('.//li[@class="info-posts"]/strong')[0].text_content()
                last_post_time = self.__convert_relative_date(
                    div.xpath('.//li[@class="info-lastpost"]/strong/a')[0].text_content()
                )
                last_post_author = div.xpath('.//li[@class="info-lastpost"]/cite')[0].text_content()

                self.log.debug("Successfully extracted information of forum: {}".format(forum_link))
            except IndexError as err:
                self.log.error("Could not extract forum information")
                self.log.debug("Error details: ", exc_info=err)
                continue
                
            result_divs.append({
                "element_type": "forum",
                "crawling_date": crawling_date,
                "title": forum_description,
                "link": forum_link,
                "topics_count": topics_count,
                "posts_count": posts_count,
                "last_post_time": last_post_time,
                "last_post_author": last_post_author
            })
        
        return result_divs
    
    def get_subforum_info(self, crawling_date, tree=None, html_content=None):
        """
        Extracts subforum information from a given forum page.

        Args:
            tree (ElementTree, optional): The parsed HTML tree of the forum page.
            html_content (str, optional): The raw HTML content of the forum page.

        Returns:
            list: A list of dictionaries containing subforum information.

        Example:
            scraper = ForumScraper()
            subforum_info = scraper.get_subforum_info(html_content=page_content)
        """
        self.log.debug("Started extracting subforum information")
        if html_content:
            tree = html.fromstring(html_content)
        subforum_elements = tree.xpath('//div[contains(@class, "vf-subforum")]')
        
        subforum_info_list = []
        for idx, subforum in enumerate(subforum_elements):
            self.log.debug("Extracting subforum information [{} of {}]"
                           .format(idx+1, len(subforum_elements)))
            try:
                subforum_name = subforum.xpath('.//div/h3/a')[0].text_content()
                subforum_link = subforum.xpath('.//div/h3/a/@href')[0]
                topics_count = subforum.xpath('.//ul/li[@class="info-topics"]/strong')[0].text_content()
                posts_count = subforum.xpath('.//ul/li[@class="info-posts"]/strong')[0].text_content()
                last_post_time = self.__convert_relative_date(
                    subforum.xpath('.//ul/li[@class="info-lastpost"]/strong/a')[0].text_content()
                )
                last_post_author = subforum.xpath('.//ul/li[@class="info-lastpost"]/cite')[0].text_content()
            except IndexError as err:
                self.log.error("Could not extract forum information")
                self.log.debug("Error details: ", exc_info=err)
                continue

            subforum_info_list.append({
                "element_type": "subforum",
                "crawling_date": crawling_date,
                "title": subforum_name,
                "link": subforum_link,
                "topics_count": topics_count,
                "posts_count": posts_count,
                "last_post_time": last_post_time,
                "last_post_author": last_post_author
            })

        return subforum_info_list
    
    def get_posts_info(self, crawling_date, tree=None, html_content=None):
        """
        Extracts post information from a forum or subforum page.

        Args:
            tree (ElementTree, optional): The parsed HTML tree of the forum page.
            html_content (str, optional): The raw HTML content of the forum page.

        Returns:
            list: A list of dictionaries containing post information.

        Example:
            scraper = ForumScraper()
            post_info = scraper.get_posts_info(html_content=forum_page_content)
        """
        self.log.debug("Started extracting post information")
        if html_content:
            tree = html.fromstring(html_content)
        post_elements = tree.xpath("//div[contains(@class, 'main-item')]")

        posts = []
        for idx, post_element in enumerate(post_elements):
            self.log.debug("Extracting post information [{} of {}]"
                           .format(idx+1, len(post_elements)))
            if "moved" in post_element.attrib["class"]:
                self.log.debug("Sipping posts because it does no longer exists")
                continue
            try:
                post_title = post_element.xpath(".//div/h3/a")[0].text_content()
                post_link = post_element.xpath(".//div/h3/a/@href")[0]
                author = post_element.xpath(".//p/span/cite")[0].text_content()
                replies_count = post_element.xpath(".//ul/li[@class='info-replies']/strong")[0].text_content()
                views_count = post_element.xpath(".//ul/li[@class='info-views']/strong")[0].text_content()
                last_post_time = self.__convert_relative_date(
                    post_element.xpath(".//ul/li[@class='info-lastpost']/strong/a")[0].text_content()
                )
                last_post_author = post_element.xpath(".//ul/li[@class='info-lastpost']/cite")[0].text_content()

                self.log.debug("Successfully extracted information of post: {}".format(post_link))
            except IndexError as err:
                self.log.error("Could not extract post information")
                self.log.debug("Error details: ", exc_info=err)
                continue

            posts.append({
                "element_type": "post",
                "crawling_date": crawling_date,
                "title": post_title,
                "link": post_link,
                "author": author,
                "replies_count": replies_count.replace(",", ""),
                "views_count": views_count.replace(",", ""),
                "last_post_time": last_post_time,
                "last_post_author": last_post_author
            })

        return posts
    
    def crawl_forums(self, auto_push_db=False):
        """
        Crawls forums to extract forum, subforum, and post information.

        Args:
            auto_push_db (bool, optional): Indicates whether to automatically push data to the database.

        Returns:
            list or None: A list of dictionaries containing extracted forum, subforum, and post information.

        Example:
            scraper = ForumScraper()
            forum_data = scraper.crawl_forums(auto_push_db=True)
        """
        self.log.info("Started crawling the forums")
        html_content = self.__request_onion_sites()
        if not html_content:
            return None
        crawling_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.forum_data = self.get_forum_info(crawling_date, html_content=html_content.text)
        for idx_forums, forum in enumerate(self.forum_data):
            self.log.info("[{}/{}] Processing forum...".format(idx_forums+1, len(self.forum_data)))
            self.log.debug("Processing forum: {}".format(forum["link"]))
            forum_html_content = self.__request_onion_sites(forum["link"])
            forum_tree = html.fromstring(forum_html_content.text)
            if forum_tree.xpath('//div[contains(@class, "vf-subforum")]'):
                subforums = self.get_subforum_info(crawling_date, tree=forum_tree)
                for idx_subforum, subforum in enumerate(subforums):
                    self.log.debug("[{}/{}] Processing subforum: {}"
                                   .format(idx_subforum+1, len(subforums), subforum["link"]))
                    subforum_html_content = self.__request_onion_sites(subforum["link"])
                    posts = self.get_posts_info(crawling_date, html_content=subforum_html_content.text)
                    subforums[idx_subforum]["posts"] = posts
                self.forum_data[idx_forums]["subforums"] = subforums
            elif forum_tree.xpath('//div[contains(@class, "forum-views")]'):
                self.log.debug("Forums does not contain subforums")
                posts = self.get_posts_info(crawling_date, tree=forum_tree)
                self.forum_data[idx_forums]["posts"] = posts
            else:
                self.log.error("No matching HTML structure found. Provided HTML is neither post view forum nor subforum")
                return None
        if auto_push_db:
            self.db.load_forums(self.forum_data)
        return self.forum_data
    
    def __request_onion_sites(self, link=None):
        """
        Sends a request to an onion site and returns the response data.

        Args:
            link (str, optional): The URL of the onion site. If not provided, uses the base link.

        Returns:
            requests.Response or None: The response object if successful, else None.

        Note:
            This method is intended for internal use within the ForumScraper class.

        Example:
            response = self.__request_onion_sites(link="http://example.onion")
        """
        self.log.debug("Sending request for {}"
                       .format(link if link else self.base_link))
        data = self.session.get(link if link else self.base_link)
        if "phishing" in data.text.lower():
            self.log.error("Received phishing mirror respose. Probably invalid cookie")
            self.log.debug(data.text)
        elif data.status_code == 200:
            self.log.debug("Successfully received response")
            return data
        else:
            self.log.error("Received unexpected response {}".format(data.status_code))
            self.log.debug(data.text)
        return None

    def __convert_relative_date(self, relative_date):
        """
        Converts a relative date string into a formatted date string.

        Args:
            relative_date (str): The relative date string to be converted.

        Returns:
            str: The formatted date string.

        Note:
            This method is intended for internal use within the ForumScraper class.

        Example:
            converted_date = self.__convert_relative_date("heute")
        """
        today = datetime.now().date()
        
        if "heute" in relative_date.lower():
            return today.strftime("%Y-%m-%d")
        elif "gestern" in relative_date.lower():
            yesterday = today - timedelta(days=1)
            return yesterday.strftime("%Y-%m-%d")
        else:
            parts = relative_date.split()
            return parts[0]