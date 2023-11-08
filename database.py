import os
import psycopg2
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv

load_dotenv()


class Queries:
    SELECT_FILE_ID_FROM_FILES = "SELECT file_id FROM files WHERE file_path = %s"
    SELECT_TOKEN_ID_FROM_TOKENS = "SELECT token_id FROM tokens WHERE token_name = %s"
    SELECT_FROM_MAPPING = "SELECT * FROM mapping WHERE token_id = %s AND file_id = %s"
    INSERT_INTO_FILES = "INSERT INTO files (file_path) VALUES (%s)"
    INSERT_INTO_TOKENS = "INSERT INTO tokens (token_name, embedding) VALUES (%s, %s)"
    INSERT_INTO_MAPPING = "INSERT INTO mapping (file_id, token_id) VALUES (%s, %s)"


class PostgresDatabase:
    def __init__(self) -> None:
        self.__db = os.getenv("DB_NAME")
        self.__user = os.getenv("DB_USER")
        self.__password = os.getenv("DB_PWD")

    def insert_tokens(self, doc, file_id) -> None:
        conn, cur = self.__connect()
        register_vector(conn)

        seen = set()
        for token in doc:
            if not token.has_vector:
                print(f"out of vocab - {token.text}")
                continue
            text, vector = token.text, token.vector
            if text in seen:
                print(f"token has already been processed - {text}")
                continue
            seen.add(text)

            cur.execute(Queries.SELECT_TOKEN_ID_FROM_TOKENS, (text,))
            if cur.fetchone() is None:
                print(f"token {text} doesn't exist in tokens table")
                cur.execute(
                    Queries.INSERT_INTO_TOKENS,
                    (
                        text,
                        vector,
                    ),
                )
                conn.commit()
            else:
                print(f"token {text} already exists in tokens table")

            cur.execute(Queries.SELECT_TOKEN_ID_FROM_TOKENS, (text,))
            token_id = cur.fetchone()[0]

            cur.execute(
                Queries.SELECT_FROM_MAPPING,
                (
                    token_id,
                    file_id,
                ),
            )
            if cur.fetchone() is None:
                print(
                    f"mapping between file id {file_id} and token id {token_id} doesn't exist"
                )
                cur.execute(
                    Queries.INSERT_INTO_MAPPING,
                    (
                        file_id,
                        token_id,
                    ),
                )
                conn.commit()
            else:
                print(
                    f"mapping between file id {file_id} and token id {token_id} already exist"
                )

        self.__close(cur, conn)

    def insert_file_path(self, path) -> int:
        conn, cur = self.__connect()
        cur.execute(Queries.SELECT_FILE_ID_FROM_FILES, (path,))
        file_id = cur.fetchone()

        if not file_id:
            cur.execute(Queries.INSERT_PATH_INTO_FILES, (path,))
            conn.commit()
            cur.execute(Queries.SELECT_FILE_ID_FROM_FILES, (path,))
            file_id = cur.fetchone()

        self.__close(cur, conn)
        return file_id[0]

    def __connect(self):
        conn = psycopg2.connect(
            database=self.__db, user=self.__user, password=self.__password
        )
        cur = conn.cursor()
        return conn, cur

    def __close(self, cur, conn) -> None:
        cur.close()
        conn.close()
