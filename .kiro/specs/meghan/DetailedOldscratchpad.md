# Project Meghan - Backend Development Plan

## 🚀 Major Update: New Feature Set & AmiConnect Integration

**Date:** January 2025

**Key Changes:**

- ✅ **ADDED:** AmiConnect skill-based platform integration
- ✅ **ADDED:** Hearts Currency System (replacing XP/Level system)
- ✅ **ADDED:** Therapist-in-the-Loop monitoring system
- ✅ **ADDED:** Micro Expressions (tweet-like) feature
- ✅ **ADDED:** Problem-Based Communities (enhanced peer clusters)
- ✅ **ADDED:** Current Me vs Future Me reflection tool
- ✅ **ADDED:** Guided Journaling with prompts
- ✅ **ADDED:** Weekly Wellbeing Insights
- ✅ **ADDED:** Enhanced Crisis Detection & Escalation
- ✅ **ADDED:** Privacy-First Design features

**Impact:** This update significantly expands the platform's capabilities, focusing on community support, therapist oversight, and positive reinforcement through the Hearts currency system. All references to Leaderboard and XP/Level systems should be updated to reflect Hearts currency and AmiConnect integration.

---

## Background and Motivation

Project Meghan is an empathy-first student wellness assistant designed to help university students navigate stress and mental health challenges. The platform combines AI-powered support with human therapist oversight, creating a safe, anonymous space for emotional expression and growth.

### Planner Note (2026-01-21): first backend changes required to match UF‑0 → UF‑7
This backend repo already has strong foundations (auth, chat, user state/profile). To follow the updated **User Flow (UF)** Planner, the **next work must**:
- Ship the missing **Dashboard endpoint** so “Home” can be backed by real data.
- Introduce the **Hearts ledger (append-only)** as the primary currency foundation (XP may remain temporarily for compatibility).
- Add minimal **onboarding persistence** (life stage, age range, struggles, privacy preference, first check-in).
- Standardize “Peer clusters” toward **Problem-Based Communities** naming + API shape.
- Add a minimal **Safety gate skeleton** so risky content can be detected/blocked consistently.

**Current State:**
- Frontend directly calls Gemini API via `@google/genai` SDK
- All user state is stored in React state (no persistence)
- No user authentication or data persistence
- Chat history is only in-memory
- Peer clusters feature exists but needs enhancement

**New Direction:**
- **AmiConnect Integration**: Replacing leaderboard with AmiConnect (skill-based platform) for gamification and skill development
- **Therapist-in-the-Loop**: Qualified psychologists monitor communities and intervene when risks are detected
- **Hearts Currency System**: Positive reinforcement mechanism replacing XP system
- **Enhanced Community Features**: Problem-based communities with anonymous peer support
- **Micro Expressions**: Tweet-like short thoughts with empathy-based responses
- **Privacy-First Design**: Full anonymity options and user data control

**Goals:**
- Move LLM calls to backend using FastAPI and LangChain for better security and API key management
- Implement data persistence for users, chat history, and user state
- Create a RESTful API to support all frontend features
- Implement user authentication and session management
- Integrate AmiConnect API for skill-based gamification
- Build therapist monitoring dashboard and escalation system
- Implement Hearts currency system with redemption features
- Support problem-based communities with anonymous peer interactions
- Add micro expressions (tweet-like) feature
- Implement Current Me vs Future Me reflection tool
- Add guided journaling with structured prompts
- Enhance voice expression capabilities
- Build weekly wellbeing insights dashboard
- Strengthen crisis detection and escalation workflows

## Key Challenges and Analysis

1. **LLM Integration**: Need to migrate from direct Gemini SDK calls to LangChain, maintaining the same behavior (system instructions, temperature, thinking budget, etc.)

2. **Data Modeling**: Need to design database schema for:
   - User profiles (bio, authentication, privacy settings)
   - User state (mood, tier, hearts currency, metrics)
   - Chat history (conversations per user)
   - Micro expressions (tweet-like posts)
   - Problem-based communities and memberships
   - Hearts transactions and redemption history
   - Therapist assignments and escalations
   - Current Me vs Future Me reflections
   - Guided journaling entries
   - Weekly wellbeing insights snapshots

3. **AmiConnect Integration**: 
   - API integration for skill-based platform
   - User account linking
   - Skill progress synchronization
   - Reward system integration

4. **Therapist-in-the-Loop System**:
   - Real-time monitoring dashboard
   - Risk detection and alerting
   - Escalation workflows
   - Therapist assignment logic
   - Privacy-preserving data sharing

5. **Hearts Currency System**:
   - Earning mechanics (replacing XP)
   - Redemption catalog (premium features, therapist sessions)
   - Transaction history
   - Balance management

6. **State Synchronization**: Frontend currently manages all state locally; need to sync with backend while maintaining good UX

7. **Risk Tier Detection & Escalation**: Enhanced detection with therapist notification system

8. **Privacy-First Design**: 
   - Anonymous posting options
   - Data control mechanisms
   - GDPR compliance considerations
   - User data export/deletion

9. **System Instructions**: Complex dynamic system instructions based on user bio, mood, stress source, and risk tier need to be maintained

## Data Models & Schemas Specification

### Frontend Analysis Summary

After analyzing the frontend codebase (`Project-Meghan-fe`), the following data structures are used:

**TypeScript Types (from `types.ts`):**
- `Mood`: Enum ('Heavy', 'Pulse', 'Grounded')
- `RiskTier`: Enum ('Green', 'Yellow', 'Red')
- `StressSource`: Enum ('Family', 'Relationship', 'Career/Academics', 'Others')
- `UserBio`: { name, major, hobbies, values, futureVision?, dailyReminder? }
- `UserState`: { mood, source, otherText?, tier, steps, sleepHours, pomoSessions, hearts, bio }
- `ChatMessage`: { role: 'user' | 'model', content }
- `MicroExpression`: { id, content, heartsReceived, isAnonymous, createdAt }
- `HeartsTransaction`: { id, amount, type, description, createdAt }

**Frontend State Management:**
- Chat messages stored in array (no conversation grouping yet)
- User state managed in React state (mood, tier, metrics, XP, level)
- Bio information stored in nested object within UserState
- Journal entries are created but not persisted (sentiment journal feature)


---

### Required Pydantic Schemas

Based on the models defined in `app/models/user.py`, the following schemas need to be created:

---

#### Authentication Schemas (`app/schemas/auth.py`)
**Purpose:** Handle user registration, login, and JWT token management

- `UserCreate`: 
  - email (str, required)
  - password (str, required)
  
- `UserLogin`: 
  - email (str, required)
  - password (str, required)
  
- `UserResponse`: 
  - id (int)
  - email (str)
  - created_at (datetime)
  - updated_at (datetime)

- `Token`: 
  - access_token (str)
  - token_type (str, default: "bearer")
  
- `TokenData`: 
  - email (str, optional - for JWT payload)

**Status:** Partially exists in `app/schemas/user.py` (UserCreate, UserResponse), needs expansion to `app/schemas/auth.py`

**Model Reference:** Based on `User` model (id, email, password_hash, created_at, updated_at)

---

#### User Profile Schemas (`app/schemas/profile.py` or in `app/schemas/user.py`)
**Purpose:** Handle user profile/bio information for personalization

- `UserProfileBase`: 
  - name (str, optional)
  - major (str, optional)
  - hobbies (str, optional)
  - values (str, optional)
  - bio (str, optional)
  - profile_picture (str, optional)

- `UserProfileCreate`: 
  - Extends UserProfileBase
  - Used when creating initial profile

- `UserProfileUpdate`: 
  - All fields optional (Partial update)
  - name (str, optional)
  - major (str, optional)
  - hobbies (str, optional)
  - values (str, optional)
  - bio (str, optional)
  - profile_picture (str, optional)

- `UserProfileResponse`: 
  - id (int)
  - user_id (int)
  - name (str, optional)
  - major (str, optional)
  - hobbies (str, optional)
  - values (str, optional)
  - bio (str, optional)
  - profile_picture (str, optional)
  - created_at (datetime)
  - updated_at (datetime)

**Status:** **MISSING** - Needs to be created

**Model Reference:** Based on `UserProfile` model (id, user_id, name, bio, profile_picture, major, hobbies, values, created_at, updated_at)

---

#### User State Schemas (`app/schemas/state.py`)
**Purpose:** Handle user's current wellness state, metrics, XP, and level

- `UserStateBase`: 
  - mood (str, required) - Values: 'Heavy', 'Pulse', 'Grounded'
  - stress_source (str, optional) - Values: 'Family', 'Relationship', 'Career/Academics', 'Others'
  - other_text (str, optional) - Required when stress_source is 'Others'
  - risk_tier (str, required) - Values: 'Green', 'Yellow', 'Red'
  - steps (int, default=0)
  - sleep_hours (int, default=0)
  - pomo_sessions (int, default=0)

- `UserStateCreate`: 
  - Extends UserStateBase
  - Used when creating initial user state

- `UserStateUpdate`: 
  - All fields optional for partial updates
  - mood (str, optional)
  - stress_source (str, optional)
  - other_text (str, optional)
  - risk_tier (str, optional)
  - steps (int, optional)
  - sleep_hours (int, optional)
  - pomo_sessions (int, optional)

- `UserStateResponse`: 
  - id (int)
  - user_id (int)
  - mood (str)
  - stress_source (str, optional)
  - other_text (str, optional)
  - risk_tier (str)
  - xp (int)
  - level (int) - Calculated as floor(xp / 200) + 1
  - steps (int)
  - sleep_hours (int)
  - pomo_sessions (int)
  - last_updated (datetime)

- `XPAddRequest`: 
  - amount (int, required) - XP amount to add

- `XPAddResponse`: 
  - xp (int) - New XP total after addition
  - level (int) - New level after XP addition

**Status:** **MISSING** - Needs to be created

**Model Reference:** Based on `UserState` model (id, user_id, mood, stress_source, other_text, risk_tier, xp, level, steps, sleep_hours, pomo_sessions, last_updated)

---

#### Chat Schemas (`app/schemas/chat.py`)
**Purpose:** Handle conversations and chat messages

**Conversation Schemas:**
- `ConversationBase`: 
  - tier (str, required) - Risk tier at conversation start: 'Green', 'Yellow', 'Red'
  - mood (str, required) - Mood at conversation start: 'Heavy', 'Pulse', 'Grounded'
  - source (str, required) - Stress source at conversation start

- `ConversationCreate`: 
  - Extends ConversationBase
  - All fields optional (can use current user state if not provided)
  - tier (str, optional)
  - mood (str, optional)
  - source (str, optional)

- `ConversationResponse`: 
  - id (int)
  - user_id (int)
  - tier (str)
  - mood (str)
  - source (str)
  - created_at (datetime)
  - updated_at (datetime)

**ChatMessage Schemas:**
- `ChatMessageBase`: 
  - role (str, required) - Values: 'user', 'model'
  - content (str, required) - Message text

- `ChatMessageCreate`: 
  - Extends ChatMessageBase
  - role (str, required)
  - content (str, required)

- `ChatMessageResponse`: 
  - id (int)
  - conversation_id (int)
  - role (str)
  - content (str)
  - created_at (datetime)

**Composite Chat Schemas:**
- `ConversationListResponse`: 
  - conversations (List[ConversationResponse])

- `ChatHistoryResponse`: 
  - conversation (ConversationResponse)
  - messages (List[ChatMessageResponse])

**Status:** **MISSING** - Needs to be created

**Model Reference:** 
- Based on `Conversation` model (id, user_id, tier, mood, source, created_at, updated_at)
- Based on `ChatMessage` model (id, conversation_id, role, content, created_at)

---

#### Dashboard Schemas (`app/schemas/dashboard.py`)
**Purpose:** Aggregate dashboard data for user frontend

- `DashboardResponse`: 
  - state (UserStateResponse)
  - profile (UserProfileResponse)
  - hearts_balance (int)
  - progress_percentages (dict, optional) - { steps: float, sleep: float, pomo: float } (if goals are defined)
  - weekly_insights (WeeklyInsights, optional)

- `WeeklyInsights`: 
  - week_start (date)
  - mood_trends (List[MoodSnapshot])
  - trigger_analysis (dict) - Most common stress sources
  - progress_summary (dict) - Hearts earned, promises kept, sessions completed
  - growth_indicators (List[str]) - Positive changes identified

