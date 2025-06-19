from utils.logger import setup_logger

logger = setup_logger('link_masker')

def generate_masked_link(domain, content, link_id):
    """Generate masked link."""
    try:
        masked_path = f"{content}s/{link_id}"
        masked_link = f"https://{domain}/{masked_path}"
        logger.info(f"Generated masked link: {masked_link}")
        return masked_link
    except Exception as e:
        logger.error(f"Error generating link: {e}")
        raise