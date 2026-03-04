

from os import getenv
from dotenv import load_dotenv

import random
import imaplib
import email
import re
import time
from logging import getLogger

from instagrapi.mixins.challenge import ChallengeChoice


load_dotenv()

logger = getLogger()   
CHALLENGE_EMAIL = getenv("CHALLENGE_EMAIL")
CHALLENGE_PASSWORD = getenv("CHALLENGE_PASSWORD")


def change_password_handler(username):
    """
    Generates a random password when Instagram challenges for a password change.
    
    Args:
        username: Instagram username
        
    Returns:
        str: New randomly generated password
    """
    chars = list("abcdefghijklmnopqrstuvwxyz1234567890!&£@#")
    password = "".join(random.sample(chars, 8))
    logger.info(f"Generated new password for {username}: {password}")
    return password


def get_code_from_email(username):
    """
    Retrieves the 6-digit verification code from Gmail inbox using IMAP.
    
    Args:
        username: Instagram username to search for in email
        
    Returns:
        str: 6-digit verification code or False if not found
    """
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(CHALLENGE_EMAIL, CHALLENGE_PASSWORD)
        mail.select("inbox")
        result, data = mail.search(None, "(UNSEEN)")
        
        if result != "OK":
            logger.error(f"Error searching emails: {result}")
            return False
        
        ids = data.pop().split()
        
        for num in reversed(ids):
            mail.store(num, "+FLAGS", "\\Seen")  # mark as read
            result, data = mail.fetch(num, "(RFC822)")
            
            if result != "OK":
                logger.error(f"Error fetching email: {result}")
                continue
            
            msg = email.message_from_bytes(data[0][1])
            payloads = msg.get_payload()
            
            if not isinstance(payloads, list):
                payloads = [msg]
            
            code = None
            
            for payload in payloads:
                try:
                    body = payload.get_payload(decode=True).decode()
                except Exception as e:
                    logger.warning(f"Could not decode payload: {e}")
                    continue
                
                if "<div" not in body:
                    continue
                
                match = re.search(">([^>]*?({u})[^<]*?)<".format(u=username), body)
                if not match:
                    continue
                
                logger.info(f"Match from email: {match.group(1)}")
                match = re.search(r">(\d{6})<", body)
                
                if not match:
                    logger.info('Skipping email, code not found')
                    continue
                
                code = match.group(1)
                if code:
                    logger.info(f"Successfully extracted code: {code}")
                    mail.close()
                    mail.logout()
                    return code
        
        mail.close()
        mail.logout()
        return False
        
    except Exception as e:
        logger.error(f"Error getting code from email: {e}")
        return False


def challenge_code_handler(username, choice):
    """
    Handles Instagram challenge code verification.
    Currently supports EMAIL verification via Gmail IMAP.
    
    Args:
        username: Instagram username
        choice: ChallengeChoice enum (SMS or EMAIL)
        
    Returns:
        str: Verification code or False if unable to retrieve
    """
    if choice == ChallengeChoice.SMS:
        logger.warning("SMS verification not implemented, returning False")
        return False
    elif choice == ChallengeChoice.EMAIL:
        return get_code_from_email(username)
    return False
