import click
import valkey
import sys

@click.command(help="Flush all data from a specific database by connection string")
@click.argument("connection_string", required=True)
def flush_cmd(connection_string):
    try:
        client = valkey.from_url(connection_string)
        client.flushall()
        print(f"✅ Successfully flushed database")
    except Exception as e:
        print(f"❌ Error flushing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    flush_cmd()
