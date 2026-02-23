#!/usr/bin/env python3
"""
Test script for the community WebSocket server.

Usage:
  1. Start the server: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  2. Run this script: uv run python scripts/test_websocket_live.py

The script will:
  - Check if the server is running (GET /health)
  - Register/login to get a JWT
  - Ensure default communities exist and join one
  - Connect to the WebSocket and send a test message
  - Verify the broadcast response
"""

import asyncio
import json
import sys

import httpx
import websockets

BASE_URL = "http://localhost:8000"
WS_BASE = "ws://localhost:8000"


def print_section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


async def check_server_running() -> bool:
    """Check if the API server is running."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{BASE_URL}/health")
            return r.status_code == 200
    except Exception as e:
        print(f"  Error: {e}")
        return False


async def main() -> bool:
    print_section("WebSocket Server Test")
    print("\nThis script tests the community WebSocket at /api/communities/ws/{community_id}")

    # Step 1: Check server
    print_section("1. Checking server")
    print("\n  GET /health ...")
    if not await check_server_running():
        print("  ✗ Server is not running!")
        print("\n  Start the server with:")
        print("    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return False
    print("  ✓ Server is running")

    # Step 2: Register and login
    print_section("2. Authentication")
    email = "wstest@example.com"
    password = "testpass123"

    async with httpx.AsyncClient(timeout=10.0) as client:
        # Register (ignore if already exists)
        r = await client.post(
            f"{BASE_URL}/api/auth/register",
            json={"email": email, "password": password},
        )
        if r.status_code not in (200, 201, 400):
            print(f"  Register failed: {r.status_code} - {r.text}")
            return False

        # Login
        r = await client.post(
            f"{BASE_URL}/api/auth/login-json",
            json={"email": email, "password": password},
        )
        if r.status_code != 200:
            print(f"  Login failed: {r.status_code} - {r.text}")
            return False

        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"  ✓ Logged in, token: {token[:40]}...")

        # Step 3: Get communities and join one
        print_section("3. Community setup")
        r = await client.get(f"{BASE_URL}/api/communities", headers=headers)
        if r.status_code != 200:
            print(f"  List communities failed: {r.status_code}")
            return False

        data = r.json()
        communities = data.get("communities", [])
        if not communities:
            print("  ✗ No communities found")
            return False

        community_id = communities[0]["id"]
        print(f"  Found community: {communities[0]['name']} (id={community_id})")

        # Join if not already a member
        r = await client.post(
            f"{BASE_URL}/api/communities/{community_id}/join",
            headers=headers,
            json={"is_anonymous": True},
        )
        if r.status_code not in (200, 201):
            print(f"  Join failed: {r.status_code} - {r.text}")
            return False
        print(f"  ✓ Joined community {community_id}")

    # Step 4: WebSocket connection and message
    print_section("4. WebSocket test")
    ws_url = f"{WS_BASE}/api/communities/ws/{community_id}?token={token}"
    print(f"\n  Connecting to {ws_url[:80]}...")

    try:
        async with websockets.connect(ws_url) as ws:
            print("  ✓ WebSocket connected")

            # Send test message
            msg = {"type": "message", "content": "Hello from WebSocket test!", "is_anonymous": True}
            await ws.send(json.dumps(msg))
            print(f"  Sent: {json.dumps(msg)}")

            # Receive broadcast
            raw = await asyncio.wait_for(ws.recv(), timeout=5.0)
            data = json.loads(raw)
            print(f"  Received: {json.dumps(data, indent=2)}")

            if data.get("type") == "message" and "message" in data:
                content = data["message"].get("content", "")
                if content == msg["content"]:
                    print("  ✓ WebSocket server is working correctly!")
                    return True
                else:
                    print(f"  ✗ Unexpected content: got {content!r}")
            else:
                print(f"  ✗ Unexpected response type: {data.get('type')}")
                if data.get("type") == "error":
                    print(f"    Error detail: {data.get('detail')}")

    except asyncio.TimeoutError:
        print("  ✗ Timeout waiting for response")
        return False
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"  ✗ WebSocket connection failed: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

    return False


if __name__ == "__main__":
    success = asyncio.run(main())
    print_section("Result")
    print("\n  WebSocket server: " + ("✓ OK" if success else "✗ FAILED"))
    sys.exit(0 if success else 1)
