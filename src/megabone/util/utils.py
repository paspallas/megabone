import uuid


def gen_unique_id() -> str:
    """Generate an unique universal identifier"""
    return uuid.uuid4().hex
