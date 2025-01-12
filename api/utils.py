def get_credit_card_unique_name(url: str) -> str:
    """Takes a URL and returns the last part of the URL after the last '/'.

    Args:
        url (str): The input URL.

    Returns:
        str: The last part of the URL.
    """
    return url.rstrip('/').split('/')[-1]
