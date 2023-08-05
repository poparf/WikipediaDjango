import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))

# edited by poparobert22
def save_entry(title, content, oldTitle):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    if oldTitle == None:     
        filename = f"entries/{title}.md"
        if default_storage.exists(filename):
            default_storage.delete(filename)
        default_storage.save(filename, ContentFile(content))
    else:
        filename = f"entries/{title}.md"
        old_filename = f"entries/{oldTitle}.md"
        if default_storage.exists(old_filename):
            default_storage.delete(old_filename)
            
        default_storage.save(filename, ContentFile(content))

# Added by poparobert22
def save_entry_new_title(title,content, oldTitle):
    filename = f"entries/{title}.md"
    if default_storage.exists(oldTitle):
        default_storage.delete(oldTitle)
    default_storage.save(filename, ContentFile(content))

def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None