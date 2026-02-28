from src.sheets import logger, fetch_rows, process_form_row
from src.insta import login_user


def main():
    """
    Main pipeline function that loops through form responses and processes them.
    Limits the number of posts per run to avoid continuous looping.
    """
    MAX_POSTS_PER_RUN = 1

    logger.info("Starting Instagram Post processing pipeline")
    print(f"Starting Instagram Post Pipeline (Max {MAX_POSTS_PER_RUN} posts per run)")

    # Login to Instagram
    try:
        insta_client = login_user()
        logger.info("Successfully logged in to Instagram")
        print("✓ Instagram login successful\n")

    except Exception as e:
        logger.error(f"Failed to login to Instagram: {str(e)}")
        print(f"✗ Instagram login failed: {str(e)}")
        return

    # Fetch all rows from Google Sheets
    all_rows = fetch_rows()
    headers = all_rows[0]
    data_rows = all_rows[1:]

    posts_made = 0

    # Loop through each response and process it
    for row in data_rows:
        if posts_made >= MAX_POSTS_PER_RUN:
            logger.info(f"Reached max posts per run ({MAX_POSTS_PER_RUN})")
            print(f"\nReached max posts per run limit ({MAX_POSTS_PER_RUN})")
            break

        row_dict = dict(zip(headers, row))

        if process_form_row(row_dict, insta_client):
            posts_made += 1

    logger.info(f"Pipeline completed. Posts made: {posts_made}")
    print(f"\nPipeline completed. Total posts made: {posts_made}")


if __name__ == "__main__":
    main()