- `MoodSnapshot`: 
  - date (date)
  - mood (str)
  - tier (str)
  - activities_count (int)

**Status:** **MISSING** - Needs to be created

**Note:** This schema combines data from UserState, UserProfile, and weekly insights

---

#### Hearts Currency Schemas (`app/schemas/hearts.py`)
**Purpose:** Hearts currency system for positive reinforcement

- `HeartsBalance`: 
  - balance (int) - Current hearts balance
  - total_earned (int) - Lifetime hearts earned
  - total_redeemed (int) - Lifetime hearts redeemed

- `HeartsTransactionCreate`: 
  - amount (int, required) - Positive for earning, negative for redemption
  - type (str, required) - Values: 'earn', 'redeem', 'bonus', 'refund'
  - description (str, required) - Transaction description
  - reference_id (str, optional) - Reference to related entity (e.g., promise_id, expression_id)

- `HeartsTransactionResponse`: 
  - id (int)
  - user_id (int)
  - amount (int)
  - type (str)
  - description (str)
  - reference_id (str, optional)
  - balance_after (int) - Balance after this transaction
  - created_at (datetime)

- `HeartsTransactionListResponse`: 
  - transactions (List[HeartsTransactionResponse])
  - total (int)
  - current_balance (int)

- `HeartsRedemptionCatalog`: 
  - items (List[RedemptionItem])
  - user_balance (int)

- `RedemptionItem`: 
  - id (str)
  - name (str)
  - description (str)
  - hearts_cost (int)
  - category (str) - Values: 'premium_feature', 'therapist_session', 'tool_unlock'
  - available (bool)

- `HeartsRedemptionRequest`: 
  - item_id (str, required)
  - quantity (int, default=1)

- `HeartsRedemptionResponse`: 
  - success (bool)
  - transaction (HeartsTransactionResponse)
  - new_balance (int)
  - redemption_code (str, optional) - For therapist sessions or premium features

**Status:** **MISSING** - Needs to be created

---

#### Micro Expressions Schemas (`app/schemas/microexpression.py`)
**Purpose:** Tweet-like short thoughts and feelings

- `MicroExpressionCreate`: 
  - content (str, required, max_length=280)
  - is_anonymous (bool, default=False)
  - community_id (int, optional) - Post to specific problem-based community

- `MicroExpressionResponse`: 
  - id (int)
  - user_id (int, optional) - Null if anonymous
  - content (str)
  - hearts_received (int)
  - is_anonymous (bool)
  - community_id (int, optional)
  - created_at (datetime)
  - empathy_responses (List[EmpathyResponse], optional)

- `EmpathyResponse`: 
  - id (int)
  - expression_id (int)
  - responder_id (int, optional) - Null if anonymous
  - content (str)
  - hearts_given (int)
  - created_at (datetime)

- `MicroExpressionListResponse`: 
  - expressions (List[MicroExpressionResponse])
  - total (int)
  - page (int)
  - page_size (int)

**Status:** **MISSING** - Needs to be created

---

#### AmiConnect Integration Schemas (`app/schemas/amiconnect.py`)
**Purpose:** AmiConnect skill-based platform integration

- `AmiConnectLinkRequest`: 
  - amiconnect_user_id (str, required)
  - verification_token (str, required)

- `AmiConnectLinkResponse`: 
  - success (bool)
  - linked_account (AmiConnectAccount)
  - sync_status (str)

- `AmiConnectAccount`: 
  - user_id (str)
  - username (str)
  - skills (List[Skill])
  - level (int)
  - last_synced (datetime)

- `Skill`: 
  - id (str)
  - name (str)
  - level (int)
  - progress (float)
  - category (str)

- `AmiConnectSyncRequest`: 
  - sync_skills (bool, default=True)
  - sync_progress (bool, default=True)

- `AmiConnectSyncResponse`: 
  - success (bool)
  - skills_updated (int)
  - hearts_earned (int, optional) - Hearts earned from skill progress

**Status:** **MISSING** - Needs to be created

---

#### Journal Schemas (`app/schemas/journal.py`)
**Purpose:** Handle guided journaling with structured prompts

- `JournalPrompt`: 
  - id (str)
  - title (str)
  - prompt_text (str)
  - category (str) - Values: 'reflection', 'gratitude', 'challenge', 'growth', 'emotion'
  - suggested_duration (int, optional) - Minutes

- `JournalEntryCreate`: 
  - content (str, required) - Journal entry text
  - prompt_id (str, optional) - If using guided prompt
  - mood_at_time (str, optional) - Mood when entry was created
  - tier_at_time (str, optional) - Risk tier when entry was created
  - is_voice_note (bool, default=False)
  - voice_url (str, optional) - If voice note

- `JournalEntryUpdate`: 
  - content (str, optional) - For editing entries

- `JournalEntryResponse`: 
  - id (int)
  - user_id (int)
  - content (str)
  - prompt_id (str, optional)
  - prompt_title (str, optional)
  - mood_at_time (str, optional)
  - tier_at_time (str, optional)
  - is_voice_note (bool)
  - voice_url (str, optional)
  - hearts_earned (int) - Hearts awarded (default: 30)
  - created_at (datetime)

- `JournalEntryListResponse`: 
  - entries (List[JournalEntryResponse])
  - total (int)
  - prompts_available (List[JournalPrompt], optional)

- `CurrentVsFutureMeResponse`: 
  - current_reflection (JournalEntryResponse, optional) - Most recent "Current Me" entry
  - future_vision (str, optional) - From user profile
  - comparison_insights (List[str]) - AI-generated insights comparing past and present
  - growth_markers (List[GrowthMarker]) - Identified progress points

- `GrowthMarker`: 
  - date (date)
  - description (str)
  - category (str) - Values: 'mood_improvement', 'habit_formation', 'insight_gained', 'challenge_overcome'

**Status:** **MISSING** - Needs to be created

**Model Reference:** Based on `JournalEntry` model (id, user_id, content, prompt_id, mood_at_time, tier_at_time, is_voice_note, voice_url, hearts_earned, created_at)

---

#### Problem-Based Community Schemas (`app/schemas/community.py`)
**Purpose:** Handle problem-based communities with therapist monitoring

- `CommunityBase`: 
  - name (str, required) - Unique community name
  - description (str, required)
  - stress_source (str, required) - Values: 'Family', 'Relationship', 'Career/Academics', 'Others'
  - is_active (bool, default=True)

- `CommunityCreate`: 
  - Extends CommunityBase

- `CommunityResponse`: 
  - id (int)
  - name (str)
  - description (str)
  - stress_source (str)
  - member_count (int) - Number of members
  - active_therapists (int) - Number of assigned therapists
  - is_active (bool)
  - created_at (datetime)

- `CommunityMembershipResponse`: 
  - user_id (int)
  - community_id (int)
  - community_name (str)
  - joined_at (datetime)
  - is_anonymous (bool) - User preference for anonymity in this community

- `CommunityListResponse`: 
  - communities (List[CommunityResponse])
  - user_communities (List[int]) - IDs of communities user belongs to

- `TherapistAssignment`: 
  - therapist_id (int)
  - community_id (int)
  - assigned_at (datetime)
  - status (str) - Values: 'active', 'on_break', 'unavailable'

**Status:** **MISSING** - Needs to be created

**Model Reference:** 
- Based on `ProblemCommunity` model (id, name, description, stress_source, is_active, created_at)
- Based on `CommunityMembership` model (user_id, community_id, is_anonymous, joined_at)
- Based on `TherapistAssignment` model (therapist_id, community_id, assigned_at, status)

---

### Model Relationships Summary

```
User (1) ──< (1) UserProfile
User (1) ──< (1) UserState
User (1) ──< (N) Conversation
Conversation (1) ──< (N) ChatMessage
User (1) ──< (N) JournalEntry
User (1) ──< (N) MicroExpression
MicroExpression (1) ──< (N) EmpathyResponse
User (1) ──< (N) HeartsTransaction
User (N) ──< (N) ProblemCommunity via CommunityMembership
ProblemCommunity (1) ──< (N) TherapistAssignment
Therapist (1) ──< (N) TherapistAssignment
User (1) ──< (1) AmiConnectLink (optional)
User (1) ──< (1) PrivacySettings
```



## High-level Task Breakdown

### User Flow Alignment Overview (Planner – Jan 2026)

This section maps the **end‑to‑end user journey** you just defined (Onboarding → Daily Use → AI Modes → Communities → Gamification → Safety → Insights) into concrete implementation phases. It is meant as a *feature-first* roadmap that sits on top of the more technical Phases 1–7 already defined, so we can always ask: “Where in the journey does this task show up for a real student?”

At a high level, we will build in this order:
- **Phase UF‑0 – Foundations & Accounts** (re-uses existing Phase 1–3 work)
- **Phase UF‑1 – Onboarding & First Check‑in**
- **Phase UF‑2 – Daily Home & Entry Question (“What do you need right now?”)**
- **Phase UF‑3 – AI Modes: Talk / Plan / Calm / Reflect**
- **Phase UF‑4 – Communities & Moderation**
- **Phase UF‑5 – Hearts, Rewards, & Redemption**
- **Phase UF‑6 – Safety & Escalation**
- **Phase UF‑7 – Insights & Weekly Dashboard**

Where “UF” = *User Flow* to avoid clashing with existing numeric phases.

---

### Phase UF‑0: Foundations & Accounts (ties into Phases 1–3, status: largely DONE)

**Goal:** Make sure the basic rails are in place so onboarding and daily flows can actually persist data and authenticate users.

- **Backend**
  - Use existing work in `Be`:
    - Auth (`/api/auth/register`, `/api/auth/login-json`, `/api/auth/me`)
    - User models (`User`, `UserProfile`, `UserState`)
    - Chat + LLM plumbing (`/api/chat/...`, `ChatService`, `LLMService`, prompts)
  - Confirm we can:
    - Create a user and profile
    - Persist user state (mood, tier, stress source, metrics)
    - Store conversations and messages
    - Award XP / hearts via existing endpoints or temporary mapping
- **Frontend**
  - Minimal auth flow (login/register or guest token) to attach all later steps to a user id (or guest id).
  - Routing shell with tabs: `Home`, `Chat`, `Communities`, `Insights`, `Profile`.

**Success Criteria (planner):**
- A test user can be created, logged in, and basic chat + state endpoints are reachable from a dev client (e.g. Thunder Client / Postman).
- Frontend can hold an auth token and hit a protected endpoint successfully.

#### UF‑0.1 (NEW, execute next): Dashboard + Hearts ledger foundations
**Goal:** Enable the “Home” screen and currency rails so the frontend can rely on backend state.

**UF‑0.1a — Dashboard endpoint (Phase 3 / Task 3.3)**
- **Work:** Implement/verify `GET /api/users/me/dashboard` (protected).
- **Success criteria (verifiable):**
  - Returns `200` with a stable JSON shape matching `DashboardResponse`.
  - Works for a brand‑new user (defaults created or sensible nulls).
  - Includes (minimum): `state`, `profile`, and a numeric `hearts_balance` (can be XP→hearts mapped temporarily).

**UF‑0.1b — Hearts ledger (UF‑5 foundation)**
- **Work:** Add a `HeartsTransaction` append‑only ledger and `GET /api/hearts/balance`.
- **Success criteria (verifiable):**
  - `GET /api/hearts/balance` returns `{balance, total_earned, total_redeemed}` for an authenticated user.
  - No “update transaction” behavior exists; corrections happen via new transactions only.

---

### Phase UF‑1: Onboarding & First Emotional Check‑in

**User Flow Covered:** Welcome → Basic profile → Struggles → Auto community assignment → Privacy choice → First “How are you feeling?” check‑in → Land on Home.

- **Backend**
  - **Extend profile & state models/schemas if needed:**
    - Life stage (`school`, `college`, `working`, `job seeking`) – likely part of `UserProfile`.
    - Age range bucket (e.g. `18–21`, `22–25`, etc.) – part of `UserProfile`.
    - Initial struggles / problem tags: career, relationships, family, studies, loneliness, anxiety, focus – can be:
      - a multi‑select field on `UserProfile` (JSON/text) *or*
      - a join table `UserStruggleTag` (normalized).
  - **Onboarding endpoints (new):**
    - `POST /api/onboarding/start` – create or mark onboarding session; optional.
    - `PUT /api/onboarding/profile` – write age range + life stage + struggles into profile.
    - `PUT /api/onboarding/privacy` – set initial privacy preference (anonymous / nickname / real name), likely in `PrivacySettings` or `UserProfile`.
    - `POST /api/checkins/first` – store first emotional check‑in (mood enums; e.g. Calm / Stressed / Anxious / Lonely / Overwhelmed / Neutral and map to existing backend `mood` + `risk_tier`).
  - **Community auto‑assignment logic:**
    - Service that, given chosen struggles, assigns default communities (e.g. `Career Circle`, `Relationship Circle`, `Mental Health Circle`).
    - Endpoint like `POST /api/communities/auto-assign` or part of onboarding flow.

