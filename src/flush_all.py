import os
import valkey
import sys
import click

def flush_db(name, conn_str):
    if not conn_str:
        print(f"Skipping {name} (no connection string)")
        return
    try:
        client = valkey.from_url(conn_str)
        client.flushall()
        print(f"✅ Flushed {name}")
    except Exception as e:
        print(f"❌ Error flushing {name}: {e}")

@click.command(help="Flush both source and target databases")
@click.option("--source", envvar="SOURCE_CONNECTION_STRING", help="Source connection string")
@click.option("--target", envvar="TARGET_CONNECTION_STRING", help="Target connection string")
def flush_all_cmd(source, target):
    if not source and not target:
        print("Neither source nor target connection string are provided.")
        sys.exit(1)

    flush_db("Source", source)
    flush_db("Target", target)

if __name__ == "__main__":
    flush_all_cmd()
