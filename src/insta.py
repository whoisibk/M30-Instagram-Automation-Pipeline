from os import getenv, path
from dotenv import load_dotenv

from instagrapi import Client
from instagrapi.types import Usertag, UserShort
from instagrapi.exceptions import LoginRequired, ChallengeRequired
from instagrapi.mixins.challenge import ChallengeChoice
from geopy.geocoders import Nominatim
import logging
import random
import imaplib
import email
import re
import time

from src.insta_security import change_password_handler, challenge_code_handler

logger = logging.getLogger()

load_dotenv()

USERNAME = getenv("IG_USERNAME")
PASSWORD = getenv("IG_PASSWORD")
SESSION_FILE = getenv("SESSION_FILE")
CHALLENGE_EMAIL = getenv("CHALLENGE_EMAIL")
CHALLENGE_PASSWORD = getenv("CHALLENGE_PASSWORD")


def login_user() -> Client:
    """
    Attempts to login to Instagram using either the provided session information
    or the provided username and password.
    """

    cl = Client()
    session = None

    if not USERNAME or not PASSWORD:
        raise Exception("Username and password must be set in .env file")
    
    # Register challenge handlers
    cl.change_password_handler = change_password_handler
    cl.challenge_code_handler = challenge_code_handler

    # Only try to load session if file exists
    if path.exists(SESSION_FILE):
        session = cl.load_settings(SESSION_FILE)

    login_via_session = False
    login_via_pw = False

    if session:
        try:
            cl.set_settings(session)
            cl.login(USERNAME, PASSWORD)

            # check if session is valid
            try:
                cl.get_timeline_feed()
            except LoginRequired:
                logger.info(
                    "Session is invalid, need to login via username and password"
                )

                old_session = cl.get_settings()

                # use the same device uuids across logins
                cl.set_settings({})
                cl.set_uuids(old_session["uuids"])

                cl.login(USERNAME, PASSWORD)
            login_via_session = True
        except ChallengeRequired as e:
            logger.error("Challenge required during session login: %s" % e)
            logger.error("Please complete the challenge manually at: https://www.instagram.com/")
        except Exception as e:
            logger.error("Couldn't login user using session information: %s" % e)

    if not login_via_session:
        try:
            logger.info(
                "Attempting to login via username and password. username: %s" % USERNAME
            )
            if cl.login(USERNAME, PASSWORD):
                login_via_pw = True
        except Exception as e:
            error_msg = str(e)
            
            # Check if it's the unknown STEP_NAME challenge
            if "Unknown step_name" in error_msg or "STEP_NAME" in error_msg:
                logger.error("=" * 80)
                logger.error("Instagram is blocking login with an unrecognized challenge.")
                logger.error("This requires MANUAL intervention:")
                logger.error("")
                logger.error("1. Go to https://www.instagram.com/")
                logger.error("2. Login with username: %s" % USERNAME)
                logger.error("3. Complete any challenges/verifications Instagram shows")
                logger.error("4. Once logged in successfully on web, DELETE this file:")
                logger.error("   %s" % SESSION_FILE)
                logger.error("5. Run this script again")
                logger.error("=" * 80)
                raise Exception("Instagram challenge required - complete manually on web browser")
            
            logger.error("Couldn't login user using username and password: %s" % e)
            raise  # Re-raise to see the full error

    if not login_via_pw and not login_via_session:
        raise Exception("Couldn't login user with either password or session")

    # Save session after successful login
    cl.dump_settings(SESSION_FILE)
    logger.info("Session saved to %s" % SESSION_FILE)

    return cl


def post_album(
    client: Client, image_paths: list, caption: str, username: str, location_str: str
) -> bool:
    """
    Posts an album with multiple images to Instagram.

    Args:
        client: Instagram API client
        image_paths: List of Path objects to images
        caption: Post caption
        username: Instagram username of the person
        location_str: Location string in format "City, Country"

    Returns:
        bool: True if post was successful, False otherwise
    """
    try:
        city = location_str.split(",")

        lat, lng = get_lat_lng(city)

        # Search for location on Instagram
        location = None
        try:
            locations = client.location_search(lat=lat, lng=lng)
            if locations:
                location = locations[0]
                logger.info(
                    f"Found Instagram location for {city}: {location.name} (pk={location.pk})"
                )
            else:
                logger.warning(
                    f"No Instagram location found for coordinates {lat}, {lng}"
                )
        except Exception as e:
            logger.warning(f"Could not find location '{city}' on Instagram: {e}")

        tags = []
        try:
            # tag the user in the post
            user = client.user_info_by_username(username)
            user_short = UserShort(pk=user.pk, username=user.username)
            tags = [Usertag(user=user_short, x=0.5, y=0.5)]
            logger.info(f"Tagged @{username} in the post")

        except Exception as e:
            logger.warning(f"Could not tag @{username}: {e}")

        # Upload album
        upload_kwargs = {
            "paths": image_paths,
            "caption": caption,
        }
        if tags:
            upload_kwargs["usertags"] = tags
        if location:
            upload_kwargs["location"] = location

        media = client.album_upload(**upload_kwargs)

        logger.info(f"Successfully posted album for @{username}. Media ID: {media.pk}")
        return True

    except Exception as e:
        logger.error(f"Failed to post album for @{username}: {str(e)}")
        return False


def get_lat_lng(location_str: str) -> tuple:
    """Gets the latitude and longitude for a given location string using geopy."""

    geolocator = Nominatim(user_agent="insta_bot")
    location = geolocator.geocode(location_str)
    if location:
        return location.latitude, location.longitude
    else:
        raise Exception("Could not geocode location")