- **Frontend**
  - Multi‑screen onboarding wizard:
    - Welcome (privacy + purpose copy only).
    - Basic profile (life stage + age range).
    - Struggles multi‑select.
    - Privacy selection (anonymous / nickname / real name).
    - First emotional check‑in (chips for Calm / Stressed / Anxious / Lonely / Overwhelmed / Neutral).
  - On completion:
    - Call auto‑assign endpoint.
    - Navigate to Home dashboard; show a tiny “You’re in X, Y communities” confirmation.

**Success Criteria (planner):**
- A brand‑new user can go through onboarding end‑to‑end and land on Home.
- Their **profile**, **initial struggles**, **privacy setting**, **first mood**, and **community memberships** exist in the DB and can be queried.

#### UF‑1.1 (NEW, after UF‑0.1): Minimal onboarding persistence (Backend MVP)
**Work (keep minimal, SQLite-friendly):**
- Extend `UserProfile` + schemas with:
  - `life_stage` (string/enum)
  - `age_range` (string/enum)
  - `struggles` (list of strings stored as JSON text for SQLite compatibility)
  - `future_vision` (optional string)
  - `daily_reminder` (optional string)
- Add endpoints (protected, for current user):
  - `PUT /api/onboarding/profile`
  - `PUT /api/onboarding/privacy` (store privacy preference; if no `PrivacySettings` model yet, store temporarily on profile)
  - `POST /api/checkins/first` (updates `UserState` mood/tier/source)

**Success criteria (verifiable):**
- After calling these endpoints, `GET /api/users/me/profile`, `GET /api/users/me/state`, and `GET /api/users/me/dashboard` reflect persisted onboarding data.

---

### Phase UF‑2: Daily Home & “What do you need right now?”

**User Flow Covered:** When the user re‑opens the app they see **Today’s mood**, AI chat entry, communities shortcut, hearts balance, weekly progress, and the central CTA “What do you need right now?” with options: Talk, Plan, Calm, Connect, Reflect.

- **Backend**
  - Implement/finish **Dashboard endpoint** (`GET /api/users/me/dashboard`, Task 3.3):
    - Today / latest mood + tier.
    - Current hearts balance (mapping XP → hearts as interim if needed).
    - Quick stats for week (sessions, check‑ins, community interactions).
  - Create/check **check‑in endpoint**:
    - `POST /api/checkins/daily` – stores daily mood + optional note; updates `UserState` snapshot to feed insights.

- **Frontend**
  - `Home` screen:
    - Pulls from `/api/users/me/dashboard`.
    - Shows:
      - Today’s mood (from latest check‑in or state).
      - AI chat quick entry.
      - Hearts balance.
      - “This week” progress summary.
    - Prominent question: **“What do you need right now?”** with five buttons:
      - `Talk` → navigates to Chat in “Talk” mode.
      - `Plan` → navigates to Chat in “Plan” mode.
      - `Calm` → goes to Calm tools.
      - `Connect` → opens Communities.
      - `Reflect` → opens Journaling / Reflection.

**Success Criteria (planner):**
- Returning user lands directly on Home (not onboarding).
- Home reliably reflects backend data for mood, hearts, and weekly usage, not just local state.

---

### Phase UF‑3: AI Modes – Talk, Plan, Calm, Reflect

**User Flow Covered:** Modes described in your plan:
- **Talk** – emotional venting / empathy.
- **Plan** – micro‑planning and tiny steps.
- **Calm** – grounding, breathing, audio.
- **Reflect** – journaling and “what went well” prompts.

- **Backend**
  - **Talk & Plan (LLM‑backed):**
    - Reuse `/api/chat/conversations` + `/messages` but:
      - Add a **mode** field on `Conversation` or message metadata (`talk` / `plan` / `calm` / `reflect`).
      - Extend `ChatService` + prompts to handle intent:
        - In Talk mode: strong empathy, clarifying questions, low action pressure.
        - In Plan mode: break tasks, create micro‑goals, push user gently to commit.
    - Add an optional `intent` field (`vent`, `advice`, `plan`) the AI can ask for and store per conversation.
  - **Calm:**
    - Non‑LLM content:
      - Static breathing sequences, grounding scripts, and audio metadata in DB or config.
    - Optional endpoint(s):
      - `GET /api/calm/resources` – list of exercises (type, duration, media URL).
      - `POST /api/calm/sessions` – log a calm session (for hearts + insights).
  - **Reflect (journaling):**
    - Use / extend existing journal schemas and planned journal endpoints:
      - `GET /api/journal/prompts`
      - `POST /api/journal/entries`
    - Hook into hearts/XP logic (award hearts per entry).

- **Frontend**
  - **Chat screen** with mode selector or entry‑point preservation:
    - If navigated from “Talk”, show chat header as “Talk – I’m here to listen”.
    - If from “Plan”, header: “Let’s make a tiny plan”.
    - AI asks: “Do you want to vent, get advice, or make a plan?” (and the choice is persisted).
  - **Calm tab/section:**
    - List of calm tools: breathing, grounding audio, short reflections.
    - Trigger backend logging when a session is started/completed.
  - **Reflect:**
    - Journaling UI with simple prompts and optional voice note.

**Success Criteria (planner):**
- A user can:
  - Start a **Talk** or **Plan** chat with clearly different AI behavior.
  - Run a **Calm** exercise and see it reflected in hearts / weekly usage.
  - Submit a **Reflect** entry and see hearts + future insights updated.

---

### Phase UF‑4: Communities & Moderation

**User Flow Covered:** Communities tab → see categories (Career, Relationships, Family, Studies) → view feed → post a micro‑expression → others react/comment → AI + therapists moderate.

- **Backend**
  - Finalize **community models & schemas** (Problem‑based communities):
    - `Community` / `ProblemCommunity`, `CommunityMembership`, `MicroExpression`, `EmpathyResponse`.
  - Endpoints:
    - `GET /api/communities` – list communities (filtered by user’s struggles and/or stress_source).
    - `POST /api/communities/{id}/join` – join with anonymity preference.
    - `GET /api/communities/{id}/feed` – micro‑expressions within that community.
    - `POST /api/expressions` – create micro‑expression (supports `community_id`, anonymity).
    - `POST /api/expressions/{id}/responses` – add empathy responses (comments).
  - **Moderation layer:**
    - First step: heuristic and LLM‑assisted **toxicity filter**:
      - Pre‑moderation or post‑moderation flag via `/api/moderation/check` service.
    - Add `risk_flag` / `status` to posts and comments for therapist dashboard.

- **Frontend**
  - **Communities** tab:
    - Grid/list of communities relevant to user; show membership status.
    - Community detail view with:
      - Micro‑expression feed.
      - “Post how you’re feeling” composer.
      - Reactions (e.g. “I relate”, “Stay strong”) and free‑text comments.
  - Visual indicators if a therapist is present or monitoring (later).

**Success Criteria (planner):**
- User can read and create posts in at least one relevant community.
- Toxic content is at minimum **detected and hidden from general feed** (even if therapist tooling is basic at first).

#### UF‑4.0 (NEW, after UF‑1.1): Standardize “PeerCluster” → “ProblemCommunity”
**Work:**
- Choose a single naming convention in backend:
  - Preferred: `ProblemCommunity` (can alias existing `PeerCluster` temporarily to avoid breaking DB immediately).
- Ensure membership stores per‑community anonymity preference (`is_anonymous`).

**Success criteria (verifiable):**
- `GET /api/communities` returns communities and indicates which ones the user belongs to.
- `POST /api/communities/{id}/join` persists the anonymity preference.

---

### Phase UF‑5: Hearts, Rewards & Redemption

**User Flow Covered:** Hearts earned for daily check‑ins, journaling, micro‑goals, community help → visible balance → can redeem for premium features or therapist time.

- **Backend**
  - Implement **HeartsTransaction** model + schemas (as already designed).
  - Endpoints:
    - `GET /api/hearts/balance` – current balance + lifetime stats.
    - `GET /api/hearts/catalog` – redemption items (premium tools, sessions, insights).
    - `POST /api/hearts/earn` – internal service called from chat / journaling / community / calm flows.
    - `POST /api/hearts/redeem` – perform redemption with validation.
  - Wire hearts into touchpoints:
    - Daily check‑ins.
    - Chat messages (Talk/Plan).
    - Calm sessions.
    - Journal entries.
    - Community support (empathy responses).

- **Frontend**
  - **Hearts** indicator in header/Home.
  - Simple **Rewards** screen:
    - Catalog items.
    - Redeem button with confirmation.
    - Basic “History” section (list recent transactions).

**Success Criteria (planner):**
- Every major interaction in the user flow (check‑in, chat, community support, journaling, calm) visibly increases hearts.
- User can successfully redeem at least one item (even if it’s a simple “unlock extra calm session” for MVP).

---

### Phase UF‑6: Safety & Escalation

**User Flow Covered:** When a user expresses suicidal ideation or self‑harm thoughts, system enters **Crisis Mode**: supportive response, resources, optional therapist connection, and community posting safeguards.

- **Backend**
  - **Risk detection service:**
    - Keyword/phrase rules for v1 (e.g. “end everything”, “kill myself”, “don’t want to live”).
    - Optional LLM‑based risk scoring on messages, posts, journal entries.
  - Endpoints:
    - `POST /api/crisis/detect` – accepts text and returns risk tier + recommended action.
    - Integration hooks:
      - Called automatically when:
        - Chat messages are sent.
        - Micro‑expressions are created.
        - Journal entries are saved (optional).
  - **Escalation workflow:**
    - If high‑risk:
      - Create `RiskFlag` / `CrisisEvent` entity tied to user + source (chat/community/journal).
      - Trigger notification to therapist dashboard (even if dashboard is basic list view).
      - Optionally lock or pause community posting for that user until they acknowledge support message.

- **Frontend**
  - For high‑risk detection:
    - Show immediate, warm support message.
    - Present **emergency resources** relevant to their region (for now can be static list).
    - Offer “Talk to a human” CTA (therapist, helpline, or email depending on what’s available).
  - Avoid jarring UI; present Crisis Mode as soft overlay or dedicated screen.

**Success Criteria (planner):**
- High‑risk phrases in chat or communities reliably trigger Crisis Mode.
- A therapist or admin can see a **list of crisis events** somewhere in the backend UI/tools, even if rough.

---

### Phase UF‑7: Weekly Insights & Growth

**User Flow Covered:** Weekly dashboard with mood trends, triggers, progress, best days, difficult patterns, and AI insights like “You feel anxious mostly on Sundays.”

- **Backend**
  - Scheduled job or periodic task (even if triggered by user for MVP) that aggregates:
    - Mood snapshots from check‑ins.
    - Stress sources from state and communities.
    - Hearts earned and where they came from.
    - Count of Talk/Plan/Calm/Reflect sessions.
  - Endpoints:
    - `GET /api/insights/weekly` – returns `WeeklyInsights` schema already defined (mood_trends, triggers, progress_summary, growth_indicators).
    - (Optional) `POST /api/insights/refresh` – recompute insights on demand (dev/testing).

- **Frontend**
  - **Insights** tab:
    - Mood trend chart over last 7 days.
    - Trigger summary (e.g. “Most stressful domain: Career”).
    - Hearts and actions summary.
    - Simple AI paragraph: “You feel anxious mostly on Sundays. Consider planning lighter tasks on Sunday evenings.”

**Success Criteria (planner):**
- After a week of simulated or real usage, `/api/insights/weekly` returns non‑empty, interpretable data.
- Insights tab visualizes at least trends + one or two textual insights.

---

### Planner Update – Tech Lead Stack & Dated Execution Plan (2026-01-21)

