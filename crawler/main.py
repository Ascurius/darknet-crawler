# Copyright (C) 2023 Xian Chen, Martin Pretz

import config
from forums import Forums
from database import MySQLConnector
from helper import Helper
from user_crawler import User_Detailed_Profiles, User_Profiles

# Initalize needed helper methods and database
helper = Helper(config.LOGGING_FILE_PATH)
db = MySQLConnector(helper=helper)
# Initiate user interaction for first cookie
cookie = None
helper.log.info("Please visit http://germania7zs27fu3gi76wlr5rd64cc2yjexyzvrbm4jufk7pibrpizad.onion and solve one captcha.")
# Need for cookie
while not cookie:
    cookie = input("Enter the valid PHPSESSID cookie here:\n")
    if len(cookie) < 5:
        helper.log.warn("You entered an invalid cookie, please try again.")
        cookie = None
        continue
    config.CRAWLER_COOKIE = cookie
# Instantiate Forum crawler
forum_scraper = Forums(
    base_link=config.CRAWLER_BASE_LINK,
    cookie=config.CRAWLER_COOKIE,
    helper=helper,
    db=db
)
# Crawl forums
forum_scraper.crawl_forums(auto_push_db=True)

# Then choose the page number
start_page = int(input("At what page number [1,25] do we start scraping the users?\n"))-1
while start_page > 24 or start_page < 0:
    start_page = int(input("The userlist has 25 pages.\nAt what page number [1,25] do you want to start scraping?\n"))-1

# Ask user, whether they want in interactive long crawl for detailed information, or a general fast crawl
choice = int(input("Do you want to crawl the general user information (type '1') or crawl the detailed profiles additionally (type '2')?\n[Warning: Detailed crawl is an interactive crawl, could take up to hours!]\n"))
if choice == 1:
    User_Profiles(start_page, helper, db)
elif choice == 2:
    User_Detailed_Profiles(start_page, helper, db)
else:
    helper.log.warn("Invalid crawler chosen.")
