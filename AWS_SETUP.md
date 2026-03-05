# AWS Bedrock Setup Guide (Task A1)

## Important: Bedrock Doesn't Use API Keys!

**Amazon Bedrock uses AWS IAM credentials**, not API keys like OpenAI or Gemini. You need to configure AWS access keys or use an IAM role.

---

## Option 1: AWS CLI (Recommended for Local Development)

### Step 1: Install AWS CLI
```bash
# Ubuntu/Debian
sudo apt install awscli

# Or via pip
pip install awscli
```

### Step 2: Configure Credentials
```bash
aws configure
```

You'll be prompted for:
- **AWS Access Key ID**: Your AWS access key (get from AWS Console → IAM → Users → Your User → Security Credentials)
- **AWS Secret Access Key**: Your secret key (same place)
- **Default region**: `us-east-1` (where your RDS and Bedrock are)
- **Default output format**: `json`

This creates `~/.aws/credentials` automatically. **boto3 will use these automatically.**

### Step 3: Test
```bash
python testAWS.py
```

---

## Option 2: Environment Variables (Alternative)

If you prefer environment variables instead of AWS CLI:

### Create/Edit `.env` file in project root:
```bash
# AWS Credentials for Bedrock
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
```

**Note:** Make sure `.env` is in `.gitignore` (never commit credentials!)

### Test
```bash
python testAWS.py
```

---

## Option 3: IAM Role (For Production: EC2/Lambda/EB)

If running on AWS infrastructure (Elastic Beanstalk, Lambda, EC2):
- **No credentials needed** - AWS automatically provides IAM role credentials
- Just attach an IAM role with `bedrock:InvokeModel` permission to your instance/function

---

## Getting AWS Access Keys

1. Go to **AWS Console** → **IAM** → **Users**
2. Click your username (or create a new user)
3. Go to **Security credentials** tab
4. Click **Create access key**
5. Choose **Command Line Interface (CLI)** or **Application running outside AWS**
6. Copy the **Access Key ID** and **Secret Access Key** (you'll only see the secret once!)

---

## Required IAM Permissions

Your AWS user/role needs this permission:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-micro-v1:0"
    }
  ]
}
```

---

## Verify Setup

Run the test script:
```bash
python testAWS.py
```

**Success looks like:**
```
Bedrock raw response (Nova Micro):
{"content": [{"text": "Task A1 success!"}]}
```

**Failure looks like:**
```
NoCredentialsError: Unable to locate credentials
```
or
```
AccessDeniedException: User is not authorized to perform: bedrock:InvokeModel
```

---

## Troubleshooting

- **"NoCredentialsError"**: Run `aws configure` or set environment variables
- **"AccessDeniedException"**: Your IAM user needs `bedrock:InvokeModel` permission
- **"ModelAccessDeniedException"**: Enable Nova Micro in Bedrock Console → Model Access
- **"ValidationException"**: Check that the model ID is correct (`amazon.nova-micro-v1:0`)

---

## Security Notes

- ✅ **DO**: Use IAM roles for production (EC2/Lambda/EB)
- ✅ **DO**: Keep `.env` in `.gitignore`
- ✅ **DO**: Use least-privilege IAM policies (only Nova Micro, not all models)
- ❌ **DON'T**: Commit AWS credentials to git
- ❌ **DON'T**: Share access keys publicly
