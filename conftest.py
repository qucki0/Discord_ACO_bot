import asyncio

import pytest
import pytest_asyncio

from sql.client import SqlClient


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest_asyncio.fixture(scope="session")
async def connected_db():
    client = SqlClient(user="dba", password='dbaPass', db_name="test_db")
    await client.start()
    await client.create_tables()
    yield client
    await client.drop_tables()
    await client.stop()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_database(connected_db: SqlClient):
    yield
    await connected_db.delete_all_data()
