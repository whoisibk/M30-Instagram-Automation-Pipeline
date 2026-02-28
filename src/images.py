import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import cv2


def handle_user_images(row_dict):
    """Handles user images by downloading, editing, and saving them."""
    # username = row_dict["Instagram username"]

    # a baby picture and a recent picture
    image_url_1, image_url_2 = row_dict["Photo_url"].split(",")
    country = row_dict["Country"].split(",")[1]
    first_name, last_name = row_dict["Full_name"].split(" ")

    # create folder for each user
    raw_path, edited_path = create_user_image_folder(first_name)

    file_id_1 = extract_file_id(image_url_1)
    file_id_2 = extract_file_id(image_url_2)

    # build publicly downloadable image using Google Drive url
    download_url_1 = build_download_url(file_id_1)
    download_url_2 = build_download_url(file_id_2)

    raw_image_1_path = raw_path / f"{file_id_1}.jpg"
    raw_image_2_path = raw_path / f"{file_id_2}.jpg"

    # file locations for edited images
    edited_image_1_path = edited_path / "baby_edited.jpg"
    edited_image_2_path = edited_path / "recent_edited.jpg"

    # downloading raw image from google drive
    download_image(download_url_1, raw_image_1_path)
    download_image(download_url_2, raw_image_2_path)

    # editing the image - pass first_name and last_name separately
    edit_image(raw_image_1_path, edited_image_1_path, first_name, last_name, country)
    edit_image(raw_image_2_path, edited_image_2_path, first_name, last_name, country)

    return edited_image_1_path, edited_image_2_path


def extract_file_id(image_url):
    return image_url.split("=")[-1]


def build_download_url(file_id):
    """Builds a download URL from a Google Drive file ID."""
    return f"https://drive.google.com/uc?export=download&id={file_id}"


def download_image(download_url, save_path):
    """Downloads an image from a given URL and saves it to a local file."""
    response = requests.get(download_url)
    if response.status_code != 200:
        raise Exception(
            f"Failed to download image from {download_url}: {response.text}"
        )

    with open(save_path, "wb") as file:
        file.write(response.content)


def create_user_image_folder(username):
    """Creates a folder for storing user images in the "images" directory."""
    base_path = Path("images") / username
    raw_path = base_path / "raw"
    edited_path = base_path / "edited"

    raw_path.mkdir(parents=True, exist_ok=True)
    edited_path.mkdir(parents=True, exist_ok=True)

    return raw_path, edited_path


# Layout constants for image placement inside the border
BORDER_INSET = 65  # Distance from edge to start of content area
CONTENT_PADDING = 15  # Additional padding inside the border
TEXT_TO_IMAGE_GAP = 20  # Gap between name text and image
COUNTRY_HANDLE_GAP = 8  # Gap between country and handle text

# Text styling constants
TEXT_COLOR = (255, 255, 255)  # White text
NAME_FONT_SIZE = 50
COUNTRY_FONT_SIZE = 45
HANDLE_FONT_SIZE = 14


def get_optimal_name_display(first_name, last_name, font, max_width):
    """
    Intelligently selects between full name and first name based on rendered pixel width.

    Args:
        first_name: Student's first name
        last_name: Student's last name
        font: PIL ImageFont object to measure against
        max_width: Maximum allowed width in pixels

    Returns:
        The name to display (full name if it fits, otherwise first name)
    """
    full_name = f"{first_name} {last_name}".title()
    first_only = first_name.title()

    # Measure full name width using getbbox
    bbox = font.getbbox(full_name)
    full_name_width = bbox[2] - bbox[0]

    # If full name fits, use it; otherwise fall back to first name
    if full_name_width <= max_width:
        return full_name
    else:
        return first_only


def intelligently_crop_to_square(image_path):
    """
    Intelligently crops an image to square format while keeping the person centered.
    Uses face detection to find the person and crops around them.
    Falls back to center crop if no face is detected.
    """
    # Read image with OpenCV
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Could not read image from {image_path}")

    height, width = img.shape[:2]

    # Determine target square size (smaller dimension)
    target_size = min(width, height)

    # Load face cascade for detecting person
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(img, 1.1, 4)

    if len(faces) > 0:
        # Get the largest face detected
        largest_face = max(faces, key=lambda f: f[2] * f[3])
        fx, fy, fw, fh = largest_face

        # Calculate center of the face
        face_center_x = fx + fw // 2
        face_center_y = fy + fh // 2

        # Calculate crop box centered on the face
        left = max(0, face_center_x - target_size // 2)
        top = max(0, face_center_y - target_size // 2)

        # Adjust if crop box goes out of bounds
        if left + target_size > width:
            left = width - target_size
        if top + target_size > height:
            top = height - target_size

        left = max(0, left)
        top = max(0, top)
    else:
        # Fallback: center crop if no face detected
        left = (width - target_size) // 2
        top = (height - target_size) // 2

    # Crop the image
    cropped = img[top : top + target_size, left : left + target_size]

    # Convert back to PIL Image
    cropped_pil = Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))

    return cropped_pil


