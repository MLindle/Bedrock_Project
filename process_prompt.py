def lambda_handler(event, context):
    import boto3, json, os

    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    s3 = boto3.client('s3')

    OUTPUT_FOLDER = os.environ.get('OUTPUT_FOLDER', 'prompt_outputs/')
    OUTPUT_BUCKET = os.environ.get('OUTPUT_BUCKET')

    INPUT_FOLDER  = os.environ.get("INPUT_FOLDER", "prompt_inputs/")
    STAGE = (os.environ.get("STAGE"))

    def load_payload_from_s3():
        obj = s3.get_object(Bucket=OUTPUT_BUCKET, Key=f"{STAGE}/{INPUT_FOLDER}sea_prompt.json")
        return json.loads(obj['Body'].read().decode('utf-8'))
    
    def load_template_from_s3():
        obj = s3.get_object(Bucket=OUTPUT_BUCKET, Key=f"{STAGE}/{INPUT_FOLDER}prompt_template_1.txt")
        return obj['Body'].read().decode('utf-8')

    payload = load_payload_from_s3()
    template = load_template_from_s3()

    payload["system"] = template

    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        body=json.dumps(payload),
        contentType="application/json",
        accept="application/json",
    )

    result = json.loads(response["body"].read())
    # print(result["content"][0]["text"])

    html = f"""<!DOCTYPE html>
    <html lang="en">
    <meta charset="UTF-8">
    <title>Poem about the Sea</title>
    <body>
    <pre>
    {(result["content"][0]["text"])}</pre>
    </body>
    </html>
    """
    #print(html)

    key = f"{STAGE}/{OUTPUT_FOLDER}sea_poem.html"

    s3.put_object(
        Bucket=OUTPUT_BUCKET,
        Key=key,
        Body=html,
        ContentType="text/html"
    )

    return {
        'statusCode': 200,
        'body': json.dumps({"bucket": OUTPUT_BUCKET, "key": key}),
    }
