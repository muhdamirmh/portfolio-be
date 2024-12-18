from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, render_template, jsonify, g
from email.message import EmailMessage
from io import BytesIO
from datetime import datetime


import requests, json, random, string, boto3, os, smtplib, pdfkit, mimetypes, sentry_sdk, qrcode
import secrets


def generate_session_id():
    return secrets.token_hex(32)  # Generates a 64-character hex token

def generate_client_id(length=64):
    # Define the character set
    char_set = string.ascii_uppercase + string.digits + "!@#$%&*~-"
    # Generate a random session ID
    return ''.join(random.choices(char_set, k=length))

def set_db(client):

    from db.mysql_component import MySQLConnector

    if client == "1":
        db = MySQLConnector()
    elif client == "2":
        db = MySQLConnector(database="2")

    return db


def betterstack_logtail(message):

    url = ""  # inserthere

    payload = json.dumps({"dt": "$(date -u +'%Y-%m-%d %T UTC')", "message": message})
    headers = {"Content-Type": "application/json", "Authorization": ""}

    response = requests.request("POST", url, headers=headers, data=payload)
    if response:
        print("Successfully ping Better Stack!"), 200
    else:
        print("Failed to ping Better Stack!"), 400


def send_error(def_name, error):
    message = f"{def_name}(): {str(error)}"
    sentry_sdk.capture_exception(error)
    betterstack_logtail(message)
    return jsonify({"message": message}), 400


def generate_random_code(length):
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string


def hash_and_salt_password(password):
    """
    Hashes and salts a password using werkzeug's generate_password_hash.

    Args:
        password (str): The plain-text password to hash.

    Returns:
        str: The hashed and salted password.
    """
    # Generate a password hash with a salt
    hashed_password = generate_password_hash(password)
    return hashed_password


def verify_password(hashed_password, password):
    """
    Verifies that a given password matches the hashed and salted password.

    Args:
        hashed_password (str): The hashed and salted password.
        password (str): The plain-text password to verify.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    return check_password_hash(hashed_password, password)


def upload_file(file_path, file, file_local_path):
    try:
        
        file_name = file.filename

        # Initiate session with the storage service (DigitalOcean Spaces or AWS S3)
        session = boto3.session.Session()
        client = session.client(
            service_name=current_app.config["SPACE_SERVER"],
            region_name=current_app.config["SPACE_REGION_NAME"],
            endpoint_url=current_app.config["SPACE_ENDPOINT_URL"],
            aws_access_key_id=current_app.config["SPACE_ACCESS_ID"],
            aws_secret_access_key=current_app.config["SPACE_SECRET_KEY"],
        )

        # Determine the file's true content type using the mimetypes library
        content_type, _ = mimetypes.guess_type(file_name)
        if not content_type:
            return {"result": "Invalid file type: Content type could not be determined"}

        # Full file path in the storage (e.g., bucket)
        full_file_path = file_path + file_name
        online_file_path = (
            "https://dpp-object-space.sgp1.digitaloceanspaces.com/" + full_file_path
        )

        # Upload the file to the storage
        client.upload_file(
            file_local_path,  # Local filename
            "dpp-object-space",  # Bucket name
            full_file_path,  # Destination path in the storage
            ExtraArgs={"ContentType": content_type},
        )

        # Set public-read ACL to make the file accessible
        client.put_object_acl(
            ACL="public-read", Bucket="dpp-object-space", Key=full_file_path
        )

        return {
            "result": "File uploaded successfully",
            "file_url": online_file_path,
        }, 200

    except Exception as e:
        return {"error": str(e)}, 502

    finally:
        if os.path.exists(file_local_path):
            os.remove(file_local_path)


def generate_pdf_from_template(template, payload, pdf_filename):
    # Render the HTML template with the provided payload data
    rendered_template = render_template(template, data=payload)

    # Configure pdfkit with path to wkhtmltopdf
    configpdfkit = pdfkit.configuration(wkhtmltopdf="/usr/bin/wkhtmltopdf")
    pdfkit_options = {
        "enable-local-file-access": "",
        "no-stop-slow-scripts": "",
    }

    # Generate PDF from the rendered HTML and save it to the specified file
    pdf_data = pdfkit.from_string(
        rendered_template, False, configuration=configpdfkit, options=pdfkit_options
    )

    with open(pdf_filename, "wb") as file:
        file.write(pdf_data)

    return pdf_data


def send_email(
    template, user_email, subject, payload=None, pdf_file=None, pdf_filename=None
):

    mail_sender =  current_app.config["MAIL_SENDER"]
    mail_username = current_app.config["MAIL_USERNAME"]
    mail_password = current_app.config["MAIL_PASSWORD"]
    mail_server = current_app.config["MAIL_SERVER"]
    mail_port = current_app.config["MAIL_PORT"]
    mail_use_tls = current_app.config["MAIL_USE_TLS"]

    if payload != None:
        rendered_template = render_template(template, data=payload)
    else:
        rendered_template = render_template(template)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = mail_sender
    msg["To"] = user_email

    msg.add_alternative(rendered_template, subtype="html")

    if pdf_file != None:
        msg.add_attachment(
            pdf_file,
            maintype="application",
            subtype="pdf",
            filename=pdf_filename,
        )

    try:
        print("Attempting to send the email to customer")

        if mail_use_tls == True:
            server = smtplib.SMTP(mail_server, mail_port)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(mail_server, mail_port)

        print("SMTP is initialized")

        server.login(mail_username, mail_password)
        print("Login to server")
        server.send_message(msg)
        print("Email has been sent to customer")
        server.quit()
        print("Server has quit")

        return "Successfully sent the email", 200
    except Exception as e:
        return str(e), 500
    finally:
        # Clean up the PDF file
        if pdf_filename != None:
            if os.path.exists(pdf_filename):
                os.remove(pdf_filename)


def generate_voucher_code(voucher_type=1, length=10):

    if length < 10:
        raise ValueError(
            "Length must be at least 10 to accommodate prefix and required characters."
        )

    code_body = "".join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=length - (2 if voucher_type == 2 else 0),
        )
    )

    # Apply prefix for Type 2 (Failed devices)
    if voucher_type == 2:
        return "50" + code_body[: length - 2]  # Limit to 8 characters after prefix
    else:
        return code_body[
            :length
        ]  # Return full 10 characters for Type 1 (Passed devices)


def generate_qr_code(data):

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    img = img.resize((1000, 1000))

    # Save QR code to a BytesIO object
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer
