from docx import Document

def extract_docx_metadata(path):
    doc = Document(path)
    props = doc.core_properties
    return {
        'title': props.title,
        'author': props.author,
        'created_at': props.created,
    }