import valkey
client = valkey.Redis()
try:
    client.geoadd("locations", {"San Francisco": (-122.4194, 37.7749)})
    print("Dict syntax works")
except Exception as e:
    print(f"Error: {e}")
    try:
        client.geoadd("locations", -122.4194, 37.7749, "San Francisco")
        print("Args syntax works")
    except Exception as e2:
        print(f"Error 2: {e2}")
