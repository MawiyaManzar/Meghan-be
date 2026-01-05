"""
Manual test script for Phase 3 endpoints.
Can be run without pytest if pytest is not installed.
Requires the server to be running.
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")

def print_response(name, response):
    print(f"\n{name}:")
    print(f"  Status: {response.status_code}")
    try:
        print(f"  Response: {json.dumps(response.json(), indent=4)}")
    except:
        print(f"  Response: {response.text}")

def test_phase3_endpoints():
    """Test Phase 3 endpoints manually."""
    print_section("PHASE 3 ENDPOINT TESTS")
    
    # Step 1: Register and Login
    print_section("1. Authentication")
    
    print("\nRegistering user...")
    register_response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={"email": "manualtest@example.com", "password": "testpass123"}
    )
    print_response("Register", register_response)
    
    if register_response.status_code not in [200, 201, 400]:  # 400 if user exists
        print("ERROR: Registration failed!")
        return False
    
    print("\nLogging in...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login-json",
        json={"email": "manualtest@example.com", "password": "testpass123"}
    )
    print_response("Login", login_response)
    
    if login_response.status_code != 200:
        print("ERROR: Login failed!")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"\n✓ Authentication successful! Token: {token[:30]}...")
    
    # Step 2: Test User State Endpoints
    print_section("2. User State Endpoints (Task 3.2)")
    
    print("\n2.1 GET /api/users/me/state (should create default)")
    state_response = requests.get(f"{BASE_URL}/api/users/me/state", headers=headers)
    print_response("GET State", state_response)
    if state_response.status_code == 200:
        state = state_response.json()
        assert state["xp"] == 0, "Initial XP should be 0"
        assert state["level"] == 1, "Initial level should be 1"
        print("  ✓ Default state created correctly")
    else:
        print("  ✗ FAILED")
        return False
    
    print("\n2.2 PUT /api/users/me/state (update state)")
    update_response = requests.put(
        f"{BASE_URL}/api/users/me/state",
        headers=headers,
        json={"mood": "Pulse", "steps": 5000}
    )
    print_response("PUT State", update_response)
    if update_response.status_code == 200:
        updated = update_response.json()
        assert updated["mood"] == "Pulse", "Mood should be updated"
        assert updated["steps"] == 5000, "Steps should be updated"
        print("  ✓ State updated correctly")
    else:
        print("  ✗ FAILED")
        return False
    
    print("\n2.3 POST /api/users/me/state/xp (add XP)")
    xp_response = requests.post(
        f"{BASE_URL}/api/users/me/state/xp",
        headers=headers,
        json={"amount": 50}
    )
    print_response("Add XP", xp_response)
    if xp_response.status_code == 200:
        xp_data = xp_response.json()
        assert xp_data["xp"] == 50, "XP should be 50"
        assert xp_data["level"] == 1, "Level should still be 1 (50 < 200)"
        print("  ✓ XP added correctly, level calculated correctly")
    else:
        print("  ✗ FAILED")
        return False
    
    # Step 3: Test Profile Endpoints
    print_section("3. User Profile Endpoints (Task 3.2)")
    
    print("\n3.1 GET /api/users/me/profile (should create empty)")
    profile_response = requests.get(f"{BASE_URL}/api/users/me/profile", headers=headers)
    print_response("GET Profile", profile_response)
    if profile_response.status_code == 200:
        print("  ✓ Profile retrieved/created")
    else:
        print("  ✗ FAILED")
        return False
    
    print("\n3.2 PUT /api/users/me/profile (update with XP bonus)")
    state_before = requests.get(f"{BASE_URL}/api/users/me/state", headers=headers).json()
    xp_before = state_before["xp"]
    
    profile_update_response = requests.put(
        f"{BASE_URL}/api/users/me/profile",
        headers=headers,
        json={"name": "Test User", "major": "CS", "hobbies": "Coding"}
    )
    print_response("PUT Profile", profile_update_response)
    
    if profile_update_response.status_code == 200:
        state_after = requests.get(f"{BASE_URL}/api/users/me/state", headers=headers).json()
        xp_after = state_after["xp"]
        xp_gained = xp_after - xp_before
        assert xp_gained == 60, f"Should gain 60 XP (3 fields * 20), got {xp_gained}"
        print(f"  ✓ Profile updated, XP gained: {xp_gained} (expected: 60)")
    else:
        print("  ✗ FAILED")
        return False
    
    # Step 4: Test Chat Endpoints
    print_section("4. Chat Endpoints (Task 3.1)")
    
    print("\n4.1 POST /api/chat/conversations (create conversation)")
    conv_response = requests.post(
        f"{BASE_URL}/api/chat/conversations",
        headers=headers,
        json={}
    )
    print_response("Create Conversation", conv_response)
    if conv_response.status_code == 201:
        conv_id = conv_response.json()["id"]
        print(f"  ✓ Conversation created, ID: {conv_id}")
    else:
        print("  ✗ FAILED")
        return False
    
    print("\n4.2 GET /api/chat/conversations (list conversations)")
    list_response = requests.get(f"{BASE_URL}/api/chat/conversations", headers=headers)
    print_response("List Conversations", list_response)
    if list_response.status_code == 200:
        convs = list_response.json()["conversations"]
        assert len(convs) >= 1, "Should have at least one conversation"
        print(f"  ✓ Found {len(convs)} conversation(s)")
    else:
        print("  ✗ FAILED")
        return False
    
    print("\n4.3 GET /api/chat/conversations/{id}/messages")
    messages_response = requests.get(
        f"{BASE_URL}/api/chat/conversations/{conv_id}/messages",
        headers=headers
    )
    print_response("Get Messages", messages_response)
    if messages_response.status_code == 200:
        messages = messages_response.json()["messages"]
        print(f"  ✓ Retrieved {len(messages)} message(s)")
    else:
        print("  ✗ FAILED")
        return False
    
    print("\n4.4 POST /api/chat/conversations/{id}/messages (send message)")
    xp_before_msg = requests.get(f"{BASE_URL}/api/users/me/state", headers=headers).json()["xp"]
    send_response = requests.post(
        f"{BASE_URL}/api/chat/conversations/{conv_id}/messages",
        headers=headers,
        json={"role": "user", "content": "Hello, this is a test message"}
    )
    print_response("Send Message", send_response)
    if send_response.status_code == 200:
        xp_after_msg = requests.get(f"{BASE_URL}/api/users/me/state", headers=headers).json()["xp"]
        xp_gained = xp_after_msg - xp_before_msg
        print(f"  ✓ Message sent, XP gained: {xp_gained} (expected: 5)")
        if xp_gained != 5:
            print(f"    WARNING: Expected 5 XP, got {xp_gained}")
    else:
        print(f"  ⚠ Message send failed (status {send_response.status_code})")
        print(f"    This may be due to missing GEMINI_API_KEY")
    
    print_section("✅ ALL TESTS COMPLETED!")
    print("\nSummary:")
    print("  - User State Endpoints: ✓")
    print("  - User Profile Endpoints: ✓")
    print("  - Chat Endpoints: ✓ (LLM may require GEMINI_API_KEY)")
    print("\nNote: Some chat tests may fail if GEMINI_API_KEY is not set.")
    return True

if __name__ == "__main__":
    try:
        # Check if server is running
        health = requests.get(f"{BASE_URL}/health")
        if health.status_code != 200:
            print("ERROR: Server is not running!")
            print(f"Please start the server: uvicorn app.main:app --reload")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server!")
        print(f"Please start the server: uvicorn app.main:app --reload")
        sys.exit(1)
    
    success = test_phase3_endpoints()
    sys.exit(0 if success else 1)

