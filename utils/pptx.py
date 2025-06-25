from pptx import Presentation

def extract_pptx_metadata(path):
    prs = Presentation(path)
    props = prs.core_properties
    return {
        'title': props.title,
        'author': props.author,
        'created_at': props.created,
    }