import requests
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def authenticate_and_send_email():
    """
    Authenticate with Plextrac API, search for specific emails, and send an email notification.

    Reads configuration from 'config.json' for Plextrac API credentials and Gmail SMTP details.
    Searches for users based on specific email criteria specified in 'customer_domains' key in config.
    Sends an email listing non-compliant users to a specified recipient using Gmail SMTP.

    Raises:
        requests.exceptions.RequestException: If an error occurs during API requests.
        smtplib.SMTPException: If an error occurs during SMTP operations.

    Notes:
        - Ensure 'config.json' contains 'plextrac_username', 'plextrac_password', 'plextrac_url',
          'gmail_username', 'gmail_app_password', and 'customer_domains' fields.
        - Use TLS (port 587) for SMTP as SSL (port 465) is deprecated.
        - Specify customer email domains in 'customer_domains' key in config.json.
    """
    # Load configuration from config.json
    with open('config.json') as config_file:
        config = json.load(config_file)

    # Authenticate with Plextrac API
    data = {
        "username": config['plextrac_username'],
        "password": config['plextrac_password']
    }
    r = requests.post(
        url=f"{config['plextrac_url']}/api/v1/authenticate",
        json=data,
        timeout=10  # Add timeout
    )
    r.raise_for_status()  # Raise exception for bad response status

    # Set authorization headers for subsequent requests
    headers = {
        "Authorization": f"Bearer {r.json()['token']}"
    }

    # Define function to search for specific emails in JSON data
    def search_emails_in_data(json_obj):
        search_terms = config['customer_domains']  # Read domains from config
        matches = []

        if isinstance(json_obj, dict) and 'data' in json_obj and isinstance(json_obj['data'], list):
            for item in json_obj['data']:
                if isinstance(item, dict) and 'email' in item:
                    email = item['email']
                    if any(term in email for term in search_terms):
                        matches.append(item)
        return matches

    # Retrieve users from Plextrac API based on authenticated session
    user_endpoint = requests.get(
        url=f"{config['plextrac_url']}/api/v2/tenants/{r.json()['tenant_id']}/users",
        params={'limit': 100},
        headers=headers,
        timeout=10  # Add timeout
    )
    user_endpoint.raise_for_status()  # Raise exception for bad response status
    user = user_endpoint.json()

    # Search for users matching specified criteria
    customer_users = search_emails_in_data(user)

    # Prepare SMTP server details for Gmail
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587  # TLS port (SSL is deprecated and should not be used)

    # Sender email credentials
    sender_email = config['gmail_username']
    sender_password = config['gmail_app_password']  # Your Gmail account password or an app-specific password

    # Recipient email address
    recipient_email = "user@example.com"  # Replace with the recipient's email address

    # Prepare the email subject
    subject = "MFA Non-compliant Users"

    # Construct the email body with user information
    body = f"The following users are not compliant with the {config['customer']}" \ 
           f"requirement for MFA enabled on the Plextrac " \
           "Platform:\n\n"
    for user in customer_users:
        if not user['mfa']['enabled']:
            body += f"Name: {user['fullName']}\nEmail: {user['email']}\n\n"

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject

    # Add body to email
    message.attach(MIMEText(body, 'plain'))

    try:
        # Establish a SMTP connection to Gmail's server
        smtp = smtplib.SMTP(smtp_server, smtp_port)

        # Start TLS encryption
        smtp.starttls()

        # Login to Gmail SMTP server
        smtp.login(sender_email, sender_password)

        # Send email
        smtp.sendmail(sender_email, recipient_email, message.as_string())
        print(f"Email sent successfully to {recipient_email}")

    except (requests.exceptions.RequestException, smtplib.SMTPException) as e:
        print(f"Error sending email: {e}")

    finally:
        # Close the SMTP connection
        smtp.quit()


if __name__ == "__main__":
    authenticate_and_send_email()
