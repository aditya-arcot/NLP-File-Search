import os
import spacy
from database import PostgresDatabase


def process_files(dir) -> None:
    for root, _, files in os.walk(dir):
        for file in files:
            path = os.path.join(root, file)
            process_file(path)


def process_file(path) -> None:
    try:
        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()
        content = " ".join([line.strip().lower() for line in lines])
    except Exception as e:
        print(path)
        print(f"Exception - {e}")
        return

    doc = nlp(content)
    file_id = db.insert_file_path(path)
    db.insert_tokens(doc, file_id)


if __name__ == "__main__":
    db = PostgresDatabase()
    nlp = spacy.load("en_core_web_lg", enable=["tok2vec"])
    # print(nlp.pipe_names)
    parent_folder = os.path.dirname(os.path.abspath(__file__))
    documents_folder = os.path.join(parent_folder, "documents")
    process_files(documents_folder)
