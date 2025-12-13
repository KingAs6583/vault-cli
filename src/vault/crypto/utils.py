import getpass

from vault.constants import MIN_PASSWORD_LENGTH
from vault.exceptions import InvalidPasswordError


def prompt_password(confirm: bool = False) -> str:
    """Prompt the user for a password securely.
    Args:
        confirm (bool): If True, prompt for password confirmation.
    Returns:
        str: The entered password.
    Raises:
        InvalidPasswordError: If passwords do not match or are too short.
    """
    password = getpass.getpass("Master password: ")

    if confirm:
        confirm_pw = getpass.getpass("Confirm password: ")
        if password != confirm_pw:
            raise InvalidPasswordError("Passwords do not match")

    if len(password) < MIN_PASSWORD_LENGTH:
        raise InvalidPasswordError("Password too short")

    return password
