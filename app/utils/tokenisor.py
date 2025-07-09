import math
from io import BytesIO
from typing import Union

import tiktoken
from PIL import Image


# o200k_base	• GPT-4o models (gpt-4o)
# cl100k_base	• GPT-4 models (gpt-4)
# • GPT-3.5 Turbo models (gpt-3.5-turbo)
# • GPT Base models (davinci-002, babbage-002)
# • Embeddings models (text-embedding-ada-002, text-embedding-3-large, text-embedding-3-small)
# • Fine-tuned models (ft:gpt-4, ft:gpt-3.5-turbo, ft:davinci-002, ft:babbage-002)

def num_tokens_from_string(string: str, encoding_name: str = "o200k_base") -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def calculate_image_tokens(image_path: Union[str, BytesIO], detail: str = "high") -> int:
    """
    Calculate tokens for an image based on its size and detail level.

    Args:
        image_path: Path to the local image file
        detail: "high" or "low" detail level

    Returns:
        int: Number of tokens required
    """
    if detail.lower() == "low":
        return 85

    try:
        # Open and get image dimensions
        with Image.open(image_path) as img:
            width, height = img.size

        # Scale down if larger than 2048 in any dimension
        if width > 2048 or height > 2048:
            ratio = 2048 / max(width, height)
            width = int(width * ratio)
            height = int(height * ratio)

        # Scale such that shortest side is 768px
        ratio = 768 / min(width, height)
        final_width = int(width * ratio)
        final_height = int(height * ratio)

        # Calculate number of 512px tiles needed
        tiles_width = math.ceil(final_width / 512)
        tiles_height = math.ceil(final_height / 512)
        total_tiles = tiles_width * tiles_height

        # Calculate total tokens
        tokens = (total_tiles * 170) + 85

        return tokens

    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")