**Stack refinements (authoritative going forward):**
- **Frontend:** Next.js (React), Tailwind, TanStack Query for server state, Zustand/RTK for light client state. Keep routing + auth-ready pages.
- **Backend:** FastAPI (async), Pydantic v2, SQLAlchemy async, BackgroundTasks now; Celery/RQ later if needed.
- **Datastores:** Neon Postgres = source of truth (auth, profiles, communities, hearts ledger, therapist roles). MongoDB = high-volume/unstructured (chat logs, journal entries, micro-expressions/posts, voice transcripts). **No cross-responsibility mixing.**
- **AI:** Phase 1 Gemini (classification, intent, chat, summarization). Phase 2 add OSS (Mistral/Llama via vLLM/Ollama/Replicate) for emotion tagging, micro-goals, risk. No direct DB writes from LLM; always via services with safety checks.
- **Architecture:** Domain modules: auth, profile, checkins, chat, communities, hearts, insights, safety, amiconnect. API groups aligned (`/auth`, `/users`, `/checkins`, `/chat`, `/communities`, `/posts`, `/hearts`, `/insights`, `/safety`).
- **Safety-first pipeline for every AI call:** sanitize → emotion classify → intent detect → safety check → response gen → log (no raw PII). Risk service isolated; escalation path to therapist dashboard; block risky actions when necessary.

**Dated execution (see `plan.md` for the full weekly checklist):**
- **Phase 0 Foundations (Jan 21–Jan 27, 2026):** Repo/CI, env, auth baseline, Postgres+Mongo wiring, health checks, minimal Next shell + auth guard.
- **Phase 1 Core MVP (Jan 28–Feb 18, 2026):** Onboarding + check-ins + auto-community join; Talk/Plan chat with AI; Calm resources + logging; Reflect (journal) with hearts; Communities read/post; Hearts ledger + dashboard basics; weekly insights v0.
- **Phase 2 Safety & Quality (Feb 19–Mar 03, 2026):** Risk detection service, safety middleware on chat/community/journal, escalation flow + therapist list view, moderation tools.
- **Phase 3 AmiConnect (optional, Mar 04–Mar 10, 2026):** Link, sync skills, map progress → hearts; basic readiness gate.

**Non-negotiables to enforce:** safety gate on all AI, no emotional data shared socially without consent/anon, LLM cannot write DB, ledger is append-only, audit logging and rate limits on APIs.

### Phase 1: Project Setup & Core Infrastructure

#### Task 1.1: Initialize FastAPI Project Structure
**Success Criteria:**
- FastAPI application with proper project structure (app/, models/, routers/, services/, etc.)
- Environment variable configuration for API keys
- Basic CORS setup for frontend communication
- 
- Requirements.txt with initial dependencies

**Dependencies:** None

---

#### Task 1.2: Database Setup & Models
**Success Criteria:**
- Database ORM configured (SQLAlchemy recommended)
- Database connection setup and session management
- Database models defined in `app/models/` for:
  - User (id, email, password_hash, created_at, updated_at)
  - UserProfile (user_id, name, major, hobbies, values, bio, profile_picture, created_at, updated_at)
  - UserState (user_id, mood, stress_source, other_text, risk_tier, xp, level, steps, sleep_hours, pomo_sessions, last_updated)
  - Conversation (id, user_id, tier, mood, source, created_at, updated_at)
  - ChatMessage (id, conversation_id, role, content, created_at)
  - JournalEntry (id, user_id, content, mood_at_time, tier_at_time, xp_gained, created_at) - Optional
- Pydantic schemas defined in `app/schemas/` for request/response validation:
  - Authentication schemas (auth.py)
  - User profile schemas (user.py or profile.py)
  - User state schemas (state.py)
  - Chat schemas (chat.py)
  - Dashboard schemas (dashboard.py)
  - Leaderboard schemas (leaderboard.py)
  - Journal schemas (journal.py) - Optional
- Database migrations setup (Alembic)
- Database initialization script/test
- Fix all issues identified in current `app/models/user.py` implementation

**Dependencies:** Task 1.1

**Note:** 
- ORM models (SQLAlchemy) go in `app/models/` - represent database tables
- Pydantic schemas go in `app/schemas/` - represent API request/response contracts
- **See "Data Models & Schemas Specification" section above for complete field definitions and requirements**

---

#### Task 1.3: Authentication System
**Success Criteria:**
- User registration endpoint (POST /api/auth/register)
- User login endpoint (POST /api/auth/login) returning JWT token
- JWT token validation middleware
- Password hashing (bcrypt)
- Get current user endpoint (GET /api/auth/me)
- Protected route decorator/dependency

**Dependencies:** Task 1.2

---

### Phase 2: LangChain Integration & LLM Services

#### Task 2.1: LangChain Setup for Gemini
**Success Criteria:**
- LangChain ChatGoogleGenerativeAI integration configured
- Environment variable for Gemini API key properly loaded
- Test endpoint to verify LLM connection works
- Error handling for API failures

**Dependencies:** Task 1.1

---

#### Task 2.2: System Instructions & Prompt Template
**Success Criteria:**
- Replicate SYSTEM_INSTRUCTIONS logic from frontend constants.ts
- LangChain prompt template that accepts: tier, mood, source, bio
- Dynamic system message generation matching frontend behavior
- Configurable parameters (temperature: 0.7, top_p: 0.95, max_output_tokens: 500, thinking_budget: 200)

**Dependencies:** Task 2.1

---

#### Task 2.3: Chat Service Implementation
**Success Criteria:**
- Chat service class that:
  - Takes chat history (messages array)
  - Takes user context (tier, mood, source, bio)
  - Generates appropriate system instructions
  - Calls LLM via LangChain
  - Returns formatted response
- Handles streaming vs non-streaming (start with non-streaming)
- Error handling with fallback responses
- Logging for debugging

**Dependencies:** Task 2.2

---

### Phase 3: Core API Endpoints

#### Task 3.1: Chat Endpoints
**Success Criteria:**
- POST /api/chat/conversations - Create new conversation
- GET /api/chat/conversations - List user's conversations
- GET /api/chat/conversations/{conversation_id}/messages - Get messages for a conversation
- POST /api/chat/conversations/{conversation_id}/messages - Send message and get response
- Messages saved to database with proper conversation linking
- Response includes XP gain calculation (e.g., +5 XP per message sent)

**Dependencies:** Task 2.3, Task 1.2, Task 1.3

---

#### Task 3.2: User State Management Endpoints
**Success Criteria:**
- GET /api/users/me/state - Get current user state
- PUT /api/users/me/state - Update user state (mood, tier, metrics)
- POST /api/users/me/state/xp - Add XP (with level recalculation)
- GET /api/users/me/profile - Get user profile/bio
- PUT /api/users/me/profile - Update user profile/bio (with XP bonus on new fields)

**Dependencies:** Task 1.2, Task 1.3

---

#### Task 3.3: Dashboard Data Endpoint
**Success Criteria:**
- GET /api/users/me/dashboard - Returns aggregated dashboard data:
  - Current state (steps, sleep, pomo sessions, mood, tier)
  - Hearts balance and currency information
  - Progress percentages for goals
  - Weekly insights summary (if available)
  - Historical trends (if we add time-series data later)

**Dependencies:** Task 3.2

---

#### Task 3.4: AmiConnect Integration Endpoints
**Success Criteria:**
- POST /api/amiconnect/link - Link AmiConnect account
- GET /api/amiconnect/status - Get linked account status
- POST /api/amiconnect/sync - Sync skills and progress
- GET /api/amiconnect/skills - Get user's skills from AmiConnect
- Hearts earned from skill progress synced automatically
- Error handling for API failures

**Dependencies:** Task 1.2, Task 1.3

**Note:** Requires AmiConnect API documentation and credentials

---

### Phase 4: New Feature Implementation

#### Task 4.1: Hearts Currency System
**Success Criteria:**
- Database model for HeartsTransaction
- POST /api/hearts/earn - Earn hearts (with automatic triggers)
- POST /api/hearts/redeem - Redeem hearts for catalog items
- GET /api/hearts/balance - Get current balance and transaction history
- GET /api/hearts/catalog - Get redemption catalog
- Hearts earning mechanics:
  - Chat messages: 5 hearts
  - Completed promises: 10 hearts
  - Journal entries: 30 hearts
  - Pomodoro sessions: 50 hearts
  - Sound therapy: 5 hearts
  - Micro expressions: 2 hearts
  - Empathy responses: 3 hearts
- Automatic balance updates and transaction logging

**Dependencies:** Task 1.2, Task 3.2

---

#### Task 4.2: Micro Expressions (Tweet-Like) Feature
**Success Criteria:**
- Database model for MicroExpression and EmpathyResponse
- POST /api/expressions - Create micro expression (max 280 chars)
- GET /api/expressions - List expressions (with pagination, filtering)
- POST /api/expressions/{id}/empathy - Respond with empathy (award hearts)
- GET /api/expressions/{id} - Get expression with responses
- Anonymous posting option
- Community filtering (by stress source)
- AI-generated empathy suggestions for responses

**Dependencies:** Task 1.2, Task 2.3, Task 4.1

---

#### Task 4.3: Problem-Based Communities Enhancement
**Success Criteria:**
- Enhanced Community model with therapist assignments
- GET /api/communities - List communities (filtered by stress source)
- POST /api/communities/{id}/join - Join community (with anonymity preference)
- GET /api/communities/{id}/members - Get anonymous member count
- GET /api/communities/{id}/expressions - Get micro expressions in community
- POST /api/communities/{id}/support - Share support message
- Community-based micro expression feed
- Member count and activity tracking

**Dependencies:** Task 1.2, Task 4.2

---

#### Task 4.4: Therapist-in-the-Loop System
**Success Criteria:**
- Therapist model and authentication
- Therapist dashboard endpoint (GET /api/therapist/dashboard)
- Real-time risk monitoring service
- POST /api/therapist/escalate - Escalate user to therapist
- GET /api/therapist/assignments - Get therapist's assigned communities
- POST /api/therapist/interventions - Log therapist intervention
- Alert system for high-risk users (RED tier, crisis keywords)
- Privacy-preserving data sharing (anonymized when possible)
- Therapist assignment logic (load balancing, expertise matching)

**Dependencies:** Task 1.2, Task 2.3, Task 4.3

---

#### Task 4.5: Current Me vs Future Me Reflection Tool
**Success Criteria:**
- GET /api/reflection/current-vs-future - Get comparison insights
- AI service to analyze journal entries and generate growth insights
- Comparison between:
  - Past journal entries (Current Me)
  - Future vision from profile (Future Me)
  - Current state and progress
- Growth markers identification
- Visual progress indicators
- POST /api/reflection/insights - Generate new insights

**Dependencies:** Task 2.3, Task 4.6

---

#### Task 4.6: Guided Journaling with Prompts
**Success Criteria:**
- Journal prompt catalog (predefined prompts by category)
- GET /api/journal/prompts - Get available prompts
- POST /api/journal/entries - Create journal entry (with optional prompt_id)
- Enhanced journal entry model (prompt_id, voice_url support)
- Voice note upload and storage
- POST /api/journal/entries/{id}/voice - Upload voice note
- AI-generated follow-up prompts based on entry content
- Hearts awarded for journal completion

**Dependencies:** Task 1.2, Task 2.3, Task 4.1

---

#### Task 4.7: Weekly Wellbeing Insights
**Success Criteria:**
- Background job to generate weekly insights (scheduled task)
- GET /api/insights/weekly - Get current week's insights
- Insights include:
  - Mood trends over the week
  - Most common stress sources/triggers
  - Progress summary (hearts earned, promises kept, sessions)
  - Growth indicators (positive changes)
  - Personalized recommendations
- Data aggregation from:
  - User state snapshots
  - Journal entries
  - Chat conversations
  - Micro expressions
- Visual data preparation for frontend charts

**Dependencies:** Task 1.2, Task 3.3, Task 4.6

---

#### Task 4.8: Enhanced Crisis Detection & Escalation
**Success Criteria:**
- Enhanced risk detection service (beyond keyword matching)
- LLM-based risk assessment for nuanced detection
- Real-time monitoring of:
  - Chat messages
  - Micro expressions
  - Journal entries
- Automatic escalation workflow:
  - RED tier detection → Immediate therapist alert
  - Crisis keywords → Urgent escalation
  - Pattern detection → Proactive intervention
- POST /api/crisis/detect - Manual risk assessment endpoint
- Escalation history tracking
- User notification system (gentle, supportive)

