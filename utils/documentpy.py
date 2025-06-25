class File:
    def __init__(self, title, author, created_at, path, upload_date, notes):
        self.title = title
        self.author = author
        self.created_at = created_at
        self.path = path
        self.upload_date = upload_date
        self.notes = notes

    def __str__(self):
        return f"Title: {self.title}, Author: {self.author}, Created At: {self.created_at}, Path: {self.path}, Upload Date: {self.upload_date}, Notes: {self.notes}"
    
class DocumentKey:
    def __init__(self, document, key_func):
        self.document = document
        self.key_value = key_func(document)

    def __lt__(self, other):
        return self.key_value < other.key_value

    def __eq__(self, other):
        return self.key_value == other.key_value