def edit_image(input_path, output_path, first_name, last_name, country):
    """
    Edits an image by:
    1. Intelligently cropping to square format
    2. Resizing to fit the layout box within borders
    3. Adding styled text overlays (name, country, minerva tag)

    Uses intelligent name selection: full name if it fits, otherwise first name only.
    """
    background = Image.open("images/background.png").convert("RGBA")
    bg_w, bg_h = background.size

    user_img = intelligently_crop_to_square(input_path)

    # Add styled text overlays first to calculate proper spacing
    draw = ImageDraw.Draw(background)

    name_font = ImageFont.truetype(
        "utils\\Playfair_Display\\static\\PlayfairDisplay-ExtraBold.ttf", NAME_FONT_SIZE
    )
    country_font = ImageFont.truetype(
        "utils\\Playfair_Display\\static\\PlayfairDisplay-ExtraBold.ttf",
        COUNTRY_FONT_SIZE,
    )
    handle_font = ImageFont.truetype(
        "utils\\Montserrat\\static\\Montserrat-ExtraLight.ttf", HANDLE_FONT_SIZE
    )

    # Maximum allowed width for name (80% of available content width for visual balance)
    content_left = BORDER_INSET + CONTENT_PADDING
    content_right = bg_w - BORDER_INSET - CONTENT_PADDING
    available_width = content_right - content_left
    MAX_NAME_WIDTH = int(available_width * 0.8)  # 80% of available width

    # Intelligently select between full name and first name
    name_text = get_optimal_name_display(
        first_name, last_name, name_font, MAX_NAME_WIDTH
    )
    handle_text = "@minervauni2030"

    # Calculate text dimensions
    name_bbox = draw.textbbox((0, 0), name_text, font=name_font)
    country_bbox = draw.textbbox((0, 0), country, font=country_font)
    handle_bbox = draw.textbbox((0, 0), handle_text, font=handle_font)

    name_h = name_bbox[3] - name_bbox[1]
    country_h = country_bbox[3] - country_bbox[1]
    handle_h = handle_bbox[3] - handle_bbox[1]

    # Calculate content area inside border
    content_right = bg_w - BORDER_INSET - CONTENT_PADDING
    content_top = BORDER_INSET + CONTENT_PADDING
    content_bottom = bg_h - BORDER_INSET - CONTENT_PADDING

    # Calculate available space for image
    # Top: content_top + name height + gap
    # Bottom: content_bottom - country height - gap - handle height - gap
    image_top = content_top + name_h + TEXT_TO_IMAGE_GAP
    image_bottom = (
        content_bottom - country_h - COUNTRY_HANDLE_GAP - handle_h - TEXT_TO_IMAGE_GAP
    )

    image_area_width = content_right - content_left
    image_area_height = image_bottom - image_top

    # Resize user image to fit within available space (maintain aspect ratio)
    user_img.thumbnail(
        (int(image_area_width), int(image_area_height)), Image.Resampling.LANCZOS
    )

    # Convert to RGBA for overlaying
    if user_img.mode != "RGBA":
        user_img = user_img.convert("RGBA")

    # Center the image within the available space
    x = content_left + (image_area_width - user_img.width) // 2
    y = image_top + (image_area_height - user_img.height) // 2
    background.paste(user_img, (int(x), int(y)), user_img)

    # Get image center x for text alignment
    center_x = bg_w // 2

    # Position text elements inside border

    # Name at top (just below border)
    name_y = content_top + name_h // 2
    draw.text(
        (center_x, name_y), name_text, font=name_font, anchor="mm", fill=TEXT_COLOR
    )

    # Country near bottom
    country_y = content_bottom - handle_h - COUNTRY_HANDLE_GAP - country_h // 2
    draw.text(
        (center_x, country_y), country, font=country_font, anchor="mm", fill=TEXT_COLOR
    )

    # Minerva handle at very bottom (just above border)
    handle_y = content_bottom - handle_h // 2
    draw.text(
        (center_x, handle_y),
        handle_text,
        font=handle_font,
        anchor="mm",
        fill=TEXT_COLOR,
    )

    # Convert to RGB and save
    background = background.convert("RGB")
    background.save(output_path)


if __name__ == "__main__":
    test_row = {
        "First Name": "Leonardo",
        "Instagram username": "barry_allen",
        "Photo_url": "https://drive.google.com/open?id=1WKho9PCTLPEZuNLVvjR0cZ34P2hlaH1F, https://drive.google.com/open?id=1G-6DbC8c9qGNtO5Jhji5IDGoM6KgLo4K",
        "Country": "Paris, France",
    }
    handle_user_images(test_row)
