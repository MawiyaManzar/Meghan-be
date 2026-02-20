# Understanding the Community WebSocket Server

This document explains how the real-time community chat system works in `app/routers/community_ws.py`.

---

## 🎯 Purpose

The server provides **Discord-style real-time chat** for communities. Users can:
- Connect to a community chat room
- Send messages instantly to all other connected members
- Send messages anonymously or with their identity
- Load message history via REST API

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     ConnectionManager                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  active_connections: Dict[community_id, Set[WS]]    │    │
│  │                                                     │    │
│  │  Community 1: [WS_user1, WS_user2, WS_user3]       │    │
│  │  Community 2: [WS_user4, WS_user5]                 │    │
│  │  Community 3: [WS_user6]                           │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    WebSocket Endpoint                        │
│  /api/communities/ws/{community_id}?token=JWT               │
│                                                             │
│  1. Authenticate user (JWT)                                 │
│  2. Verify community membership                             │
│  3. Add to ConnectionManager                                │
│  4. Listen for messages → Broadcast to all                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Key Components

### 1. ConnectionManager Class

This is the **heart** of the WebSocket system. It tracks who's connected to which community.

```python
class ConnectionManager:
    def __init__(self):
        # Dictionary: community_id -> set of websocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
```

**Methods:**

| Method | Purpose |
|--------|---------|
| `connect(community_id, websocket)` | Accept connection & add to room |
| `disconnect(community_id, websocket)` | Remove connection from room |
| `broadcast(community_id, message)` | Send message to ALL users in room |

**How `broadcast` works:**
```python
async def broadcast(self, community_id: int, message: dict):
    # Get all websockets for this community
    for websocket in self.active_connections.get(community_id, set()):
        # Check if still connected
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_json(message)  # Send!
        else:
            dead.append(websocket)  # Mark for cleanup
    
    # Clean up dead connections
    for ws in dead:
        self.disconnect(community_id, ws)
```

---

### 2. WebSocket Endpoint Flow

```
Client connects to: /api/communities/ws/5?token=eyJhbGc...

     ┌──────────┐                              ┌──────────┐
     │  Client  │                              │  Server  │
     └────┬─────┘                              └────┬─────┘
          │                                         │
          │  1. Connect with JWT token              │
          │ ────────────────────────────────────▶  │
          │                                         │
          │         2. Validate token               │
          │         3. Check membership             │
          │         4. Accept connection            │
          │  ◀────────────────────────────────────  │
          │                                         │
          │  5. Send message                        │
          │  {"type":"message","content":"Hi!"}     │
          │ ────────────────────────────────────▶  │
          │                                         │
          │         6. Safety check                 │
          │         7. Save to database             │
          │         8. Broadcast to ALL             │
          │  ◀────────────────────────────────────  │
          │                                         │
```

---

### 3. Authentication

The server uses **JWT tokens** passed as a query parameter:

```python
@router.websocket("/ws/{community_id}")
async def community_chat_ws(websocket: WebSocket, community_id: int):
    # Get token from URL: /ws/5?token=eyJhbG...
    token = websocket.query_params.get("token")
    
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Decode and verify the JWT
    user = _authenticate_websocket(token, db)
```

**Why query params instead of headers?**
- Browser WebSocket API doesn't support custom headers easily
- Query params work universally across all clients

---

### 4. Message Format

**Client sends:**
```json
{
    "type": "message",
    "content": "Hello everyone!",
    "is_anonymous": true
}
```

**Server broadcasts to all:**
```json
{
    "type": "message",
    "message": {
        "id": 123,
        "community_id": 5,
        "user_id": 42,
        "content": "Hello everyone!",
        "is_anonymous": true,
        "created_at": "2026-02-20T10:30:00Z",
        "display_name": "Anonymous"
    }
}
```

**Error response:**
```json
{
    "type": "error",
    "detail": "Message content cannot be empty"
}
```

---

