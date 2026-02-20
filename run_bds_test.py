import asyncio
import os
import shutil
import subprocess
import zipfile
import requests
import websockets
import json
import time
import sys
import uuid
import threading
import re

# Configuration
ADDON_DIR = "muscular_villager_addon"
SERVER_DIR = "bds_server"
WS_PORT = 3000

def download_server_url():
    print("Finding latest Bedrock Dedicated Server for Linux...")
    url = "https://www.minecraft.net/en-us/download/server/bedrock"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        content = response.text
    except Exception as e:
        print(f"Failed to fetch download page: {e}")
        return "https://minecraft.azureedge.net/bin-linux/bedrock-server-1.20.73.01.zip"

    match = re.search(r'https://minecraft\.azureedge\.net/bin-linux/bedrock-server-[\d\.]+\.zip', content)
    if match:
        download_url = match.group(0)
        print(f"Found download URL: {download_url}")
        return download_url
    else:
        print("Could not find download URL in page content. Using fallback.")
        return "https://minecraft.azureedge.net/bin-linux/bedrock-server-1.20.73.01.zip"

def setup_server(download_url):
    if os.path.exists(SERVER_DIR):
        print(f"Removing existing {SERVER_DIR}...")
        shutil.rmtree(SERVER_DIR)
    os.makedirs(SERVER_DIR)

    zip_path = os.path.join(SERVER_DIR, "server.zip")
    print(f"Downloading server from {download_url}...")
    try:
        r = requests.get(download_url, stream=True, timeout=120)
        r.raise_for_status()
        with open(zip_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    except Exception as e:
        print(f"Download failed: {e}")
        sys.exit(1)

    print("Extracting server...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(SERVER_DIR)

    os.remove(zip_path)

    # Configure server.properties
    props_path = os.path.join(SERVER_DIR, "server.properties")
    props = ""
    if os.path.exists(props_path):
        with open(props_path, "r") as f:
            props = f.read()

    props = props.replace("gamemode=survival", "gamemode=creative")
    props = props.replace("allow-cheats=false", "allow-cheats=true")
    props = props.replace("level-name=Bedrock level", "level-name=MuscularWorld")

    # Ensure properties exist
    if "default-player-permission-level" not in props:
         props += "\ndefault-player-permission-level=operator\n"
    if "enable-lan-visibility" not in props:
         props += "\nenable-lan-visibility=true\n"

    with open(props_path, "w") as f:
        f.write(props)

    # Make executable
    bedrock_server_bin = os.path.join(SERVER_DIR, "bedrock_server")
    if os.path.exists(bedrock_server_bin):
        os.chmod(bedrock_server_bin, 0o755)

    # Install Addon
    print("Installing addon...")
    bp_dest = os.path.join(SERVER_DIR, "behavior_packs", "muscular_villager_bp")
    rp_dest = os.path.join(SERVER_DIR, "resource_packs", "muscular_villager_rp")

    shutil.copytree(os.path.join(ADDON_DIR, "BP"), bp_dest)
    shutil.copytree(os.path.join(ADDON_DIR, "RP"), rp_dest)

    # Read Manifests
    with open(os.path.join(ADDON_DIR, "BP", "manifest.json")) as f:
        bp_manifest = json.load(f)
        bp_uuid = bp_manifest["header"]["uuid"]
        bp_version = bp_manifest["header"]["version"]

    with open(os.path.join(ADDON_DIR, "RP", "manifest.json")) as f:
        rp_manifest = json.load(f)
        rp_uuid = rp_manifest["header"]["uuid"]
        rp_version = rp_manifest["header"]["version"]

    # Add to valid_known_packs.json
    valid_packs_path = os.path.join(SERVER_DIR, "valid_known_packs.json")
    known_packs = []
    if os.path.exists(valid_packs_path):
        try:
            with open(valid_packs_path, "r") as f:
                content = f.read()
                if content:
                    known_packs = json.loads(content)
        except json.JSONDecodeError:
            pass

    known_packs.append({
        "file_system": "RawPath",
        "path": "behavior_packs/muscular_villager_bp",
        "uuid": bp_uuid,
        "version": ".".join(map(str, bp_version))
    })
    known_packs.append({
        "file_system": "RawPath",
        "path": "resource_packs/muscular_villager_rp",
        "uuid": rp_uuid,
        "version": ".".join(map(str, rp_version))
    })

    with open(valid_packs_path, "w") as f:
        json.dump(known_packs, f, indent=4)

    # Create World Config
    world_dir = os.path.join(SERVER_DIR, "worlds", "MuscularWorld")
    os.makedirs(world_dir)

    with open(os.path.join(world_dir, "world_behavior_packs.json"), "w") as f:
        json.dump([
            {
                "pack_id": bp_uuid,
                "version": bp_version
            }
        ], f)

    with open(os.path.join(world_dir, "world_resource_packs.json"), "w") as f:
        json.dump([
            {
                "pack_id": rp_uuid,
                "version": rp_version
            }
        ], f)

    print("Server setup complete.")

async def run_server():
    connected_event = asyncio.Event()

    async def handler(websocket):
        print("BDS Connected via WebSocket!")
        connected_event.set()

        # Subscribe
        subscribe_msg = {
            "body": {
                "eventName": "PlayerMessage"
            },
            "header": {
                "requestId": str(uuid.uuid4()),
                "messagePurpose": "subscribe",
                "version": 1,
                "messageType": "commandRequest"
            }
        }
        await websocket.send(json.dumps(subscribe_msg))

        # Summon
        print("Summoning Muscular Villager...")
        summon_cmd = {
            "body": {
                "origin": { "type": "player" },
                "commandLine": "summon my:muscular_villager ~ ~ ~",
                "version": 1
            },
            "header": {
                "requestId": str(uuid.uuid4()),
                "messagePurpose": "commandRequest",
                "version": 1,
                "messageType": "commandRequest"
            }
        }
        await websocket.send(json.dumps(summon_cmd))

        await asyncio.sleep(2)

        # Check
        list_cmd = {
             "body": {
                "origin": { "type": "player" },
                "commandLine": "testfor @e[type=my:muscular_villager]",
                "version": 1
            },
            "header": {
                "requestId": str(uuid.uuid4()),
                "messagePurpose": "commandRequest",
                "version": 1,
                "messageType": "commandRequest"
            }
        }
        await websocket.send(json.dumps(list_cmd))

        try:
            async for message in websocket:
                msg = json.loads(message)
                if 'body' in msg:
                    # Log everything
                    print(f"WS Recv: {msg}")
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket closed.")

    print(f"Starting WebSocket server on port {WS_PORT}...")

    server = await websockets.serve(handler, "localhost", WS_PORT)

    print("Starting BDS...")
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = os.path.abspath(SERVER_DIR)

    process = subprocess.Popen(
        [os.path.join(os.path.abspath(SERVER_DIR), "bedrock_server")],
        cwd=os.path.abspath(SERVER_DIR),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        universal_newlines=True
    )

    def read_stdout(proc):
        for line in proc.stdout:
            print(f"[BDS]: {line.strip()}")
            if "Server started" in line:
                print("Sending connect command...")
                try:
                    proc.stdin.write(f"connect localhost:{WS_PORT}\n")
                    proc.stdin.flush()
                except Exception as e:
                    print(f"Failed to write to stdin: {e}")

    def read_stderr(proc):
        for line in proc.stderr:
            print(f"[BDS ERR]: {line.strip()}")

    t_out = threading.Thread(target=read_stdout, args=(process,))
    t_out.daemon = True
    t_out.start()

    t_err = threading.Thread(target=read_stderr, args=(process,))
    t_err.daemon = True
    t_err.start()

    try:
        await asyncio.wait_for(connected_event.wait(), timeout=90)
    except asyncio.TimeoutError:
        print("Timeout waiting for BDS to connect.")

    # Wait a bit more to verify entity spawn
    await asyncio.sleep(5)

    print("Stopping BDS...")
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()

    server.close()
    await server.wait_closed()

if __name__ == "__main__":
    url = download_server_url()
    setup_server(url)
    asyncio.run(run_server())
