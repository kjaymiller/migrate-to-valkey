import os
import valkey
import sys

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

if __name__ == "__main__":
    source = os.environ.get("SOURCE_CONNECTION_STRING")
    target = os.environ.get("TARGET_CONNECTION_STRING")
    
    if not source and not target:
        print("Neither SOURCE_CONNECTION_STRING nor TARGET_CONNECTION_STRING are set.")
        sys.exit(1)
        
    flush_db("Source", source)
    flush_db("Target", target)