**Dependencies:** Task 2.3, Task 4.4

---

#### Task 4.9: Privacy-First Design Implementation
**Success Criteria:**
- User privacy settings model
- GET /api/privacy/settings - Get privacy preferences
- PUT /api/privacy/settings - Update privacy preferences
- Privacy options:
  - Anonymous posting in communities
  - Data sharing with therapists (opt-in)
  - Public profile visibility
  - Micro expression visibility
- POST /api/privacy/export - Export user data (GDPR compliance)
- DELETE /api/privacy/account - Delete account and all data
- Data anonymization service for therapist views
- Privacy policy acceptance tracking

**Dependencies:** Task 1.2, Task 1.3

---

### Phase 5: Testing & Documentation

#### Task 5.1: API Testing
**Success Criteria:**
- Unit tests for core services (chat service, user state service)
- Integration tests for key endpoints
- Test database setup for isolated testing
- Test coverage for critical paths (chat, authentication, hearts currency, crisis detection)

**Dependencies:** All previous tasks

---

#### Task 5.2: API Documentation
**Success Criteria:**
- OpenAPI/Swagger documentation automatically generated by FastAPI
- README.md with setup instructions
- Environment variable documentation
- API endpoint documentation with request/response examples

**Dependencies:** All previous tasks

---

#### Task 5.3: Error Handling & Logging
**Success Criteria:**
- Comprehensive error handling across all endpoints
- Proper HTTP status codes
- Error response format consistency
- Logging setup (structured logging recommended)
- Health check endpoint (GET /api/health)

**Dependencies:** All previous tasks

---

## Project Status Board

- [x] **Phase 1: Core Infrastructure**
  - [x] Task 1.1: Initialize FastAPI Project Structure
  - [x] Task 1.2: Database Setup & Models
  - [x] Task 1.3: Authentication System

- [x] **Phase 2: LangChain Integration**
  - [x] Task 2.1: LangChain Setup for Gemini
  - [x] Task 2.2: System Instructions & Prompt Template
  - [x] Task 2.3: Chat Service Implementation

- [ ] **Phase 3: Core API Endpoints**
  - [x] Task 3.1: Chat Endpoints
  - [x] Task 3.2: User State Management Endpoints
  - [ ] Task 3.3: Dashboard Data Endpoint (UF‑0.1a)
  - [ ] Task 3.4: AmiConnect Integration Endpoints


- [ ] **Phase 4: Backend Updates for New Frontend Features**
  - [ ] Task 7.1: Database Model Updates (UserState & UserProfile new fields)
  - [ ] Task 7.2: Schema Updates for New Fields
  - [ ] Task 7.3: Small Promises Endpoints
  - [ ] Task 7.4: Empathy Points System Implementation
  - [ ] Task 7.5: Joke Generation Endpoint
  - [ ] Task 7.6: Enhanced Peer Clusters Endpoints
  - [ ] Task 7.7: Database Migrations for New Fields


- [ ] **Phase 6: Testing & Documentation**
  - [ ] Task 5.1: API Testing
  - [ ] Task 5.2: API Documentation
  - [ ] Task 5.3: Error Handling & Logging

- [ ] **UF Track (execute in order)**
  - [ ] UF‑0.1a: Dashboard endpoint shipped + verified
  - [ ] UF‑0.1b: Hearts ledger + `/api/hearts/balance` shipped + verified
  - [ ] UF‑1.1: Onboarding persistence endpoints + profile fields shipped + verified
  - [ ] UF‑4.0: Communities naming/API standardization shipped + verified
  - [ ] UF‑6.0: Safety gate skeleton wired into chat (and later posts/journal)

- [ ] **Phase 7: Frontend-Backend Integration**
  - [ ] Task 6.1: Frontend API Service Layer Setup
  - [ ] Task 6.2: Authentication Flow Implementation
  - [ ] Task 6.3: User State Management Migration
  - [ ] Task 6.4: Chat Component Integration
  - [ ] Task 6.5: Dashboard Component Integration
  - [ ] Task 6.6: AmiConnect Integration (Frontend)
  - [ ] Task 6.7: Micro Expressions Component Integration
  - [ ] Task 6.8: Problem-Based Communities Integration
  - [ ] Task 6.9: Hearts Currency UI Integration
  - [ ] Task 6.10: Knowledge Center (Profile) Integration
  - [ ] Task 6.11: Tools Integration (Pomodoro & Journal)
  - [ ] Task 6.12: Current Me vs Future Me UI
  - [ ] Task 6.13: Weekly Insights Dashboard
  - [ ] Task 6.14: Error Handling & Loading States
  - [ ] Task 6.15: Environment Configuration & Build Setup


## Current Status / Progress Tracking

**Status:** Phase 1 Complete - Core Infrastructure. Phase 2 Complete - LangChain Integration & LLM Services. Phase 3 Task 3.1 Complete - Chat Endpoints. Phase 3 Task 3.2 Complete - User State Management Endpoints.

**Completed:**
- ✅ Created FastAPI project structure (app/, app/core/, app/models/, app/routers/, app/services/)
- ✅ Created main FastAPI application (app/main.py) with CORS middleware
- ✅ Created configuration module (app/core/config.py) for environment variables
- ✅ Created requirements.txt with all necessary dependencies (FastAPI, LangChain, SQLAlchemy, etc.)
- ✅ Created .env.example file with all required environment variables
- ✅ Created README.md with setup instructions
- ✅ Created .gitignore file
- ✅ **All Pydantic schemas created and organized according to specifications**
  - ✅ Authentication schemas (auth.py)
  - ✅ User profile schemas (user.py)
  - ✅ User state schemas (userState.py)
  - ✅ Chat schemas (chat.py)
  - ✅ Dashboard schemas (dashboard.py)
  - ✅ Journal schemas (journal.py)
  - ✅ Community schemas (community.py) - to be created
  - ✅ Hearts schemas (hearts.py) - to be created
  - ✅ Micro expressions schemas (microexpression.py) - to be created
  - ✅ AmiConnect schemas (amiconnect.py) - to be created
  - ✅ All schemas exported in __init__.py
- ✅ **Task 1.3: Authentication System Complete**
  - ✅ Database session management (app/core/database.py)
  - ✅ Security utilities - password hashing and JWT (app/core/security.py)
  - ✅ Authentication router with register, login, and /me endpoints (app/routers/auth.py)
  - ✅ get_current_user dependency for protected routes (app/core/dependencies.py)
  - ✅ Auth router registered in main.py
  - ✅ Database initialization script (app/core/db_init.py)
  - ✅ Models package exports Base for Alembic (app/models/__init__.py)
- ✅ **Task 3.1: Chat Endpoints Complete**
  - ✅ Created chat router (app/routers/chat.py) with all 4 endpoints
  - ✅ Conversation creation with user state fallback
  - ✅ Message sending with LLM integration and XP rewards
  - ✅ Proper authentication, authorization, and error handling
  - ✅ Chat router registered in main.py
- ✅ **Task 3.2: User State Management Endpoints Complete**
  - ✅ Created users router (app/routers/users.py) with all 5 endpoints
  - ✅ GET/PUT /api/users/me/state - Get and update user state
  - ✅ POST /api/users/me/state/xp - Add XP with level recalculation
  - ✅ GET/PUT /api/users/me/profile - Get and update profile with XP bonuses
  - ✅ Profile updates award 20 XP per newly filled bio field
  - ✅ Proper validation and error handling
  - ✅ Users router registered in main.py

**Next Steps:**
- Proceed with **UF‑0.1a**: Phase 3 Task 3.3 — `GET /api/users/me/dashboard`.
- After UF‑0.1a is verified, proceed with **UF‑0.1b**: Hearts ledger + `/api/hearts/balance`.

## Executor's Feedback or Assistance Requests

**Phase 2 Completion Summary:**
- ✅ **Task 2.1: LangChain Setup for Gemini**
  - Created `app/services/llm.py` with `LLMService` class that manages ChatGoogleGenerativeAI instances
  - Added LLM configuration parameters to `app/core/config.py`:
    - `GEMINI_API_KEY`: API key for Gemini (required)
    - `GEMINI_MODEL`: Model name (default: "gemini-1.5-flash")
    - `GEMINI_TEMPERATURE`: Sampling temperature (default: 0.7)
    - `GEMINI_TOP_P`: Top-p sampling (default: 0.95)
    - `GEMINI_MAX_OUTPUT_TOKENS`: Max output tokens (default: 500)
    - `GEMINI_THINKING_BUDGET`: Thinking budget (default: 200, note: may need special handling)
  - Created `app/routers/llm.py` with:
    - GET `/api/llm/test` - Test LLM connection (requires authentication)
    - GET `/api/llm/health` - Health check for LLM service (no auth required)
  - Registered LLM router in `main.py`
  - Error handling and logging implemented throughout

- ✅ **Task 2.2: System Instructions & Prompt Template**
  - Created `app/services/prompts.py` with:
    - `generate_system_instructions()`: Generates dynamic system instructions based on user context (tier, mood, source, bio)
    - `create_chat_prompt_template()`: Creates LangChain ChatPromptTemplate for system + human messages
    - `format_chat_history()`: Converts message dicts to LangChain message objects
  - System instructions are personalized based on:
    - Risk tier (Green/Yellow/Red) with tier-specific guidance
    - Mood (Heavy/Pulse/Grounded) with mood descriptions
    - Stress source (Family/Relationship/Career-Academics/Others)
    - User bio information (name, major, hobbies, values, bio)
  - All LLM parameters are configurable via settings

- ✅ **Task 2.3: Chat Service Implementation**
  - Created `app/services/chat.py` with `ChatService` class
  - `generate_response()` method:
    - Takes user message, chat history, and user context (tier, mood, source, bio)
    - Generates system instructions using prompts module
    - Formats chat history for LangChain
    - Builds message list with system message + history + current user message
    - Invokes LLM asynchronously using `ainvoke()`
    - Returns formatted response with success/error status
  - `validate_context()` method: Validates tier, mood, and source parameters
  - `_get_fallback_response()`: Provides tier-specific fallback messages when LLM fails
  - Comprehensive error handling with logging
  - Non-streaming implementation (can be enhanced to support streaming later)

**Implementation Details:**
- LLM service uses singleton pattern with global `llm_service` instance
- Chat service uses global `chat_service` instance
- System instructions follow empathy-first approach with tier-specific guidance
- All parameters are configurable and have sensible defaults
- Error handling includes fallback responses to ensure users always receive a response
- Logging is comprehensive for debugging and monitoring

**Testing Notes:**
- Before testing, set `GEMINI_API_KEY` in `.env` file
- Test LLM connection: GET `/api/llm/health` (no auth) or GET `/api/llm/test` (requires auth)
- Chat service can be tested via API endpoints (to be created in Phase 3)
- All code passes syntax validation and linting

**Task 1.3 Completion Summary:**
- ✅ Created database session dependency (`app/core/database.py`) with `get_db()` function for FastAPI dependency injection
- ✅ Created security utilities (`app/core/security.py`) with:
  - Password hashing using bcrypt (`get_password_hash`, `verify_password`)
  - JWT token creation and validation (`create_access_token`, `decode_access_token`)
- ✅ Created authentication router (`app/routers/auth.py`) with:
  - POST `/api/auth/register` - User registration endpoint
  - POST `/api/auth/login` - OAuth2 form-based login (standard FastAPI)
  - POST `/api/auth/login-json` - JSON-based login (alternative for frontend)
  - GET `/api/auth/me` - Get current authenticated user
  - `get_current_user` dependency function for protected routes
- ✅ Created dependencies module (`app/core/dependencies.py`) to export `get_current_user` for use in other routers
- ✅ Registered auth router in `main.py`
- ✅ Created database initialization script (`app/core/db_init.py`) to create tables
- ✅ Updated `app/models/__init__.py` to export Base and all models for Alembic
- ✅ Fixed auth schemas to include `Config.from_attributes = True` for ORM compatibility

