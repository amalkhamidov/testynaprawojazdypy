from concurrent.futures import ThreadPoolExecutor

import asyncpg
from bs4 import BeautifulSoup
from langdetect import detect, detector_factory

# Initialize langdetect
detector_factory.init_factory()


async def update_formatted_content(pool, slide_id, formatted_content):
    """
    Update the formatted_content column of the slides table for the given slide_id.

    Args:
        pool (asyncpg.Pool): An instance of asyncpg connection pool.
        slide_id (int): The ID of the slide to update.
        formatted_content (str): The formatted content to set in the formatted_content column.
    """
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("UPDATE slides SET formatted_content = $1 WHERE id = $2", formatted_content,
                               slide_id)


def process_text(text):
    """
    Process a single text and separate English and Polish text.

    Args:
        text (str): A string containing the text to process.

    Returns:
        tuple: A tuple containing the separated English and Polish texts.
    """
    soup = BeautifulSoup(text, 'html.parser')

    english_text = ''
    polish_text = ''
    for t in soup.stripped_strings:
        lang = detect(t)
        if lang == 'en':
            english_text += ' ' + t
        elif lang == 'pl':
            polish_text += ' ' + t

    english_text = english_text.strip()
    polish_text = polish_text.strip()

    return english_text, polish_text


class TextProcessor:
    def __init__(self, db_name, db_user, db_password, db_host, db_port=None):
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port

    async def create_conn_pool(self):
        """
        Create a connection pool to the PostgreSQL database.

        Returns:
            asyncpg.Pool: An instance of asyncpg connection pool.
        """
        return await asyncpg.create_pool(
            database=self.db_name,
            user=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port
        )

    async def process_database_texts(self, pool):
        """
        Process the content of all slides in the database and update the formatted_content column.

        Args:
            pool (asyncpg.Pool): An instance of asyncpg connection pool.
        """
        async with pool.acquire() as conn:
            texts = [
                (record['id'], record['content'])
                for record in await conn.fetch("SELECT id, content FROM slides")
            ]

        processed_texts = self.process_texts([text[1] for text in texts])

        for idx, (slide_id, content) in enumerate(texts):
            _, formatted_text = processed_texts[idx]
            print(f"Updating slide {slide_id} with formatted content")
            await update_formatted_content(pool, slide_id, formatted_text)

    def process_texts(self, texts):
        """
        Process a list of texts and separate English and Polish text.

        Args:
            texts (list): A list of strings containing the texts to process.

        Returns:
            list: A list of tuples containing the separated English and Polish texts.
        """
        with ThreadPoolExecutor() as executor:
            processed_texts = list(executor.map(process_text, texts))

        return processed_texts

    async def fetch_formatted_content(pool):
        async with pool.acquire() as conn:
            records = await conn.fetch("SELECT id, formatted_content FROM slides")
            return [(record['id'], record['formatted_content']) for record in records]

    async def main(self):
        """
        Main function to process and update the texts in the database.
        """
        pool = await self.create_conn_pool()

        # Call the function to process and update the database texts
        await self.process_database_texts(pool)

        # Close the connection pool
        await pool.close()


"""if __name__ == "__main__":
    # Replace these values with your own database credentials

    processor = TextProcessor(
        settings.PG_DATABASE, settings.PG_LOGIN,
        settings.PG_PASS, settings.PG_HOST
    )
    asyncio.run(processor.main())
"""