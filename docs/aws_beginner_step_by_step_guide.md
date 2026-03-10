# AWS Beginner Guide for Your Project (EC2 + S3 + Database + Bedrock)

This guide explains how to use what you already created in AWS:
- `EC2` (your server/computer in cloud)
- `S3` (file storage)
- `DB` (your database, likely Amazon RDS PostgreSQL)
- `Bedrock` (AI model service)

Written in simple language, with step-by-step actions.

---

## 1) Understand each service in one line

- **EC2**: runs your backend app (FastAPI, Node, etc.).
- **RDS DB**: stores structured data (users, chats, etc.).
- **S3**: stores files (audio, images, docs).
- **Bedrock**: generates AI responses from models (Claude, Nova, etc.).

Think of it like:
- EC2 = kitchen
- DB = notebook
- S3 = storage room
- Bedrock = expert assistant

---

## 2) What should connect to what

Your normal backend flow is:

1. User sends request to your backend on EC2.
2. EC2 reads/writes data in DB (RDS).
3. If file upload, EC2 stores file in S3 and saves only `s3_key` in DB.
4. If AI needed, EC2 calls Bedrock.
5. EC2 returns response to user app.

Important: users should **not** connect directly to DB.

---

## 3) First-time setup checklist (safe defaults)

Do this once:

1. Keep all services in the **same region** (example: `us-east-1`) if possible.
2. Create an IAM role for EC2 with only needed permissions:
   - S3 (specific bucket/prefix only)
   - Bedrock `InvokeModel` only
3. Use security groups:
   - EC2 security group allows app port (for example 8000/443 as needed)
   - RDS security group allows port `5432` **only from EC2 security group**
4. Keep S3 bucket private (no public read/write).
5. Store secrets in environment variables or AWS Secrets Manager, not hard-coded in code.

---

## 4) Database password and credential management (very important)

## 4.1 Where DB password should live

Use one of these:
- **Best**: AWS Secrets Manager
- **Simple for now**: EC2 environment variable (in `.env` on server, not in git)

Never:
- commit password to GitHub
- send password in chat/messages
- put password in frontend/mobile app

## 4.2 Example connection string

For PostgreSQL:

```text
postgresql+psycopg2://DB_USER:DB_PASSWORD@DB_ENDPOINT:5432/DB_NAME?sslmode=require
```

Example variable:

```bash
DATABASE_URL="postgresql+psycopg2://meghan_user:YOUR_PASSWORD@meghan.cluster-xxxx.us-east-1.rds.amazonaws.com:5432/meghan_db?sslmode=require"
```

## 4.3 Password rotation (simple process)

1. Create a new DB password.
2. Update it in Secrets Manager or EC2 env.
3. Restart backend service.
4. Test login/API quickly.
5. Delete old password after confirmation.

Tip: rotate regularly (for example every 60-90 days).

---

## 5) How to connect to DB using AWS Query Editor (beginner steps)

This is the easiest UI way to run SQL without local tools.

1. Open AWS Console.
2. Go to **RDS**.
3. Click **Query Editor** (or **Query Editor v2**, depending on your account).
4. First-time setup may ask for:
   - database engine/type
   - database identifier/cluster
   - username
   - password (or Secrets Manager secret)
5. Connect.
6. Run test SQL:

```sql
SELECT current_database(), current_user, now();
SELECT 1;
```

If connection fails:
- check region (must match your DB region)
- check user/password
- check DB is in `Available` state
- check security/network restrictions

---

## 6) How to connect app running on EC2 to DB

## 6.1 On EC2 machine

1. SSH into EC2.
2. Add env variables (`DATABASE_URL`, `AWS_REGION`, etc.).
3. Start/restart app service (systemd, docker, or uvicorn/gunicorn).
4. Check logs for DB connection success.

## 6.2 Security group rules (most common issue)

- RDS inbound: PostgreSQL `5432` from **EC2 security group**.
- Do not allow `0.0.0.0/0` to DB unless temporary emergency.

---

## 7) S3 usage in simple terms

Use S3 for files only (audio/images/docs), not relational records.

Recommended pattern:
1. App uploads file to S3.
2. Store `s3_key` in DB (example: `media/chat_voice/2026/03/05/uuid.webm`).
3. Generate short-lived pre-signed URL when client needs to read file.

Why this is good:
- DB stays small/fast
- files remain private
- better cost and scaling

---

## 8) Bedrock usage in simple terms

Your EC2 backend calls Bedrock API when user needs AI response.

Basic requirements:
- AWS region supports Bedrock
- model access enabled in Bedrock console
- IAM permission: `bedrock:InvokeModel`

Process:
1. Build prompt in backend.
2. Invoke model (Claude/Nova).
3. Parse response text.
4. Save response in DB.

Do not call Bedrock directly from frontend if you can avoid it. Keep keys server-side.

---

## 9) Minimum environment variables your backend usually needs

```bash
AWS_REGION=us-east-1
DATABASE_URL=postgresql+psycopg2://...
S3_MEDIA_BUCKET=your-private-bucket
S3_MEDIA_PREFIX=media
S3_PRESIGNED_URL_TTL_SECONDS=900
BEDROCK_MODEL_ID=amazon.nova-micro-v1:0
```

If using direct access keys (not preferred on EC2 role):

```bash
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

Prefer IAM role on EC2 to avoid manual key management.

---

## 10) Quick health checks you can run after deployment

1. App health endpoint:
   - `GET /health` should return OK.
2. DB check endpoint (if available):
   - simple `SELECT 1` path should return success.
3. Upload small test file to S3 through your API.
4. Generate and open pre-signed URL.
5. Send one AI message and confirm Bedrock response is saved.

---

## 11) Common mistakes and how to fix

- **Mistake:** DB timeout from EC2  
  **Fix:** verify RDS inbound rule from EC2 security group + correct port.

- **Mistake:** `AccessDenied` for S3  
  **Fix:** attach IAM policy to EC2 role for that bucket/prefix.

- **Mistake:** Bedrock call fails with model error  
  **Fix:** enable model access in Bedrock console and check region/model ID.

- **Mistake:** query editor not showing DB  
  **Fix:** switch AWS console to correct region.

- **Mistake:** app works locally but not on EC2  
  **Fix:** missing env vars on server; check service env and restart app.

---

## 12) Suggested learning order (for non-technical users)

Follow this sequence:
1. Learn RDS Query Editor basics (`SELECT`, `INSERT`, `UPDATE`, `DELETE`).
2. Learn how EC2 reads env variables and starts your backend.
3. Learn S3 upload and pre-signed URL flow.
4. Learn one Bedrock model call from backend.
5. Add monitoring and backups.

This order keeps things practical and avoids confusion.

---

## 13) Safety checklist before sharing app publicly

- DB not public to internet.
- S3 bucket not public.
- Secrets not in code repository.
- HTTPS enabled for API.
- Regular DB snapshot backups enabled.
- Basic CloudWatch logs enabled for EC2/app.

---

## 14) If you want, next step from this guide

A good next practical milestone is:
- create a `db-check` endpoint,
- run one query from Query Editor,
- upload one file via API to S3,
- call one Bedrock prompt from backend.

That single flow will make all 4 services clear very quickly.
