LOGGING_VERBOSITY = 1
LOGGING_FILE_PATH = "./darknet-crawler.log"

MYSQL_DATABASE = "germania"
MYSQL_USER = "user"
MYSQL_PASSWORD = "User1234"
MYSQL_ROOT_PASSWORD = "User1234"
MYSQL_HOST = "127.0.0.1"

CRAWLER_USERLIST_LINKS = ["http://germania7zs27fu3gi76wlr5rd64cc2yjexyzvrbm4jufk7pibrpizad.onion/userlist.php?show_group=-1&sort_by=karma&sort_dir=DESC&username=-"] + [f"http://germania7zs27fu3gi76wlr5rd64cc2yjexyzvrbm4jufk7pibrpizad.onion/userlist.php?show_group=-1&sort_by=karma&sort_dir=DESC&username=-&p={i}" for i in range(2,26)]
CRAWLER_BASE_LINK = "http://germania7zs27fu3gi76wlr5rd64cc2yjexyzvrbm4jufk7pibrpizad.onion"
CRAWLER_COOKIE = "5rccd78prsqqgn8p0ufngob5g7mpiop330ka3op3u9dke8qj"

MYSQL_TABLE_NAME_LIST = ["posts", "subforums", "forums", "users_feedback", "users_general", "users_detailed"]

CREATE_FORUMS_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS forums (
    forum_id INT AUTO_INCREMENT PRIMARY KEY,
    element_type VARCHAR(255) NOT NULL,
    crawling_date DATETIME NOT NULL,
    title VARCHAR(255) NOT NULL,
    link VARCHAR(255) NOT NULL,
    topics_count INT NOT NULL,
    posts_count INT NOT NULL,
    last_post_time DATE NOT NULL,
    last_post_author VARCHAR(255) NOT NULL
)
"""

CREATE_SUBFORUMS_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS subforums (
    subforum_id INT AUTO_INCREMENT PRIMARY KEY,
    forum_id INT,
    element_type VARCHAR(255) NOT NULL,
    crawling_date DATETIME NOT NULL,
    title VARCHAR(255) NOT NULL,
    link VARCHAR(255) NOT NULL,
    topics_count INT NOT NULL,
    posts_count INT NOT NULL,
    last_post_time DATE NOT NULL,
    last_post_author VARCHAR(255) NOT NULL,
    FOREIGN KEY (forum_id) REFERENCES forums(forum_id)
)
"""

CREATE_POSTS_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS posts (
    post_id INT AUTO_INCREMENT PRIMARY KEY,
    forum_id INT,
    subforum_id INT,
    element_type VARCHAR(255) NOT NULL,
    crawling_date DATETIME NOT NULL,
    title VARCHAR(255) NOT NULL,
    link VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    replies_count INT NOT NULL,
    views_count BIGINT NOT NULL,
    last_post_time DATE NOT NULL,
    last_post_author VARCHAR(255) NOT NULL,
    FOREIGN KEY (forum_id) REFERENCES forums(forum_id),
    FOREIGN KEY (subforum_id) REFERENCES subforums(subforum_id)
)
"""

CREATE_USERS_DETAILED_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS users_detailed (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    crawling_date DATETIME NOT NULL,
    title VARCHAR(255) NOT NULL,
    number_of_points INT NOT NULL,
    points INT NOT NULL,
    registration_date VARCHAR(255) NOT NULL,
    badge VARCHAR(255),
    trade_activity_handelspunkte INT,
    trade_activity_positive INT,
    trade_activity_neutral INT,
    trade_activity_negative INT,
    feedback_statistic_produktverpackung VARCHAR(255),
    feedback_statistic_kontakt_lieferung VARCHAR(255),
    feedback_statistic_produkt_dienstleistung VARCHAR(255),
    fingerprint VARCHAR(255),
    public_key TEXT
)
"""

CREATE_USERS_GENERAL_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS users_general (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    link VARCHAR(255),
    number_of_posts INT,
    points INT,
    registration_date DATE,
    crawled_datetime DATETIME
)
"""

CREATE_FEEDBACK_REVIEW_TABLE = """
CREATE TABLE IF NOT EXISTS users_feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    crawling_date DATETIME NOT NULL,
    date VARCHAR(255) NOT NULL,
    mark VARCHAR(255) NOT NULL,
    comment VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users_detailed(user_id)
)
"""

INSERT_FORUMS_QUERY = """
    INSERT INTO forums (element_type, crawling_date, title, link, topics_count, posts_count, last_post_time, last_post_author)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """
INSERT_SUBFORUMS_QUERY = """
    INSERT INTO subforums (element_type, crawling_date, title, link, topics_count, posts_count, last_post_time, last_post_author, forum_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
INSERT_POSTS_WITH_SUBFORUM_QUERY = """
    INSERT INTO posts (element_type, crawling_date, title, link, author, replies_count, views_count, last_post_time, last_post_author, subforum_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
INSERT_POSTS_WITH_FORUM_QUERY = """
    INSERT INTO posts (element_type, crawling_date, title, link, author, replies_count, views_count, last_post_time, last_post_author, forum_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
INSERT_USER_FEEDBACK_QUERY = """
    INSERT INTO users_feedback (user_id, crawling_date, date, mark, comment, author)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
INSERT_USER_DETAILED_DATA = """
    INSERT INTO users_detailed (name, crawling_date, title, number_of_points, points, registration_date, badge,
                   trade_activity_handelspunkte, trade_activity_positive, trade_activity_neutral,
                   trade_activity_negative, feedback_statistic_produktverpackung,
                   feedback_statistic_kontakt_lieferung, feedback_statistic_produkt_dienstleistung,
                   fingerprint, public_key)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
INSERT_USER_GENERAL_DATA = """
    INSERT INTO users_general (name, title, link, number_of_posts, points, registration_date, crawled_datetime)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """