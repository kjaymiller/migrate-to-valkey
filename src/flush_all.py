import os
import valkey
import sys
import click

def flush_db(name, conn_str):
    if not conn_str:
        print(f"Skipping {name} (no connection string)")
        return True
    try:
        client = valkey.from_url(conn_str)
        client.flushall()
        print(f"✅ Flushed {name}")
        return True
    except Exception as e:
        print(f"❌ Error flushing {name}: {e}")
        return False

@click.command(help="Flush both source and target databases")
@click.option("--source", default="valkey://localhost:6379", envvar="SOURCE_CONNECTION_STRING", help="Source connection string")
@click.option("--target", default="valkey://localhost:6379", envvar="TARGET_CONNECTION_STRING", help="Target connection string")
def flush_all_cmd(source, target):
    if not source and not target:
        print("Neither source nor target connection string are provided.")
        sys.exit(1)

    source_success = flush_db("Source", source)
    target_success = flush_db("Target", target)

    if not source_success or not target_success:
        sys.exit(1)

if __name__ == "__main__":
    flush_all_cmd()
