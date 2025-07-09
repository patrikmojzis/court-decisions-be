import base64
import mimetypes
import os
from io import BytesIO

import requests
from PIL import Image
from flask import request

from app.exceptions.app_exception import AppException

image_extensions = ['png', 'jpg', 'jpeg']
document_extensions = ['pdf', 'doc', 'docx', 'pptx']
allowed_extensions = image_extensions + document_extensions
max_content_length = int(os.getenv("MAX_UPLOAD_MB", 50)) * 1024 * 1024  # 50 MB
public_dir = os.path.join(os.getcwd(), 'public')
thumbnails_dir = os.path.join(public_dir, 'thumbnails')
temp_dir = os.path.join(public_dir, 'temp')

if not os.path.exists(public_dir):
    os.makedirs(public_dir)

if not os.path.exists(thumbnails_dir):
    os.makedirs(thumbnails_dir)

if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)


def download_image_from_url(url: str, filename: str):
    response = requests.get(url)

    if response.status_code == 200:
        save_file(response.content, filename)
    else:
        raise AppException(f"Failed to download image. Status code: {response.status_code}")


def get_image_format(image_bytes):
    with Image.open(BytesIO(image_bytes)) as img:
        return img.format.lower()


def save_file(content, filename):
    # Define the path to the 'temp' directory
    # save_dir = os.path.join(os.getcwd(), 'public')

    # Define the full path to the file
    path = os.path.join(public_dir, filename)
    with open(path, "wb") as f:
        f.write(content)

    return path


def delete_file(filename):
    # Define the path to the 'temp' directory
    # temp_dir = os.path.join(os.getcwd(), 'public')

    # Define the full path to the file
    path = os.path.join(public_dir, filename)

    # Delete the file
    os.remove(path)


def allowed_file(filename):
    return '.' in filename and get_file_extension(filename) in allowed_extensions and \
        len(filename) <= 255 and request.content_length <= max_content_length


def is_image_file(filename):
    return get_file_extension(filename) in image_extensions


def is_document_file(filename):
    return get_file_extension(filename) in document_extensions


def get_file_extension(filename):
    """
    Get the file extension from a filename.

    Parameters:
    filename (str): The name of the file.

    Returns:
    str: The file extension.
    """
    _, extension = os.path.splitext(filename)
    return extension.lstrip('.').lower()


def image_to_base64(filepath: str):
    # Get the MIME type of the file
    mime_type = mimetypes.guess_type(filepath)[0]
    if not mime_type:
        mime_type = 'image/jpeg'  # default to jpeg if type cannot be determined

    # Read and encode the image
    with open(filepath, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')

    # Return with the correct data URI format
    return f"data:{mime_type};base64,{base64_image}"