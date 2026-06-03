import asyncio
from glide import GlideClient, GlideClientConfiguration, NodeAddress

async def main():
    config = GlideClientConfiguration([NodeAddress("localhost", 6379)])
    client = await GlideClient.create(config)
    info = await client.info()
    print(info)

asyncio.run(main())
