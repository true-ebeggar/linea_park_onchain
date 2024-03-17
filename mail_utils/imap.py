import re
import imaplib
import email
from email.header import decode_header

from linea_park_onchain.config import *


def read_inbox_and_find_code(mail, imap_password, logger, subject_filter):

    # subject_filter = 'Pictographs - verify code'

    def _get_email_body(email_message):
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == 'text/plain':
                    return part.get_payload(decode=True).decode()
        else:
            return email_message.get_payload(decode=True).decode()

    def _find_verification_code(email_content):
        pattern = r"\b\d{6}\b"
        match = re.search(pattern, email_content)
        return match.group(0) if match else None

    try:
        connection = imaplib.IMAP4_SSL(IMAP_SERVER_LINK)
        connection.login(mail, imap_password)
        logger.info("Logged into email account.")

        connection.select('inbox')
        status, messages = connection.search(None, 'ALL')
        if status != 'OK':
            logger.warning("No messages found!")
            return None

        messages = messages[0].split()
        latest_email_date = None
        latest_email_content = None

        for mail_id in messages[::-1]:
            status, data = connection.fetch(mail_id, '(RFC822)')
            if status != 'OK':
                logger.error(f"Error reading message {mail_id}")
                continue

            email_message = email.message_from_bytes(data[0][1])
            # Pls ignore "error" above, its don`t affect execution
            subject, encoding = decode_header(email_message['Subject'])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or 'utf-8')

            if subject_filter in subject:
                email_date = email.utils.parsedate_to_datetime(email_message['Date'])
                # Pls ignore "error" above, its don`t affect execution
                if latest_email_date is None or email_date > latest_email_date:
                    latest_email_date = email_date
                    latest_email_content = _get_email_body(email_message)

        code = _find_verification_code(latest_email_content) if latest_email_content else None
        if code:
            logger.info(f"Verification code found: {code}")
        else:
            logger.warning("No verification code found.")

        connection.close()
        connection.logout()
        return code
    except Exception as e:
        logger.error(f"An error occurred: {e}")