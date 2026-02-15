import asyncio
import json
import sys

# Try to import websockets (need to install via pip install websockets)
try:
    import websockets
except ImportError:
    print("Please install websockets library: pip install websockets")
    sys.exit(1)

# Default BDS WebSocket port is usually 3000 if configured, or needs to be configured.
# Command to connect: /connect localhost:3000
URI = "ws://localhost:3000"

async def connect_and_listen():
    print(f"Connecting to {URI}...")
    try:
        async with websockets.connect(URI) as websocket:
            print("Connected!")

            # Subscribe to events
            print("Subscribing to PlayerMessage event...")
            subscribe_message = {
                "header": {
                    "requestId": "12345",
                    "messagePurpose": "subscribe",
                    "version": 1,
                    "messageType": "commandRequest"
                },
                "body": {
                    "eventName": "PlayerMessage"
                }
            }
            await websocket.send(json.dumps(subscribe_message))

            # Send a command to verify the villager exists (if op)
            print("Sending command: /testfor @e[type=custom:muscular_villager]")
            command_message = {
                "header": {
                    "requestId": "67890",
                    "messagePurpose": "commandRequest",
                    "version": 1,
                    "messageType": "commandRequest"
                },
                "body": {
                    "origin": {
                        "type": "player"
                    },
                    "commandLine": "testfor @e[type=custom:muscular_villager]",
                    "version": 1
                }
            }
            await websocket.send(json.dumps(command_message))

            # Listen loop
            print("Listening for messages...")
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                print(f"Received: {json.dumps(data, indent=2)}")

                # Exit condition example
                if "body" in data and "matches" in data["body"]: # Simplified check
                     if data["body"]["matches"]:
                         print("SUCCESS: Muscular Villager found!")
                         break

    except Exception as e:
        print(f"Connection failed: {e}")
        print("Ensure BDS is running and you have connected via '/connect localhost:3000' in-game console if testing locally.")

if __name__ == "__main__":
    asyncio.run(connect_and_listen())
