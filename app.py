
from flask import Flask
from db.mysql_component import MySQLConnector
from flask_cors import CORS
from core.routes import routes 
from dotenv import load_dotenv
# from werkzeug.middleware.proxy_fix import ProxyFix  # Uncomment if using ProxyFix

import sentry_sdk
import os


load_dotenv(".env",override=True)

sentry_sdk.init(
    dsn="", #inserthere
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=0.5,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

app = Flask(__name__)
app.register_blueprint(routes)
CORS(app)

# Space (S3) configuration from environment variables
# You can now use these variables (space_access_id, etc.) as needed
# for initializing services like boto3 for DigitalOcean Spaces, AWS S3, etc.

db_user = os.getenv("USER")
db_password = os.getenv("PASSWORD")
db_host = os.getenv("HOST")
db_host_ro = os.getenv("HOST_READONLY")
db_db = os.getenv("DATABASE")
db_port = os.getenv("PORT")
db_api_password = os.getenv("API_PASSWD")

space_access_id = os.getenv("FLASK_SPACES_ACCESS_ID")
space_secret_key = os.getenv("FLASK_SPACES_SECRET_KEY")
space_server = os.getenv("FLASK_SPACES_SERVER_TYPE")
space_region_name = os.getenv("FLASK_SPACES_REGION_NAME")
space_endpoint_url = os.getenv("FLASK_SPACES_ENDPOINT_URL")

mail_debug = os.getenv("FLASK_MAIL_DEBUG")
mail_server = os.getenv("FLASK_MAIL_SERVER")
mail_port = os.getenv("FLASK_MAIL_PORT")
mail_tls = os.getenv("FLASK_MAIL_USE_TLS") == 'True'
mail_ssl = os.getenv("FLASK_MAIL_USE_SSL") == 'True'
mail_username = os.getenv("FLASK_MAIL_USERNAME")
mail_password = os.getenv("FLASK_MAIL_PASSWORD")
mail_claims_username = os.getenv("FLASK_CLAIMS_MAIL_USERNAME")
mail_sender = os.getenv("FLASK_MAIL_SENDER")

personal_mail = os.getenv("FLASK_PERSONAL_EMAIL")
mailersend_api_token = os.getenv("FLASK_MAILERSEND_API_TOKEN")

sentry = os.getenv("FLASK_SENTRY")

app.config.update(
    DEBUG=True,
    DB_USER = db_user,
    DB_PASSWORD = db_password,
    DB_HOST = db_host,
    DB_HOST_RO = db_host_ro,
    DB_DB = db_db,
    DB_PORT = db_port,
    DB_API_PASSWORD = db_api_password,
    MAIL_SERVER=mail_server,
    MAIL_PORT=mail_port,
    MAIL_USE_TLS=mail_tls,
    MAIL_USE_SSL=mail_ssl,
    MAIL_USERNAME=mail_username,
    MAIL_PASSWORD=mail_password,
    MAIL_SENDER = mail_sender,
    SPACE_ACCESS_ID = space_access_id,
    SPACE_SECRET_KEY = space_secret_key,
    SPACE_SERVER = space_server,
    SPACE_REGION_NAME = space_region_name,
    SPACE_ENDPOINT_URL = space_endpoint_url,
    SENTRY = sentry,
    PERSONAL_MAIL = personal_mail,
    MAILERSEND_API_TOKEN = mailersend_api_token
    
)

# (Optional) Use ProxyFix if necessary
# app.wsgi_app = ProxyFix(
#     app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
# )

# Initialize MySQL connection
db = MySQLConnector(app)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)