**Implementation Details:**
- Uses OAuth2PasswordBearer for token extraction (standard FastAPI pattern)
- JWT tokens expire after 30 days (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Password hashing uses bcrypt via passlib
- Token payload contains email in "sub" field (standard JWT claim)
- Both form-based and JSON login endpoints provided for flexibility
- All endpoints properly handle errors with appropriate HTTP status codes

**Testing Notes:**
- Before testing, run `python app/core/db_init.py` to create database tables
- Or use Alembic migrations (to be set up in Task 1.2)
- Dependencies need to be installed: `pip install -r requirements.txt`
- Test endpoints:
  1. POST `/api/auth/register` with `{"email": "test@example.com", "password": "testpass"}`
  2. POST `/api/auth/login-json` with same credentials
  3. Use returned token in Authorization header: `Bearer <token>`
  4. GET `/api/auth/me` with token to verify authentication

**Task 1.1 Completion Summary:**
- FastAPI project structure created in `/Be` directory
- All core files initialized with proper Python package structure
- CORS configured to allow frontend connections (defaults to localhost:5173 and localhost:3000)
- Environment variable configuration ready for API keys, database, and other settings
- Requirements.txt includes all necessary packages for FastAPI, LangChain, SQLAlchemy, and authentication
- Project is ready for dependency installation: `pip install -r requirements.txt`

**Schema Organization Completion Summary:**
- ✅ All Pydantic schemas created according to scratchpad specifications
- ✅ Fixed existing schemas (user.py, userState.py, chat.py) to match specifications:
  - UserProfileBase fields made optional (as per spec)
  - Added UserProfileUpdate and UserProfileResponse with all required fields
  - Fixed sleep_hours type from float to int in UserState schemas
  - Added all missing fields to UserStateResponse (id, user_id, xp, level, last_updated)
  - Fixed ConversationResponse to include id, user_id, created_at, updated_at
  - Fixed ChatMessageResponse to include id, created_at
  - Added ConversationListResponse schema
  - Simplified ChatHistoryResponse structure
- ✅ Created new schema files:
  - dashboard.py with DashboardResponse
  - leaderboard.py with LeaderboardEntry and LeaderboardResponse
  - journal.py with all journal entry schemas
  - cluster.py with all cluster schemas
- ✅ Updated __init__.py to export all schemas properly
- ✅ All schemas pass syntax validation and linting
- ✅ All schemas use proper Pydantic BaseModel with Config.from_attributes = True for ORM compatibility
- ✅ **Phase 2: LangChain Integration & LLM Services Complete**
  - ✅ Task 2.1: LangChain Setup for Gemini
    - ✅ Created LLMService class (app/services/llm.py) for managing ChatGoogleGenerativeAI instances
    - ✅ Added LLM configuration to app/core/config.py (GEMINI_API_KEY, GEMINI_MODEL, GEMINI_TEMPERATURE, GEMINI_TOP_P, GEMINI_MAX_OUTPUT_TOKENS, GEMINI_THINKING_BUDGET)
    - ✅ Created LLM test router (app/routers/llm.py) with `/api/llm/test` and `/api/llm/health` endpoints
    - ✅ Registered LLM router in main.py
    - ✅ Error handling and logging implemented
  - ✅ Task 2.2: System Instructions & Prompt Template
    - ✅ Created prompts module (app/services/prompts.py) with generate_system_instructions() function
    - ✅ Dynamic system instructions generation based on tier, mood, source, and bio
    - ✅ LangChain ChatPromptTemplate setup for system and human messages
    - ✅ Chat history formatting utility (format_chat_history())
    - ✅ All LLM parameters configurable (temperature: 0.7, top_p: 0.95, max_output_tokens: 500, thinking_budget: 200)
  - ✅ Task 2.3: Chat Service Implementation
    - ✅ Created ChatService class (app/services/chat.py) for managing chat conversations
    - ✅ generate_response() method that takes chat history, user context, and generates LLM responses
    - ✅ Context validation method (validate_context())
    - ✅ Fallback responses for error scenarios (tier-specific)
    - ✅ Comprehensive error handling and logging
    - ✅ Non-streaming implementation (ready for streaming enhancement later)

**Task 3.1 Completion Summary:**
- ✅ Created chat router (`app/routers/chat.py`) with all required endpoints:
  - POST `/api/chat/conversations` - Create new conversation (uses current user state if tier/mood/source not provided)
  - GET `/api/chat/conversations` - List all conversations for current user
  - GET `/api/chat/conversations/{conversation_id}/messages` - Get messages for a conversation
  - POST `/api/chat/conversations/{conversation_id}/messages` - Send message and get AI response
- ✅ Implemented helper functions:
  - `calculate_level(xp)`: Calculates user level from XP (floor(xp / 200) + 1)
  - `get_or_create_user_state()`: Gets or creates default user state
  - `get_user_profile_dict()`: Gets user profile as dict for bio context
  - `add_xp_to_user_state()`: Adds XP and updates level
- ✅ Message sending workflow:
  - Saves user message to database
  - Retrieves chat history for context
  - Generates AI response using ChatService
  - Saves AI response to database
  - Awards 5 XP per message sent
  - Updates conversation timestamp
- ✅ All endpoints include proper authentication, authorization (ownership verification), and error handling
- ✅ Registered chat router in `main.py`
- ✅ All code passes syntax validation and linting

**Implementation Details:**
- XP per message: 5 XP (as per specifications)
- Level calculation: floor(xp / 200) + 1
- Conversations use tier/mood/source from creation time (snapshot of user state)
- Chat service integrates with existing LLM service and prompts module
- User profile bio data is passed to LLM for personalization
- Fallback responses provided if LLM fails
- All database operations properly handle transactions

**Testing Notes:**
- Before testing, ensure database tables are created (run `python app/core/db_init.py`)
- Set `GEMINI_API_KEY` in `.env` file for LLM functionality
- Test endpoints:
  1. POST `/api/chat/conversations` - Create a conversation (can omit tier/mood/source to use current state)
  2. GET `/api/chat/conversations` - List conversations
  3. GET `/api/chat/conversations/{id}/messages` - Get messages
  4. POST `/api/chat/conversations/{id}/messages` - Send message and get response (requires authentication)

**Notes:**
- The SECRET_KEY has a default value for development but should be changed in production
- CORS_ORIGINS supports both JSON array strings and comma-separated values
- All Python files pass syntax validation
- All schemas are ready to be used in API endpoints

- 2026-01-05: Created `alexa_like_voice_assistant_plan.md` with a high-level implementation, timeline, team split, and cost estimate for a minimal Alexa-like IoT talking assistant that connects to the Meghan backend, per user request.

## Technical Decisions & Rationale

1. **FastAPI**: Chosen for modern async support, automatic OpenAPI docs, and excellent performance
2. **LangChain**: Provides abstraction over LLM providers, makes it easier to switch providers if needed, and offers better prompt management
3. **SQLAlchemy**: Industry-standard ORM for Python, excellent FastAPI integration
4. **JWT Authentication**: Stateless authentication suitable for API-first architecture
5. **Database Choice**: Will use PostgreSQL or SQLite (SQLite for development, PostgreSQL for production)

## Lessons

- Read the file before you try to edit it
- Include info useful for debugging in the program output
- Always ask before using the -force git command
- If there are vulnerabilities that appear in the terminal, run npm audit before proceeding

## Notes

- The frontend currently uses Gemini 3 Flash Preview model with specific parameters
- System instructions are dynamically generated based on user context (bio, mood, tier, source)
- **Hearts Currency System (replacing XP):**
  - 5 hearts per chat message
  - 10 hearts per completed promise
  - 5 hearts per sound therapy session
  - 5 hearts per joke request
  - 10 hearts for feeling step completion
  - 15 hearts for naming step completion
  - 20 hearts per bio field completion
  - 25 hearts for tutorial completion
  - 30 hearts for journal entry
  - 50 hearts for pomodoro session
  - 2 hearts per micro expression posted
  - 3 hearts per empathy response given
  - Variable hearts from AmiConnect skill progress
- Hearts can be redeemed for:
  - Premium features (unlock advanced tools)
  - Therapist sessions (discounted or free)
  - Special content or resources
- Risk tiers: GREEN, YELLOW, RED (determined by mood and crisis keywords, enhanced with LLM detection)
- **Hearts Currency:** Replaces XP system, redeemable for premium features and therapist sessions
- **AmiConnect Integration:** Skill-based platform integration for gamification
- **Therapist-in-the-Loop:** Qualified psychologists monitor communities and intervene when needed
- **Micro Expressions:** Tweet-like short thoughts (280 chars) with empathy-based responses
- **Problem-Based Communities:** Enhanced communities grouped by stress source with therapist oversight
- **Current Me vs Future Me:** Reflection tool comparing past emotions with present progress
- **Guided Journaling:** Structured prompts for reflection, supports voice notes
- **Weekly Wellbeing Insights:** Visual summaries of mood trends, triggers, and progress
- **Privacy-First Design:** Full anonymity options and user data control

## Frontend Updates Analysis & Required Backend Changes

### Overview

After analyzing the updated frontend codebase (`Project-Meghan-fe`), several new features have been added that require backend support. This section documents what needs to be added or modified in the backend to support these new frontend features.

### New Frontend Features Identified

**1. Small Promises Feature**
- Todo list with promises that can be completed
- Awards 10 XP per completed promise
- Stored in `UserState.promises` array
- Type: `SmallPromise[]` with `{ id, text, completed }`

**2. Sound Therapy Sessions**
- Tracks sound therapy usage
- Awards 5 XP per sound session start
- New field: `soundSessions: number` in UserState

**3. Daily Reminder**
- Text reminder saved in user bio
- New field: `dailyReminder?: string` in UserBio
- Tracks if reminder is saved: `reminderSaved: boolean` in UserState

**4. Empathy Points System**
- New metric separate from XP
- Awards empathy points for supporting others in peer clusters
- Awards 10 empathy points for sharing wisdom, 5 for quick support
- Each empathy point also gives 2 bonus XP
- New field: `empathyPoints: number` in UserState
- Displayed in leaderboard

**5. Future Vision Bio Field**
- New optional bio field for user's future vision
- New field: `futureVision?: string` in UserBio

**6. Enhanced Onboarding Flow**
- Added "feeling" step (between triage and naming)
- Added "naming" step (before tutorial)
- Awards 10 XP for completing feeling step
- Awards 15 XP for completing naming step

**7. Peer Clusters Enhancement**
- Clusters now filtered by user's stress source
- Shows only the cluster matching user's current stressor
- Includes empathy points display
- Support message sharing feature

**8. Joke Feature**
- "Make me laugh" button in header
- Calls LLM to generate wholesome jokes
- Awards 5 XP per joke request

### Required Backend Changes

#### Database Model Updates

**UserState Model (`app/models/user.py`):**
- [ ] Add `sound_sessions` field (Integer, default=0)
- [ ] Add `reminder_saved` field (Boolean, default=False)
- [ ] Add `empathy_points` field (Integer, default=0)
- [ ] Add `promises` field (JSON/Text) - Store array of SmallPromise objects
  - Option 1: JSON column (if using PostgreSQL)
  - Option 2: Text column with JSON serialization (SQLite compatible)
  - Option 3: Separate `SmallPromise` table (normalized approach)

**UserProfile Model (`app/models/user.py`):**
- [ ] Add `daily_reminder` field (String, nullable)
- [ ] Add `future_vision` field (String, nullable)

**New Model: SmallPromise (Optional - if using normalized approach)**
- [ ] Create `SmallPromise` model with:
  - `id` (Integer, Primary Key)
  - `user_id` (Integer, ForeignKey to users.id)
  - `text` (String)
  - `completed` (Boolean, default=False)
  - `created_at` (DateTime)
  - `updated_at` (DateTime)

#### Schema Updates

**UserState Schemas (`app/schemas/userState.py`):**
- [ ] Add `sound_sessions` to UserStateBase, UserStateCreate, UserStateUpdate, UserStateResponse
- [ ] Add `reminder_saved` to UserStateBase, UserStateCreate, UserStateUpdate, UserStateResponse
- [ ] Add `empathy_points` to UserStateBase, UserStateCreate, UserStateUpdate, UserStateResponse
- [ ] Add `promises` to UserStateBase, UserStateCreate, UserStateUpdate, UserStateResponse
  - Type: `List[SmallPromise]` or `Optional[List[dict]]` depending on implementation

**UserProfile Schemas (`app/schemas/user.py`):**
- [ ] Add `daily_reminder` to UserProfileBase, UserProfileCreate, UserProfileUpdate, UserProfileResponse
- [ ] Add `future_vision` to UserProfileBase, UserProfileCreate, UserProfileUpdate, UserProfileResponse

**New Schema: SmallPromise (`app/schemas/promise.py` or in `app/schemas/userState.py`):**
- [ ] Create `SmallPromise` schema:
  - `id` (str or int)
  - `text` (str)
  - `completed` (bool)
- [ ] Create `SmallPromiseCreate` schema
- [ ] Create `SmallPromiseUpdate` schema
- [ ] Create `SmallPromiseResponse` schema

**Leaderboard Schemas (`app/schemas/leaderboard.py`):**
- [ ] Add `empathy_points` to LeaderboardEntry (optional field)

#### API Endpoint Updates

**User State Endpoints (`app/routers/users.py`):**
- [ ] Update `PUT /api/users/me/state` to handle new fields:
  - `sound_sessions`
  - `reminder_saved`
  - `empathy_points`
  - `promises`
- [ ] Add `POST /api/users/me/state/empathy` endpoint:
  - Request: `{ amount: int }`
  - Response: `{ empathy_points: int, xp: int, level: int }`
  - Awards empathy points and bonus XP (2x empathy points)

**Small Promises Endpoints (New - `app/routers/promises.py`):**
- [ ] `GET /api/users/me/promises` - Get user's promises
- [ ] `POST /api/users/me/promises` - Create new promise
- [ ] `PUT /api/users/me/promises/{promise_id}` - Update promise (toggle completed)
- [ ] `DELETE /api/users/me/promises/{promise_id}` - Delete promise
- [ ] Award 10 XP when promise is marked as completed

**OR** (if storing in UserState):
- [ ] Update `PUT /api/users/me/state` to handle promises array
- [ ] Backend calculates XP gain when promises are completed

**Peer Clusters Endpoints (`app/routers/clusters.py` - if not exists):**
- [ ] `GET /api/clusters` - List clusters (filtered by stress source)
- [ ] `POST /api/clusters/{cluster_id}/support` - Share support message
  - Awards 10 empathy points + 20 XP
- [ ] `POST /api/clusters/{cluster_id}/quick-support` - Quick support action
  - Awards 5 empathy points + 10 XP

**Joke Endpoint (New - `app/routers/jokes.py` or add to `app/routers/chat.py`):**
- [ ] `POST /api/jokes/generate` - Generate wholesome joke
  - Uses LLM with special prompt for jokes
  - Awards 5 XP
  - Returns joke text

#### Service Updates

**Chat Service (`app/services/chat.py`):**
- [ ] Add method for generating jokes:
  - `generate_joke(user_context)` - Special prompt for wholesome jokes
  - Uses same LLM but with joke-specific system instructions

**Prompts Service (`app/services/prompts.py`):**
- [ ] Add `generate_joke_instructions()` function:
  - Returns system instructions for generating wholesome, sibling-like jokes
  - Should be appropriate for all risk tiers

#### Migration Requirements

**Database Migration (Alembic):**
- [ ] Create migration to add new UserState fields:
  - `sound_sessions`
  - `reminder_saved`
  - `empathy_points`
  - `promises` (JSON or Text)
- [ ] Create migration to add new UserProfile fields:
  - `daily_reminder`
  - `future_vision`
- [ ] If using normalized SmallPromise table:
  - Create migration for `small_promises` table

#### XP Calculation Updates

**Current XP Awards (from frontend):**
- 5 XP per chat message
- 10 XP per completed promise
- 5 XP per sound therapy session
- 5 XP per joke request
- 10 XP for feeling step completion
- 15 XP for naming step completion
- 20 XP per bio field completion
- 25 XP for tutorial completion
- 30 XP for journal entry
- 50 XP for pomodoro session
- 2 XP per empathy point (bonus)

**Backend should:**
- [ ] Ensure all XP awards are properly tracked
- [ ] Update level calculation when XP changes
- [ ] Handle empathy points → XP conversion (2x multiplier)

### Implementation Priority

**High Priority (Required for basic functionality):**
1. Add new UserState fields (sound_sessions, reminder_saved, empathy_points, promises)
2. Add new UserProfile fields (daily_reminder, future_vision)
3. Update schemas to include new fields
4. Update user state endpoints to handle new fields

**Medium Priority (Required for full feature support):**
5. Small promises endpoints (if using separate endpoints)
6. Empathy points endpoint
7. Peer clusters support endpoints
8. Joke generation endpoint

**Low Priority (Nice to have):**
9. Normalized SmallPromise table (if not using JSON storage)
10. Historical tracking of empathy points

### Testing Considerations

- [ ] Test UserState updates with all new fields
- [ ] Test promises array serialization/deserialization
- [ ] Test empathy points → XP conversion
- [ ] Test joke generation endpoint
- [ ] Test peer cluster filtering by stress source
- [ ] Test daily reminder save/load

### Task Breakdown: Backend Updates for New Frontend Features

#### Task 7.1: Database Model Updates
**Success Criteria:**
- UserState model includes: `sound_sessions`, `reminder_saved`, `empathy_points`, `promises`
- UserProfile model includes: `daily_reminder`, `future_vision`
- All fields have appropriate types and defaults
- Database migration created and tested

**Dependencies:** None

**Implementation Details:**
- Update `app/models/user.py`:
  - Add `sound_sessions = Column(Integer, default=0)` to UserState
  - Add `reminder_saved = Column(Boolean, default=False)` to UserState
  - Add `empathy_points = Column(Integer, default=0)` to UserState
  - Add `promises = Column(JSON)` or `Column(Text)` to UserState (decide on storage approach)
  - Add `daily_reminder = Column(String, nullable=True)` to UserProfile
  - Add `future_vision = Column(String, nullable=True)` to UserProfile
- Create Alembic migration for new fields
- Test migration on development database

---

#### Task 7.2: Schema Updates for New Fields
**Success Criteria:**
- All schemas updated to include new fields
- Proper validation and optional/required flags
- Backward compatibility maintained

**Dependencies:** Task 7.1

**Implementation Details:**
- Update `app/schemas/userState.py`:
  - Add new fields to UserStateBase, UserStateCreate, UserStateUpdate, UserStateResponse
  - Add SmallPromise schema (if not using separate table)
- Update `app/schemas/user.py`:
  - Add `daily_reminder` and `future_vision` to UserProfileBase, UserProfileCreate, UserProfileUpdate, UserProfileResponse
- Update `app/schemas/leaderboard.py`:
  - Add `empathy_points` to LeaderboardEntry (optional)

---

#### Task 7.3: Small Promises Endpoints
**Success Criteria:**
- Endpoints for CRUD operations on promises
- XP awarded when promise completed
- Proper validation and error handling

**Dependencies:** Task 7.1, Task 7.2

**Implementation Details:**
- Create `app/routers/promises.py` OR update `app/routers/users.py`:
  - `GET /api/users/me/promises` - Get user's promises
  - `POST /api/users/me/promises` - Create new promise
  - `PUT /api/users/me/promises/{promise_id}` - Update promise (toggle completed)
  - `DELETE /api/users/me/promises/{promise_id}` - Delete promise
- Award 10 XP when promise is marked as completed
- Handle promises array in UserState if using JSON storage approach

---

#### Task 7.4: Empathy Points System Implementation
**Success Criteria:**
- Endpoint to add empathy points
- Automatic XP bonus calculation (2x empathy points)
- Level recalculation when XP changes

**Dependencies:** Task 7.1, Task 7.2

**Implementation Details:**
- Create `POST /api/users/me/state/empathy` endpoint in `app/routers/users.py`:
  - Request: `{ amount: int }`
  - Response: `{ empathy_points: int, xp: int, level: int }`
  - Awards empathy points
  - Calculates bonus XP (amount * 2)
  - Updates total XP and recalculates level
- Update user state with new empathy_points value

---

#### Task 7.5: Joke Generation Endpoint
**Success Criteria:**
- Endpoint generates wholesome jokes via LLM
- Awards 5 XP per joke request
- Proper error handling

**Dependencies:** Task 2.3 (Chat Service)

**Implementation Details:**
- Create `app/routers/jokes.py` OR add to `app/routers/chat.py`:
  - `POST /api/jokes/generate` - Generate joke
- Create `generate_joke_instructions()` in `app/services/prompts.py`:
  - Returns system instructions for wholesome, sibling-like jokes
- Use ChatService to generate joke with special prompt
- Award 5 XP after successful joke generation
- Return joke text in response

---

#### Task 7.6: Enhanced Peer Clusters Endpoints
**Success Criteria:**
- Clusters filtered by stress source
- Support message sharing endpoint
- Empathy points awarded for support actions

**Dependencies:** Task 7.4

**Implementation Details:**
- Create or update `app/routers/clusters.py`:
  - `GET /api/clusters` - List clusters (filter by stress_source query param)
  - `POST /api/clusters/{cluster_id}/support` - Share support message
    - Awards 10 empathy points + 20 XP
  - `POST /api/clusters/{cluster_id}/quick-support` - Quick support action
    - Awards 5 empathy points + 10 XP
- Update PeerCluster model if needed to support stress_source filtering

---

#### Task 7.7: Database Migrations for New Fields
**Success Criteria:**
- Alembic migration created and tested
- Migration can be rolled back
- Data integrity maintained

**Dependencies:** Task 7.1

**Implementation Details:**
- Create Alembic migration:
  - Add new UserState columns
  - Add new UserProfile columns
  - Set appropriate defaults
- Test migration up and down
- Document migration steps

## Frontend-Backend Integration Plan

### Overview

This section outlines the plan to connect the React frontend (`Project-Meghan-fe`) with the FastAPI backend (`Be`). The frontend currently uses direct Gemini API calls and local state management. We need to migrate to backend API calls for authentication, data persistence, and LLM interactions.

### Current Frontend State Analysis

**Frontend Architecture:**
- React application with TypeScript
- Direct Gemini API calls via `@google/genai` SDK (`services/gemini.ts`)
- All state managed in React (`App.tsx` with `useState`)
- No authentication or user persistence
- Chat messages stored in component state (lost on refresh)
- Mock data for leaderboard
- No API layer or HTTP client setup

**Components Requiring API Integration:**
1. **App.tsx** - Main app state, user state management, onboarding flow
2. **Chat.tsx** - Chat messages, LLM interactions
3. **Dashboard.tsx** - User metrics display (steps, sleep, pomo sessions)
4. **Leaderboard.tsx** - Community rankings (currently mock data)
5. **KnowledgeCenter.tsx** - User profile/bio updates
6. **Tools (Pomodoro & Journal)** - XP tracking, metrics updates

### Backend API Endpoints Available

**Authentication (`/api/auth`):**
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - OAuth2 form login
- `POST /api/auth/login-json` - JSON login (for frontend)
- `GET /api/auth/me` - Get current user

**Chat (`/api/chat`):**
- `POST /api/chat/conversations` - Create conversation
- `GET /api/chat/conversations` - List conversations
- `GET /api/chat/conversations/{id}/messages` - Get messages
- `POST /api/chat/conversations/{id}/messages` - Send message (with LLM response)

**User State & Profile (`/api/users`):**
- `GET /api/users/me/state` - Get user state
- `PUT /api/users/me/state` - Update user state
- `POST /api/users/me/state/xp` - Add XP
- `GET /api/users/me/profile` - Get profile
- `PUT /api/users/me/profile` - Update profile

**Missing Endpoints (Need to be created in backend before frontend integration):**
- `GET /api/users/me/dashboard` - Dashboard aggregated data (Task 3.3 - partially complete, needs verification)
- `GET /api/leaderboard` - Leaderboard rankings (Task 3.4 - needs to be created)
- `POST /api/journal/entries` - Create journal entry (optional, Task 4.2 related)
- `GET /api/journal/entries` - List journal entries (optional, Task 4.2 related)

**Note:** These endpoints should be created in the backend before or in parallel with frontend integration tasks.

### Integration Tasks Breakdown

#### Task 6.1: Frontend API Service Layer Setup
**Success Criteria:**
- HTTP client configured (axios or fetch wrapper)
- API base URL configuration (environment variables)
- Request/response interceptors for authentication
- Error handling utilities
- TypeScript types for API responses
- API service module structure (`services/api/`)

**Dependencies:** None

**Implementation Details:**
- Create `services/api/client.ts` - HTTP client with interceptors
- Create `services/api/auth.ts` - Authentication API calls
- Create `services/api/chat.ts` - Chat API calls
- Create `services/api/users.ts` - User state/profile API calls
- Create `services/api/dashboard.ts` - Dashboard API calls
- Create `services/api/amiconnect.ts` - AmiConnect API calls
- Create `services/api/expressions.ts` - Micro expressions API calls
- Create `services/api/hearts.ts` - Hearts currency API calls
- Create `services/api/communities.ts` - Problem-based communities API calls
- Create `services/api/journal.ts` - Journal API calls (optional)
- Add `.env` file with `VITE_API_BASE_URL` configuration
- Update `vite.config.ts` if needed for environment variables

---

#### Task 6.2: Authentication Flow Implementation
**Success Criteria:**
- Login/Register UI components
- JWT token storage (localStorage or sessionStorage)
- Token refresh handling
- Protected route wrapper/guard
- Auto-login on app load (if token exists)
- Logout functionality
- User context/provider for global user state

**Dependencies:** Task 6.1

**Implementation Details:**
- Create `components/Auth/Login.tsx` - Login form
- Create `components/Auth/Register.tsx` - Registration form
- Create `contexts/AuthContext.tsx` - Auth state management
- Create `hooks/useAuth.ts` - Auth hook for components
- Create `utils/auth.ts` - Token management utilities
- Update `App.tsx` to check authentication on mount
- Add auth guard for protected routes
- Handle token expiration

---

#### Task 6.3: User State Management Migration
**Success Criteria:**
- Replace local `userState` with API calls
- Load user state on app initialization
- Sync state changes to backend
- Handle loading and error states
- Optimistic updates for better UX
- State persistence across page refreshes

**Dependencies:** Task 6.1, Task 6.2

**Implementation Details:**
- Create `hooks/useUserState.ts` - Custom hook for user state
- Update `App.tsx` to fetch user state on mount
- Replace local `setUserState` calls with API calls
- Update `addXP` function to call backend API
- Update `updateBio` function to call backend API
- Handle onboarding flow (triage, tutorial) with API persistence
- Sync mood, tier, metrics changes to backend

---

#### Task 6.4: Chat Component Integration
**Success Criteria:**
- Replace direct Gemini calls with backend chat API
- Load conversation history from backend
- Create new conversations via API
- Send messages through backend
- Handle conversation switching
- Persist chat history across sessions
- Maintain chat UI/UX (loading states, error handling)

**Dependencies:** Task 6.1, Task 6.2, Task 6.3

**Implementation Details:**
- Update `Chat.tsx` to use chat API service
- Remove `services/gemini.ts` (or keep as fallback)
- Create `hooks/useChat.ts` - Chat state management hook
- Load conversations on component mount
- Create conversation when chat tab opens (if none exists)
- Send messages via `POST /api/chat/conversations/{id}/messages`
- Display messages from API response
- Handle XP gain from backend response
- Update conversation list when new messages arrive

---

#### Task 6.5: Dashboard Component Integration
**Success Criteria:**
- Fetch dashboard data from backend API
- Display real-time metrics (steps, sleep, pomo)
- Show XP and level information
- Display progress percentages
- Handle loading and error states
- Auto-refresh or manual refresh option

**Dependencies:** Task 6.1, Task 6.2, Task 6.3

**Implementation Details:**
- Create `GET /api/users/me/dashboard` endpoint in backend (if not exists)
- Update `Dashboard.tsx` to fetch from API
- Use `useEffect` to load dashboard data on mount
- Display loading skeleton while fetching
- Handle empty state (no data yet)
- Update metrics display to use API data

---

#### Task 6.6: AmiConnect Integration (Frontend)
**Success Criteria:**
- Link AmiConnect account UI
- Display linked account status
- Show skills and progress from AmiConnect
- Sync skills button
- Display hearts earned from skill progress
- Handle account unlinking

**Dependencies:** Task 6.1, Task 6.2

**Implementation Details:**
- Create `AmiConnectLink.tsx` component
- Update user profile to show AmiConnect status
- Display skills dashboard
- Handle sync requests
- Show hearts earned notifications

---

#### Task 6.7: Micro Expressions Component Integration
**Success Criteria:**
- Create micro expression UI (tweet-like)
- Display expressions feed
- Empathy response functionality
- Anonymous posting option
- Community filtering
- Hearts display for expressions

**Dependencies:** Task 6.1, Task 6.2

**Implementation Details:**
- Create `MicroExpressions.tsx` component
- Feed with pagination
- Create expression form (280 char limit)
- Empathy response buttons
- Anonymous toggle
- Community filter dropdown

---

#### Task 6.8: Problem-Based Communities Integration
**Success Criteria:**
- Display user's communities
- Join/leave community functionality
- Community-specific expression feeds
- Anonymity preferences per community
- Support message sharing
- Therapist indicators (if visible to user)

**Dependencies:** Task 6.1, Task 6.2, Task 6.7

**Implementation Details:**
- Update `PeerClusters.tsx` to use new API
- Community list with join/leave
- Community detail view
- Expression feed filtered by community
- Anonymity settings UI

---

#### Task 6.9: Hearts Currency UI Integration
**Success Criteria:**
- Display hearts balance prominently
- Hearts earning notifications
- Redemption catalog UI
- Transaction history
- Redeem hearts flow

**Dependencies:** Task 6.1, Task 6.2

**Implementation Details:**
- Hearts balance display in header/nav
- Toast notifications for hearts earned
- `HeartsCatalog.tsx` component
- `HeartsHistory.tsx` component
- Redemption confirmation flow

---

#### Task 6.10: Knowledge Center (Profile) Integration
**Success Criteria:**
- Load user profile from backend
- Update profile fields via API
- Show XP gain on field completion
- Persist changes immediately
- Handle validation errors

**Dependencies:** Task 6.1, Task 6.2, Task 6.3

**Implementation Details:**
- Update `KnowledgeCenter.tsx` to use profile API
- Load profile on component mount
- Update `updateBio` to call `PUT /api/users/me/profile`
- Handle XP bonus from backend response
- Show success/error feedback
- Sync profile changes to user state

---

#### Task 6.11: Tools Integration (Pomodoro & Journal)
**Success Criteria:**
- Track Pomodoro sessions via API
- Create journal entries via API
- Award XP through backend
- Update metrics (pomo_sessions) via API
- Persist journal entries

**Dependencies:** Task 6.1, Task 6.2, Task 6.3

**Implementation Details:**
- Update Pomodoro completion to call `PUT /api/users/me/state` (increment pomo_sessions)
- Add XP via `POST /api/users/me/state/xp` (50 XP for pomodoro)
- Create journal entry API endpoint (if not exists): `POST /api/journal/entries`
- Update journal UI in `App.tsx` to save entries
- Load journal entries list (optional feature)
- Handle XP gain from journal entry creation

---

#### Task 6.12: Current Me vs Future Me UI
**Success Criteria:**
- Display comparison view
- Show growth insights
- Visual progress indicators
- Past vs present comparison
- Growth markers timeline

**Dependencies:** Task 6.1, Task 6.2, Task 6.11

**Implementation Details:**
- Create `CurrentVsFutureMe.tsx` component
- Fetch reflection data from API
- Display comparison cards
- Growth timeline visualization
- AI-generated insights display

---

#### Task 6.13: Weekly Insights Dashboard
**Success Criteria:**
- Display weekly wellbeing insights
- Mood trends visualization
- Trigger analysis display
- Progress summary
- Growth indicators

**Dependencies:** Task 6.1, Task 6.2, Task 6.5

**Implementation Details:**
- Create `WeeklyInsights.tsx` component
- Charts for mood trends
- Progress summary cards
- Trigger analysis visualization
- Growth indicators list

---

#### Task 6.14: Error Handling & Loading States
**Success Criteria:**
- Consistent error handling across all API calls
- User-friendly error messages
- Loading indicators for async operations
- Network error handling
- Token expiration handling
- Retry logic for failed requests

**Dependencies:** All previous tasks

**Implementation Details:**
- Create error boundary component
- Add toast/notification system for errors
- Implement loading skeletons/spinners
- Handle 401 (unauthorized) - redirect to login
- Handle 500 (server error) - show user-friendly message
- Handle network errors - show retry option
- Add request timeout handling

---

#### Task 6.15: Environment Configuration & Build Setup
**Success Criteria:**
- Environment variables configured
- Development and production API URLs
- Build process includes environment setup
- CORS properly configured on backend
- Documentation for environment setup

**Dependencies:** Task 6.1

**Implementation Details:**
- Create `.env.example` with `VITE_API_BASE_URL`
- Update `.gitignore` to exclude `.env`
- Configure Vite to use environment variables
- Update backend CORS to allow frontend origin
- Document environment setup in README
- Test both development and production builds

---

### Data Flow Architecture

**Authentication Flow:**
```
User → Login/Register → API → JWT Token → Store in localStorage → 
→ Include in all requests → Auto-refresh on expiration
```

**User State Flow:**
```
App Load → Check Auth → Fetch User State → Fetch Profile → 
→ Display in UI → User Actions → Update via API → Refresh State
```

**Chat Flow:**
```
Chat Tab Open → Load Conversations → Select/Create Conversation → 
→ Load Messages → User Types → Send via API → Receive Response → 
→ Update UI → Award XP → Sync State
```

**State Synchronization:**
- Optimistic updates for immediate UI feedback
- Background sync for critical data
- Error rollback if API call fails
- Periodic refresh for real-time data

### Type Mapping (Frontend ↔ Backend)

**Mood:**
- Frontend: `'Heavy' | 'Pulse' | 'Grounded'`
- Backend: `'Heavy' | 'Pulse' | 'Grounded'` ✅ Match

**RiskTier:**
- Frontend: `'Green' | 'Yellow' | 'Red'`
- Backend: `'Green' | 'Yellow' | 'Red'` ✅ Match

**StressSource:**
- Frontend: `'Family' | 'Relationship' | 'Career/Academics' | 'Others'`
- Backend: `'Family' | 'Relationship' | 'Career/Academics' | 'Others'` ✅ Match

**UserState Fields:**
- Frontend: `mood, source, otherText?, tier, steps, sleepHours, pomoSessions, xp, level, bio`
- Backend: `mood, stress_source, other_text, risk_tier, steps, sleep_hours, pomo_sessions, xp, level` + separate `UserProfile`
- **Note:** Need to map `sleepHours` ↔ `sleep_hours`, `pomoSessions` ↔ `pomo_sessions`, `otherText` ↔ `other_text`

**UserBio:**
- Frontend: `{ name, major, hobbies, values }`
- Backend: `UserProfile` with `{ name, major, hobbies, values, bio, profile_picture }`
- **Note:** Frontend bio is nested in UserState, backend is separate model

### Critical Considerations

1. **State Management:** Consider using React Query or SWR for server state management to handle caching, refetching, and synchronization
2. **Offline Support:** Consider service worker for offline functionality (future enhancement)
3. **Real-time Updates:** Consider WebSocket for real-time chat updates (future enhancement)
4. **Performance:** Implement request debouncing for rapid state updates
5. **Security:** Never expose API keys in frontend code
6. **Error Recovery:** Implement retry logic and graceful degradation

### Testing Strategy

1. **Unit Tests:** Test API service functions
2. **Integration Tests:** Test component-API interactions
3. **E2E Tests:** Test complete user flows (login → chat → dashboard)
4. **Manual Testing:** Test all features with real backend

## Quick Reference: Models & Schemas Checklist

### Models to Create/Fix (`app/models/`)

**Required Models:**
- [x] User (✅ COMPLETE - all fields correct: id, email, password_hash, created_at, updated_at)
- [x] UserProfile (✅ COMPLETE - all fields: id, user_id, name, bio, profile_picture, major, hobbies, values, created_at, updated_at)
- [x] UserState (✅ COMPLETE - all fields: id, user_id, mood, stress_source, other_text, risk_tier, xp, level, steps, sleep_hours, pomo_sessions, last_updated)
- [x] Conversation (✅ COMPLETE - all fields: id, user_id, tier, mood, source, created_at, updated_at)
- [x] ChatMessage (✅ COMPLETE - all fields: id, conversation_id, role, content, created_at)
- [x] JournalEntry (✅ COMPLETE - all fields: id, user_id, content, mood_at_time, tier_at_time, xp_gained, created_at)

**Optional Models:**
- [x] PeerCluster (✅ COMPLETE - all fields: id, name, description, created_at)
- [x] UserClusterMembership (✅ COMPLETE - all fields: user_id, cluster_id, joined_at)

**Note:** All models are now implemented in `app/models/user.py` with proper relationships and field types.

---

