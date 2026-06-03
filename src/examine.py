import os
import sys
import valkey

def main():
    conn_str = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SOURCE_CONNECTION_STRING")
    if not conn_str:
        print("Error: Please provide a connection string as an argument or set SOURCE_CONNECTION_STRING.")
        sys.exit(1)

    try:
        # Connect to the database
        client = valkey.from_url(conn_str, decode_responses=True)
        
        # Grab all keys using scan
        keys = list(client.scan_iter())
        if not keys:
            print("No keys found.")
            return

        # Use a pipeline to fetch all types in a SINGLE network request
        pipe = client.pipeline()
        for k in keys:
            pipe.type(k)
        
        types = pipe.execute()

        # Print the results
        for k, t in zip(keys, types):
            print(f"{k} -> {t}")

    except Exception as e:
        print(f"Error connecting or fetching data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
