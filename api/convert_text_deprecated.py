import asyncio
import concurrent.futures

import asyncpg
from bs4 import BeautifulSoup
from langdetect import detect, detector_factory

from config import settings

detector_factory.init_factory()


def separate_languages(text):
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


def process_texts(texts):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(separate_languages, texts))

    return results


"""# Example: processing multiple texts
texts = []  # Replace this with your list of 1500 texts
processed_texts = process_texts(texts)

for idx, (english, polish) in enumerate(processed_texts):
    print(f"Text {idx + 1}")
    print("English text:", english)
    print("Polish text:", polish)
    print()
"""


# Replace the psycopg2 connection details with asyncpg connection details
async def create_conn_pool():
    """
    settings.PG_LOGIN}:{settings.PG_PASS}@{settings.PG_HOST}"
            f"/{settings.PG_DATABASE
    :return:
    """
    return await asyncpg.create_pool(
        database=settings.PG_DATABASE,
        user=settings.PG_LOGIN,
        password=settings.PG_PASS,
        host=settings.PG_HOST,
    )


async def update_formatted_content(pool, slide_id, formatted_content):
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("UPDATE slides SET formatted_content = $1 WHERE id = $2", formatted_content, slide_id)


async def process_database_texts(pool):
    async with pool.acquire() as conn:
        texts = [
            (record['id'], record['content'])
            for record in await conn.fetch("SELECT id, content FROM slides")
        ]

    processed_texts = process_texts([text[1] for text in texts])

    for idx, (slide_id, content) in enumerate(texts):
        formatted_text, _ = processed_texts[idx]
        if not formatted_text:
            print("No formatted text for slide", slide_id)

        print(f"Updating slide {slide_id} with formatted content")
        await update_formatted_content(pool, slide_id, formatted_text)


async def main():
    pool = await create_conn_pool()

    # Call the function to process and update the database texts
    await process_database_texts(pool)

    # Close the connection pool
    await pool.close()


# Run the main function using asyncio
# asyncio.run(main())
