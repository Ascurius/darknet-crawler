import sys
import config
import mysql.connector
from helper import Helper
from tqdm import tqdm
from mysql.connector.errors import ProgrammingError, DatabaseError
  
class MySQLConnector():

    def __init__(self, helper: Helper):
        self.log = helper.log
        self.log.info("Initializing database connection")
        try:
            self.connection = mysql.connector.connect(
                user=config.MYSQL_USER, 
                password=config.MYSQL_PASSWORD, 
                host=config.MYSQL_HOST
            )
        except ProgrammingError as ProErr:
            self.log.error("Failed to init database connection. Probably authentication failed")
            self.log.debug("Error details: ", exc_info=ProErr)
            sys.exit(-1)
        except DatabaseError as DBErr:
            self.log.error("Failed to init database connection. Probably could not connect to DB")
            self.log.debug("Error details: ", exc_info=DBErr)
            sys.exit(-2)
        self.cursor = self.connection.cursor(dictionary=True)
        self.init_database()
        self.init_tables()

    def init_database(self):
        """
        Initializes the database for storing scraped data.

        Note:
            This method is intended for internal use within the ForumScraper class.

        Example:
            connector = MySQLConnector()
            connector.init_database()
        """
        self.log.debug("Init database")
        database = config.MYSQL_DATABASE
        check_db_query = f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{database}'"
        self.cursor.execute(check_db_query)
        database_exists = self.cursor.fetchone()
        if database_exists:
            self.log.debug(f"Database '{database}' exists")
        else:
            self.log.warning(f"Database '{database}' does not exist")
            create_db_query = f"CREATE DATABASE {database}"
            try:
                self.cursor.execute(create_db_query)
            except Exception as err:
                self.log.error(f"Failed to create database '{database}'")
                self.log.debug("Error details: ", exc_info=err)
            self.log.debug(f"Database '{database}' created")
        self.connection.database = database

    def init_tables(self):
        """
        Initializes the database tables for storing scraped data.

        Note:
            This method is intended for internal use within the ForumScraper class.

        Example:
            connector = MySQLConnector()
            connector.init_tables()
        """
        self.log.info("Init tables")
        try:
            self.log.debug("Init forums table")
            self.cursor.execute(config.CREATE_FORUMS_TABLE_QUERY)
            self.log.debug("Forums table created successfully")

            self.log.debug("Init subforums table")
            self.cursor.execute(config.CREATE_SUBFORUMS_TABLE_QUERY)
            self.log.debug("Subforums table created successfully")

            self.log.debug("Init posts table")
            self.cursor.execute(config.CREATE_POSTS_TABLE_QUERY)
            self.log.debug("Posts table created successfully")

            self.log.debug("Init users detailed table")
            self.cursor.execute(config.CREATE_USERS_DETAILED_TABLE_QUERY)
            self.log.debug("Users detailed table created successfully")

            self.log.debug("Init users general table")
            self.cursor.execute(config.CREATE_USERS_GENERAL_TABLE_QUERY)
            self.log.debug("Users general table created successfully")

            self.log.debug("Init feedback review table")
            self.cursor.execute(config.CREATE_FEEDBACK_REVIEW_TABLE)
            self.log.debug("Feedback review table created successfully")

        except Exception as err:
            self.log.warning("Table creation failed")
            self.log.debug("Error details:", exc_info=err)

    def load_forums(self, data):
        """
        Loads forum data into the database.

        Args:
            data (list): A list of dictionaries containing forum, subforum, and post information.

        Note:
            This method is intended for internal use within the ForumScraper class.

        Example:
            connector = MySQLConnector()
            connector.load_forums(forum_data)
        """
        self.log.info("Loading forums into DB")
        try:
            pbar = tqdm(total=len(data), desc="Progress", unit="forum")
            for forum_data in data:
                if "subforums" in forum_data:
                    forum_values = {key: value for key, value in forum_data.items() if key != "subforums"}
                    self.cursor.execute(config.INSERT_FORUMS_QUERY, tuple(forum_values.values()))
                    forum_id = self.cursor.lastrowid
                    
                    for subforum_data in forum_data["subforums"]:
                        subforum_values = {key: value for key, value in subforum_data.items() if key != "posts"}
                        self.cursor.execute(config.INSERT_SUBFORUMS_QUERY, tuple(subforum_values.values()) + (forum_id,))
                        subforum_id = self.cursor.lastrowid
                        
                        for post_data in subforum_data.get("posts", []):
                            post_values = {key: value for key, value in post_data.items()}
                            self.cursor.execute(config.INSERT_POSTS_WITH_SUBFORUM_QUERY, tuple(post_values.values()) + (subforum_id,))
                else:
                    forum_values = {key: value for key, value in forum_data.items() if key != "posts"}
                    self.cursor.execute(config.INSERT_FORUMS_QUERY, tuple(forum_values.values()))
                    forum_id = self.cursor.lastrowid
                    
                    for post_data in forum_data.get("posts", []):
                        post_values = {key: value for key, value in post_data.items()}
                        self.cursor.execute(config.INSERT_POSTS_WITH_FORUM_QUERY, tuple(post_values.values()) + (forum_id,))
                pbar.update(1)
        except Exception as err:
            self.log.error("Failed to load forums data to DB")
            self.log.debug("Error details: ", exc_info=err)
        finally:
            self.connection.commit()

    def single_load_user_detailed(self, single_user_data):
        """
        Loads detailed user data into the database.

        Args:
            single_user_data (dict): A dictionary containing detailed user information.

        Returns:
            int: The ID of the inserted user in the database.

        Note:
            This method is intended for internal use within the ForumScraper class.

        Example:
            connector = MySQLConnector()
            user_id = connector.single_load_user_detailed(single_user_data)
        """
        self.log.debug("Loading single user data into DB")
        try:
            single_user_values = self.__clean_detailed_user(single_user_data)
            self.cursor.execute(config.INSERT_USER_DETAILED_DATA, tuple(single_user_values.values()))
            return self.cursor.lastrowid
        except Exception as err:
            self.log.error("Failed to load user data")
            self.log.debug("Error details: ", exc_info=err)
        finally:
            self.connection.commit()

    def single_load_user_general(self, single_user_data):
        """
        Loads general user data into the database.

        Args:
            single_user_data (dict): A dictionary containing general user information.

        Returns:
            int: The ID of the inserted user in the database.

        Note:
            This method is intended for internal use within the ForumScraper class.

        Example:
            connector = MySQLConnector()
            user_id = connector.single_load_user_general(single_user_data)
        """
        self.log.debug("Loading single user data into DB")
        try:
            self.cursor.execute(config.INSERT_USER_GENERAL_DATA, tuple(single_user_data.values()))
            return self.cursor.lastrowid
        except Exception as err:
            self.log.error("Failed to load user data")
            self.log.debug("Error details: ", exc_info=err)
        finally:
            self.connection.commit()

    def single_load_user_feedback(self, feedback_data, user_id, crawling_date):
        """
        Loads user feedback data into the database.

        Args:
            feedback_data (dict): A dictionary containing user feedback information.
            user_id (int): The ID of the user in the database.
            crawling_date (str): The crawling date in the format '%Y-%m-%d %H:%M:%S'.

        Note:
            This method is intended for internal use within the ForumScraper class.

        Example:
            connector = MySQLConnector()
            user_id = 123  # Replace with the actual user ID
            crawling_date = "2023-09-01 12:00:00"  # Replace with the actual crawling date
            feedback_data = {
                "rating": 5,
                "comment": "Great user experience."
            }
            connector.single_load_user_feedback(feedback_data, user_id, crawling_date)
        """
        self.log.debug("Loading user feedback data into DB")
        try:
            feedback_values = (user_id, crawling_date) + tuple(feedback_data.values())
            self.cursor.execute(config.INSERT_USER_FEEDBACK_QUERY, feedback_values)
        except Exception as err:
            self.log.error("Failed to load user feedback data")
            self.log.debug("Error details: ", exc_info=err)
        finally:
            self.connection.commit()

    def bulk_load_user_general(self, user_list):
        """
        Bulk loads general user data into the database.

        Args:
            user_list (list): A list of dictionaries containing general user information.

        Note:
            This method is intended for internal use within the ForumScraper class.

        Example:
            connector = MySQLConnector()
            user_data = [
                {"username": "user1", "age": 25},
                {"username": "user2", "age": 30},
                # ...
            ]
            connector.bulk_load_user_general(user_data)
        """
        self.log.info("Bulk loading general user data into db")
        try:
            with tqdm(total=len(user_list), desc="Progress", unit="user") as pbar:
                for user in user_list:
                    self.cursor.execute(config.INSERT_USER_GENERAL_DATA, tuple(user.values()))
                    pbar.update(1)
        except Exception as err:
            self.log.error("Failed to bulk load general user data")
            self.log.debug("Error details: ", exc_info=err)
        finally:
            self.connection.commit()

    def bulk_load_user_detailed(self, user_list):
        """
        Bulk loads detailed user data into the database.

        Args:
            user_list (list): A list of dictionaries containing detailed user information.

        Note:
            This method is intended for internal use within the ForumScraper class.

        Example:
            connector = MySQLConnector()
            user_data = [
                {
                    "username": "user1",
                    "age": 25,
                    "feedback_reviews": [
                        {"rating": 5, "comment": "Great experience."},
                        {"rating": 4, "comment": "Good service."}
                    ],
                    "crawled_datetime": "2023-09-01 12:00:00"
                },
                {
                    "username": "user2",
                    "age": 30,
                    # ...
                },
                # ...
            ]
            connector.bulk_load_user_detailed(user_data)
        """
        self.log.info("Bulk loading general user data into db")
        try:
            with tqdm(total=len(user_list), desc="Progress", unit="user") as pbar:
                for user_data in user_list:
                    user_values = self.__clean_detailed_user(user_data)
                    self.cursor.execute(config.INSERT_USER_DETAILED_DATA, tuple(user_values.values()))
                    user_id = self.cursor.lastrowid

                    if user_data["feedback_reviews"]:
                        for feedback_review in user_data["feedback_reviews"]:
                            self.single_load_user_feedback(feedback_review, user_id, user_data["crawled_datetime"])
                    pbar.update(1)
        except Exception as err:
            self.log.error("Failed to bulk load detailed user data")
            self.log.debug("Error details: ", exc_info=err)
            self.log.debug(user_values)
        finally:
            self.connection.commit()

    def delete_tables(self, table_list):
        """
        Deletes specified tables from the database.

        Args:
            table_list (list): A list of table names to be deleted.

        Example:
            connector = MySQLConnector()
            tables_to_delete = ["users", "posts", "feedback"]
            connector.delete_tables(tables_to_delete)
        """
        for table_name in table_list:
            delete_query = f"DROP TABLE IF EXISTS {table_name}"
            try:
                self.cursor.execute(delete_query)
                self.log.debug(f"Table '{table_name}' deleted successfully.")
            except mysql.connector.Error as err:
                self.log.error(f"Error while deleting table {table_name}")
                self.log.debug(f"Error: {err}")
            finally:
                self.connection.commit()

    def __clean_detailed_user(self, data):
        """
        Cleans detailed user data for insertion into the database.

        Args:
            data (dict): A dictionary containing detailed user information.

        Returns:
            dict: A dictionary with cleaned user data for database insertion.

        Note:
            This method is intended for internal use within the ForumScraper class.

        Example:
            connector = MySQLConnector()
            user_data = {
                "name": "John Doe",
                "crawled_datetime": "2023-09-01 12:00:00",
                "title": "Regular User",
                "number_of_posts": 100,
                "points": 500,
                # ...
            }
            cleaned_user_data = connector.__clean_detailed_user(user_data)
        """
        cleaned_user = {
            "name": data["name"],
            "crawling_date": data["crawled_datetime"],
            "title": data["title"],
            "number_of_points": data["number_of_posts"],
            "points": data["points"],
            "registration_date": data["registration_date"],
            "badge": data["badge"]
        }
        if data["trade_activity"]:
            cleaned_user["trade_activity_handelspunkte"] = data["trade_activity"]["Handelspunkte"]
            cleaned_user["trade_activity_positive"] = data["trade_activity"]["Positive Feedbacks"]
            cleaned_user["trade_activity_neutral"] = data["trade_activity"]["Neutrale Feedbacks"]
            cleaned_user["trade_activity_negative"] = data["trade_activity"]["Negative Feedbacks"]
        else:
            cleaned_user["trade_activity_handelspunkte"] = None
            cleaned_user["trade_activity_positive"] = None
            cleaned_user["trade_activity_neutral"] = None
            cleaned_user["trade_activity_negative"] = None
        if data["feedback_statistic"]:
            cleaned_user["feedback_statistic_produktverpackung"] = data["feedback_statistic"]["Produktverpackung"]
            cleaned_user["feedback_statistic_kontakt_lieferung"] = data["feedback_statistic"]["Kontakt & Lieferung"]
            cleaned_user["feedback_statistic_produkt_dienstleistung"] = data["feedback_statistic"]["Produkt/Dienstleistung"]
        else:
            cleaned_user["feedback_statistic_produktverpackung"] = None
            cleaned_user["feedback_statistic_kontakt_lieferung"] = None
            cleaned_user["feedback_statistic_produkt_dienstleistung"] = None
        cleaned_user["fingerprint"] = data["fingerprint"]
        cleaned_user["public_key"] = data["public_key"]
        return cleaned_user

    def get_all_posts(self):
        """
        Retrieves all posts from the database.

        Returns:
            list: A list of dictionaries containing post data.

        Example:
            connector = MySQLConnector()
            posts = connector.get_all_posts()
        """
        query = "SELECT * FROM posts"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_all_forums(self):
        """
        Retrieves all forums from the database.

        Returns:
            list: A list of dictionaries containing forum data.

        Example:
            connector = MySQLConnector()
            forums = connector.get_all_forums()
        """
        query = "SELECT * FROM forums"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_all_subforums(self):
        """
        Retrieves all subforums from the database.

        Returns:
            list: A list of dictionaries containing subforum data.

        Example:
            connector = MySQLConnector()
            subforums = connector.get_all_subforums()
        """
        query = "SELECT * FROM subforums"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_all_users_detailed(self):
        """
        Retrieves all detailed user data from the database.

        Returns:
            list: A list of dictionaries containing detailed user data.

        Example:
            connector = MySQLConnector()
            users_detailed = connector.get_all_users_detailed()
        """
        query = "SELECT * FROM users_detailed"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_all_users_general(self):
        """
        Retrieves all general user data from the database.

        Returns:
            list: A list of dictionaries containing general user data.

        Example:
            connector = MySQLConnector()
            users_general = connector.get_all_users_general()
        """
        query = "SELECT * FROM users_general"
        self.cursor.execute(query)
        return self.cursor.fetchall()