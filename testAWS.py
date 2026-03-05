import boto3
import json
import os
from botocore.exceptions import ClientError, NoCredentialsError

"""
Amazon Bedrock Nova Micro Test Script
Tests Bedrock access using AWS IAM credentials (from aws configure)
"""

def check_credentials():
    """Verify AWS credentials are configured"""
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✓ AWS Credentials found!")
        print(f"  Account: {identity.get('Account')}")
        print(f"  User ARN: {identity.get('Arn')}")
        return True
    except NoCredentialsError:
        print("✗ No AWS credentials found!")
        print("  Run: aws configure")
        return False
    except Exception as e:
        print(f"✗ Error checking credentials: {e}")
        return False

def test_bedrock_nova():
    """Test Bedrock Nova Micro invocation"""
    region = os.getenv("AWS_REGION", "us-east-1")
    
    print(f"\n📡 Connecting to Bedrock in region: {region}")
    client = boto3.client("bedrock-runtime", region_name=region)
    
    prompt = "Say 'Hello from Nova Micro' in one short sentence."
    
    # Nova Micro requires content as array of objects with "text" field
    body = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "text": prompt  # Each content item must be an object with "text" field
                    }
                ],
            }
        ],
    }
    
    print(f"📤 Sending request to amazon.nova-micro-v1:0...")
    print(f"   Prompt: {prompt}")
    
    try:
        response = client.invoke_model(
            modelId="amazon.nova-micro-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body),
        )
        
        raw = response["body"].read().decode("utf-8")
        result = json.loads(raw)
        
        print("\n✓ SUCCESS! Bedrock responded:")
        print(json.dumps(result, indent=2))
        
        # Extract text if available
        if "content" in result and len(result["content"]) > 0:
            if "text" in result["content"][0]:
                print(f"\n📝 Response text: {result['content'][0]['text']}")
        
        return True
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_msg = e.response.get('Error', {}).get('Message', str(e))
        
        print(f"\n✗ AWS Error ({error_code}): {error_msg}")
        
        if error_code == "AccessDeniedException":
            print("\n💡 Fix: Your IAM user needs bedrock:InvokeModel permission")
            print("   Go to: IAM → Users → Your User → Add permissions")
        elif error_code == "ModelAccessDeniedException":
            print("\n💡 Fix: Enable Nova Micro in Bedrock Console")
            print("   Go to: Bedrock → Model access → Enable amazon.nova-micro-v1:0")
        elif error_code == "ValidationException":
            print("\n💡 Fix: Check model ID and request format")
        
        return False
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        print(f"   Type: {type(e).__name__}")
        return False

def main():
    print("=" * 60)
    print("Amazon Bedrock Nova Micro Test")
    print("=" * 60)
    
    # Step 1: Check credentials
    if not check_credentials():
        print("\n❌ Cannot proceed without AWS credentials")
        return
    
    # Step 2: Test Bedrock
    success = test_bedrock_nova()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed - see errors above")
    print("=" * 60)

if __name__ == "__main__":
    main()
