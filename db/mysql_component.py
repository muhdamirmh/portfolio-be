import mysql.connector
from dotenv import load_dotenv
import os
import core.utils as utils

# Load environment variables from .env file
load_dotenv(".env", override=True)


class MySQLConnector:
    def __init__(self, app=None, host_rw=None, host_ro=None, user=None, password=None, database=None, port=None):
        # Connection parameters for read-write operations

        try:
            self.conn_params_rw = {
                "host": host_rw or os.getenv("HOST"),
                "user": user or os.getenv("USER"),
                "password": password or os.getenv("PASSWORD"),
                "database": database or os.getenv("DATABASE"),
                "port": port or os.getenv("PORT"),
            }

            # Connection parameters for read-only operations
            self.conn_params_ro = {
                "host": host_ro or os.getenv("HOST_READONLY"),
                "user": user or os.getenv("USER"),
                "password": password or os.getenv("PASSWORD"),
                "database": database or os.getenv("DATABASE"),
                "port": port or os.getenv("PORT"),
            }
        except mysql.connector.Error as err:
            print(f"Error mysql.connector: {err}")
            self.conn_params_rw = None
            self.conn_params_ro = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        pass  # Initialization can be handled here if needed

    def get_connection(self, read_only=False):
        try:
            # Choose connection parameters based on read-only flag
            connection_params = (
                self.conn_params_ro if read_only else self.conn_params_rw
            )

            connection = mysql.connector.connect(**connection_params)

            if read_only:
                connection.start_transaction(readonly=True)

            return connection
        except mysql.connector.Error as e:
            print(f"Error: {e}")
            return None

    def execute_query(self, query, params=None):
        """Execute a single query with or without parameters."""
        read_only = query.strip().upper().startswith("SELECT")
        with self.get_connection(read_only=read_only) as connection:
            if connection:
                cursor = connection.cursor()
                try:
                    cursor.execute(query, params)
                    if read_only:
                        return 200
                    else:
                        latest_id = None
                        if query.strip().upper().startswith("INSERT"):
                            latest_id = cursor.lastrowid
                        connection.commit() 
                        if latest_id:
                            return 200, latest_id
                        else:
                            return 200
                except mysql.connector.Error as e:
                    print(f"Error at query: {query}")
                    print(f"Error execute_query: {e}")
                    if not read_only:
                        connection.rollback()
                    message = f"Error execute_query: {e}"
                    utils.betterstack_logtail(message)
                    raise Exception(message)
                finally:
                    cursor.close()

    def fetch_one(self, query, params=None):
        """Fetch a single record."""
        with self.get_connection(read_only=True) as connection:
            if connection:
                cursor = connection.cursor(dictionary=True)
                try:
                    cursor.execute(query, params)
                    return cursor.fetchone()
                except mysql.connector.Error as e:
                    print(f"Error at query: {query}")
                    message = f"Error fetch_one: {e}"
                    print(message)
                    utils.betterstack_logtail(message)
                    raise Exception(message)
                finally:
                    cursor.close()

    def fetch_all(self, query, params=None):
        """Fetch all records."""
        with self.get_connection(read_only=True) as connection:
            if connection:
                cursor = connection.cursor(dictionary=True)
                try:
                    cursor.execute(query, params)
                    return cursor.fetchall()
                except mysql.connector.Error as e:
                    print(f"Error at query: {query}")
                    message = f"Error fetch_all: {e}"
                    print(message)
                    utils.betterstack_logtail(message)
                    raise Exception(message)

                finally:
                    cursor.close()

    def close(self):
        # Since connections are managed within context managers, no explicit close method is necessary
        pass
