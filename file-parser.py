import os
from dotenv import load_dotenv
import fitz
import docx
from docx import Document


load_dotenv()
ROOT_FILE_DIR = os.getenv("ROOT_FILE_DIR")


def main():
    file_paths_to_parse = []
    for path, subdirs, files in os.walk(ROOT_FILE_DIR):
        for file_name in files:
            file_paths_to_parse.append(os.path.join(path, file_name))    

    files_not_read = []
    
    # try to read each file if possible
    for fp in file_paths_to_parse:
        print(f"file path: {fp}, create time: {os.path.getctime(fp)}, last modified time: {os.path.getmtime(fp)}")
        with open(fp, 'r') as file:
            while True:
                try:
                    chunk = file.read(1024)  # 1 Kibibyte
                    if not chunk:
                        break  # the while loop
                    print(chunk.strip().replace('\n', ' '))
                except UnicodeDecodeError:
                    print(f"Could not read file {fp} due to extension..trying again with pdf reader.")

                    try:
                        document = fitz.open(fp)
                        for page in document:
                            print(page.get_text().strip().replace('\n', ' '))
                        break
                    except ValueError:
                        print(f"Could not read file {fp} due to it being encrypted or closed..skipping read")
                        break  # necessary break 
                    except fitz.FileDataError:
                        print(f"Could not read file {fp} due to extension..trying again with docx reader.")

                    try:
                        document = Document(fp)
                        for paragraph in document.paragraphs:
                            if paragraph.text != '':
                                print(paragraph.text.strip().replace('\n', ' '))
                        break
                    except Exception as e:
                        print(f"Could not read file {fp} due to extension..file type not supported currently. Skipping read.")
                        files_not_read.append(fp)
                        break

                    break

    print(files_not_read)

main()
