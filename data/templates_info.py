from data.templates_store import (
    load_templates,
    save_templates,
    add_template,
    delete_template,
    get_template_file_paths,
    DEFAULT_TEMPLATES
)

# Eski importlar uchun qulaylik
TEMPLATES_DATA = load_templates()

def get_templates() -> dict:
    """Doim eng yangi shablonlar ro'yxatini qaytaradi."""
    return load_templates()
