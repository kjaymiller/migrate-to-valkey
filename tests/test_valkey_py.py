import valkey
from unittest.mock import patch, MagicMock

# Create a mock redis connection
client = valkey.Redis()
client.execute_command = MagicMock(return_value=b"redis_version:7.0.0\r\nvalkey_version:7.2.5\r\ndragonfly_version:1.15.0\r\n")

info_dict = client.info()
print(info_dict)

res = client.execute_command("INFO", "server")
print(res)
