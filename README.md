# Plextrac MFA Compliance Notification Script

This script interacts with the Plextrac API to identify users who are not compliant with MFA (Multi-Factor Authentication) requirements based on specified customer email domains. It then sends an email notification to alert about non-compliant users using Gmail SMTP.

### Requirements

    Python 3.x
    Requests library (pip install requests)
    Gmail account for sending emails

### Setup

    Clone the Repository:
    git clone https://github.com/yourusername/plextrac-mfa-compliance.git
    cd plextrac-mfa-compliance

    Install Dependencies:
    pip install -r requirements.txt

    Configuration:

        Create a config.json file in the root directory with the following structure:

        {
        "plextrac_username": "your_plextrac_username",
        "plextrac_password": "your_plextrac_password",
        "plextrac_url": "https://example.plextrac.com",
        "gmail_username": "your_gmail_username",
        "gmail_app_password": "your_gmail_app_password",
        "customer_domains": ["example.com", "example.org"]
        }
            Replace your_plextrac_username, your_plextrac_password, and https://example.plextrac.com with your actual Plextrac API credentials and URL.
            Replace your_gmail_username and your_gmail_app_password with your Gmail account credentials or an app-specific password.
            Add the domains of your customers whose users you want to monitor for MFA compliance in the customer_domains list.

    Run the Script:
    python plextrac_mfa_notification.py

    Automation:
        To automate the script to run weekly, configure a cron job on Linux or a scheduled task on Windows to execute the script at your desired frequency (e.g., every Friday at 8 AM EST).

### Functionality

    Authentication: The script authenticates with the Plextrac API using credentials provided in config.json.
    User Search: It searches for users within specified customer domains (defined in customer_domains list in config.json) who are not compliant with MFA requirements.
    Email Notification: Sends an email notification using Gmail SMTP to inform about non-compliant users, listing their names and email addresses.

### Notes

    Ensure that the configuration (config.json) is correctly set up before running the script.
    Use TLS (port 587) for SMTP connections as SSL (port 465) is deprecated.
    Modify the cron job or scheduled task configuration based on your operating system (Linux or Windows) for automated execution.