### 5. Safety Gate

Before broadcasting, messages go through a safety check:

```python
safety = safety_service.assess_user_message(content)

if not safety.allowed:
    # Don't broadcast - send private safety message instead
    await websocket.send_json({
        "type": "system",
        "role": "safety",
        "content": safety.safe_reply
    })
    # Also log crisis event and notify therapist
```

This prevents harmful content from being shared with the community.

---

### 6. REST Endpoint for History

```python
@router.get("/{community_id}/messages")
async def list_community_messages(community_id: int, limit: int = 50, offset: int = 0):
    # Returns paginated message history
```

**Use case:** When a user opens the chat, load the last 50 messages to show history.

---

## 🔄 Connection Lifecycle

```
1. CONNECT
   ├── Validate JWT token
   ├── Check community membership
   ├── Accept WebSocket connection
   └── Add to ConnectionManager

2. MESSAGE LOOP (while connected)
   ├── Receive JSON message
   ├── Validate content
   ├── Safety check
   ├── Save to database
   └── Broadcast to all connections

3. DISCONNECT
   ├── Catch WebSocketDisconnect exception
   ├── Remove from ConnectionManager
   └── Close database session
```

---

## 💡 Important Patterns

### Pattern 1: In-Memory Connection Tracking
```python
manager = ConnectionManager()  # Module-level singleton
```
This works for **single-server deployments**. For multi-server, you'd need Redis pub/sub.

### Pattern 2: Generator for DB Sessions
```python
def _get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # Always cleanup!
```

### Pattern 3: Dead Connection Cleanup
```python
if websocket.client_state == WebSocketState.CONNECTED:
    await websocket.send_json(message)
else:
    dead.append(websocket)  # Clean up later
```

---

## 📝 Practice Task

Now it's your turn! Create a **simple echo WebSocket server** with the following requirements:

### Requirements

1. **Create a new file:** `app/routers/echo_ws.py`

2. **Build a WebSocket endpoint:** `/api/echo/ws`

3. **Functionality:**
   - Accept WebSocket connections (no authentication needed for practice)
   - When a client sends a message, echo it back with a timestamp
   - Track how many total messages this connection has sent

4. **Message format:**
   - **Client sends:** `{"message": "Hello!"}`
   - **Server responds:** 
     ```json
     {
         "original": "Hello!",
         "echoed_at": "2026-02-20T10:30:00Z",
         "message_count": 1
     }
     ```

5. **Add validation:**
   - If message is empty, return error
   - If message is longer than 500 characters, return error

6. **Bonus:** Add a `/api/echo/stats` REST endpoint that returns how many active connections exist

### Starter Template

```python
"""
Echo WebSocket - Practice Exercise
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime
import json

router = APIRouter(prefix="/api/echo", tags=["echo"])

# TODO: Create a simple connection counter

@router.websocket("/ws")
async def echo_ws(websocket: WebSocket):
    # TODO: Accept the connection
    
    # TODO: Track message count for this connection
    
    try:
        while True:
            # TODO: Receive message
            # TODO: Validate
            # TODO: Echo back with timestamp and count
            pass
    except WebSocketDisconnect:
        # TODO: Handle disconnect
        pass
```

### Success Criteria

- [ ] WebSocket accepts connections at `/api/echo/ws`
- [ ] Messages are echoed with timestamp and count
- [ ] Empty messages return error
- [ ] Long messages (>500 chars) return error
- [ ] Connection counter tracks active connections

### Testing

Use a WebSocket client like **Postman** or this Python script:

```python
import asyncio
import websockets
import json

async def test_echo():
    async with websockets.connect("ws://localhost:8000/api/echo/ws") as ws:
        await ws.send(json.dumps({"message": "Hello!"}))
        response = await ws.recv()
        print(response)

asyncio.run(test_echo())
```

---

Good luck! 🚀 Once you complete this, you'll have a solid understanding of WebSocket fundamentals.
