from lxml import html
from datetime import datetime, timedelta
import requests
import logging

class Forums:
    
    def __init__(self, base_link, cookie):
        self.base_link = base_link
        self.cookie = cookie
        
    def get_forum_info(self, tree=None, html_content=None):
        if html_content:
            tree = html.fromstring(html_content)
        div_elements = tree.xpath('//div[contains(@class, "main-item")]')

        result_divs = []
        for div in div_elements:
            description = div.xpath('.//div[@class="item-subject"]/h3/a/span')[0].text_content()
            onion_link = div.xpath('.//div[@class="item-subject"]/h3/a/@href')[0]
            topics_count = div.xpath('.//li[@class="info-topics"]/strong')[0].text_content()
            posts_count = div.xpath('.//li[@class="info-posts"]/strong')[0].text_content()
            last_post_time = self.__convert_relative_date(
                div.xpath('.//li[@class="info-lastpost"]/strong/a')[0].text_content()
            )
            last_post_author = div.xpath('.//li[@class="info-lastpost"]/cite')[0].text_content()

            result_divs.append({
                "element_type": "forum",
                "forum_title": description,
                "forum_link": onion_link,
                "topics_count": topics_count,
                "posts_count": posts_count,
                "last_post_time": last_post_time,
                "last_post_author": last_post_author
            })

        return result_divs
    
    def get_subforum_info(self, tree=None, html_content=None):
        if html_content:
            tree = html.fromstring(html_content)
        subforum_elements = tree.xpath('//div[contains(@class, "vf-subforum")]')
        
        subforum_info_list = []
        for subforum in subforum_elements:
            subforum_name = subforum.xpath('.//div/h3/a')[0].text_content()
            subforum_link = subforum.xpath('.//div/h3/a/@href')[0]
            topics_count = subforum.xpath('.//ul/li[@class="info-topics"]/strong')[0].text_content()
            posts_count = subforum.xpath('.//ul/li[@class="info-posts"]/strong')[0].text_content()
            last_post_time = self.__convert_relative_date(
                subforum.xpath('.//ul/li[@class="info-lastpost"]/strong/a')[0].text_content()
            )
            last_post_author = subforum.xpath('.//ul/li[@class="info-lastpost"]/cite')[0].text_content()

            subforum_info_list.append({
                "element_type": "subforum",
                "subforum_title": subforum_name,
                "subforum_link": subforum_link,
                "topics_count": topics_count,
                "posts_count": posts_count,
                "last_post_time": last_post_time,
                "last_post_author": last_post_author
            })
        
        return subforum_info_list
    
    def get_posts_info(self, tree=None, html_content=None):
        if html_content:
            tree = html.fromstring(html_content)
        post_elements = tree.xpath("//div[contains(@class, 'main-item')]")

        posts = []
        for post_element in post_elements:
            if "moved" in post_element.attrib["class"]:
                continue
            title = post_element.xpath(".//div/h3/a")[0].text_content()
            post_link = post_element.xpath(".//div/h3/a/@href")[0]
            author = post_element.xpath(".//p/span/cite")[0].text_content()
            replies_count = post_element.xpath(".//ul/li[@class='info-replies']/strong")[0].text_content()
            views_count = post_element.xpath(".//ul/li[@class='info-views']/strong")[0].text_content()
            last_post_time = self.__convert_relative_date(
                post_element.xpath(".//ul/li[@class='info-lastpost']/strong/a")[0].text_content()
            )
            last_post_author = post_element.xpath(".//ul/li[@class='info-lastpost']/cite")[0].text_content()

            posts.append({
                "element_type": "post",
                "post_title": title,
                "post_link": post_link,
                "author": author,
                "replies_count": replies_count,
                "views_count": views_count,
                "last_post_time": last_post_time,
                "last_post_author": last_post_author
            })

        return posts
    
    def crawl_forums(self):
        html_content = self.__request_onion_sites()
        forums = self.get_forum_info(html_content=html_content.text)
        for idx_forums, forum in enumerate(forums):
            forum_html_content = self.__request_onion_sites(forum["forum_link"])
            forum_tree = html.fromstring(forum_html_content.text)
            if forum_tree.xpath('//div[contains(@class, "vf-subforum")]'):
                subforums = self.get_subforum_info(forum_tree)
                for idx_subforum, subforum in enumerate(subforums):
                    subforum_html_content = self.__request_onion_sites(subforum["subforum_link"])
                    posts = self.get_posts_info(html_content=subforum_html_content.text)
                    subforums[idx_subforum]["posts"] = posts
                forums[idx_forums]["subforums"] = subforums
            elif forum_tree.xpath('//div[contains(@class, "forum-views")]'):
                posts = self.get_posts_info(forum_tree)
                forums[idx_forums]["posts"] = posts
            else:
                return ["No matching HTML structure found!"]
        return forums
    
    def __request_onion_sites(self, link=None):
        session = requests.session()
        session.proxies = {'http':  'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}
        cookies = { 'PHPSESSID': self.cookie}
        if link:
            data = session.get(link, cookies=cookies)
        else:
            data = session.get(self.base_link, cookies=cookies)
        return data

    def __convert_relative_date(self, relative_date):
        today = datetime.now().date()
        
        if "heute" in relative_date.lower():
            return today.strftime("%Y-%m-%d")
        elif "gestern" in relative_date.lower():
            yesterday = today - timedelta(days=1)
            return yesterday.strftime("%Y-%m-%d")
        else:
            parts = relative_date.split()
            return parts[0]