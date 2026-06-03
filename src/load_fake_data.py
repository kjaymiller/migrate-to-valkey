import click
import valkey
import json
import logging
from valkey.exceptions import ConnectionError

logging.basicConfig(level=logging.INFO, format="%(message)s")

def insert_standard_types(client):
    """Insert only core, standard data types that are universally supported."""
    # Strings
    client.set("user:101:name", "Alice")
    client.set("user:102:name", "Bob")

    # Lists
    client.lpush("user:101:tasks", "task A", "task B", "task C")

    # Sets
    client.sadd("user:101:tags", "admin", "active")

    # Hashes
    client.hset("user:101:profile", mapping={"age": 30, "city": "New York", "status": "premium"})

    # Sorted Sets
    client.zadd("leaderboard", {"Alice": 1500, "Bob": 1200, "Charlie": 950})

    # Streams
    client.xadd("events:login", {"user": "Alice", "status": "success", "ip": "192.168.1.5"})
    client.xadd("events:login", {"user": "Bob", "status": "failed", "ip": "10.0.0.4"})

    # HyperLogLogs
    client.pfadd("unique_visitors:today", "user1", "user2", "user3", "user1")

    # Geospatial (GEO)
    client.execute_command("GEOADD", "store_locations", "-122.4194", "37.7749", "San Francisco", "-74.0060", "40.7128", "New York")

    # Bitmaps
    client.setbit("user:101:login_days", 10, 1)
    client.setbit("user:101:login_days", 11, 1)

    try:
        # Bloom Filter via RedisBloom commands (BF.ADD)
        client.execute_command("BF.ADD", "bf:usernames", "alice")
        client.execute_command("BF.ADD", "bf:usernames", "bob")
        logging.info("✅ Added Bloom Filter data (supported by Aiven for Valkey).")
    except Exception as e:
        logging.warning(f"⚠️  Could not add Bloom Filter data: {e} (Bloom module might not be enabled on the target)")

def insert_extension_types(client):
    """Insert data types that rely on modules/extensions (e.g., JSON)."""
    try:
        user_doc_1 = json.dumps({"name": "Charlie", "age": 28, "roles": ["user", "beta-tester"]})
        user_doc_2 = json.dumps({"name": "Diana", "age": 35, "roles": ["admin"]})

        client.execute_command("JSON.SET", "doc:user:103", "$", user_doc_1)
        client.execute_command("JSON.SET", "doc:user:104", "$", user_doc_2)
        logging.info("✅ Added JSON data (extension type).")
    except Exception as e:
        logging.warning(f"⚠️  Could not add JSON data: {e} (JSON module might not be enabled on the target)")

    try:
        client.execute_command("FT.CREATE", "idx:books", "ON", "HASH", "PREFIX", "1", "book:", "SCHEMA", "title", "TEXT", "author", "TAG")
        client.hset("book:1", mapping={"title": "The Hobbit", "author": "J.R.R. Tolkien"})
        client.hset("book:2", mapping={"title": "1984", "author": "George Orwell"})
        logging.info("✅ Added Search Index data (extension type).")
    except Exception as e:
        logging.warning(f"⚠️  Could not add Search data: {e} (Search module might not be enabled on the target)")

@click.command(help="Load fake test data into a database to test migration scenarios.")
@click.option("--target", required=True, envvar="TARGET_CONNECTION_STRING", help="Connection string (e.g., valkey://user:pass@host:port)")
@click.option("--scenario", type=click.Choice(['passing', 'failing']), required=True, help="Scenario to generate (passing=only standard types, failing=includes extension types)")
@click.option("--force", is_flag=True, help="Force flush existing data without confirmation.")
def load_fake_data_cmd(target, scenario, force):
    logging.info(f"Connecting to database to load '{scenario}' dataset...")
    client = valkey.from_url(target, decode_responses=True)

    try:
        client.ping()
    except ConnectionError as e:
        logging.error(f"❌ Connection error: {e}")
        return

    db_size = client.dbsize()
    if db_size > 0:
        if not force:
            click.confirm(f"⚠️  Database currently contains {db_size} keys. This will flush all data. Continue?", abort=True)
        logging.info("Flushing existing data...")
        client.flushall()
    else:
        logging.info("Database is empty. No need to flush.")

    logging.info(f"Loading '{scenario}' dataset...")

    # Both scenarios get standard types
    insert_standard_types(client)
    logging.info("✅ Added standard data types.")

    # Failing scenario also gets module/extension types
    if scenario == 'failing':
        insert_extension_types(client)

    logging.info(f"✅ Done! Test data for '{scenario}' scenario loaded.")

if __name__ == "__main__":
    load_fake_data_cmd()
