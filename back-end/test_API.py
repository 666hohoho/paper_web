import httpx
def test_moonshot_connection(api_host, api_key):
    try:
        test_data = {
            "messages": [{"role": "user", "content": "Hello"}],
            "model": "moonshot-v1-8k"
        }
        
        resp = httpx.post(
            f"{api_host}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=test_data,
            timeout=5
        )
        
        if resp.status_code == 200 and 'choices' in resp.json():
            return True, "Moonshot API连接成功"
        return False, f"Moonshot API返回异常: {resp.text}"
        
    except Exception as e:
        return False, f"Moonshot API连接错误: {str(e)}"

def test_openai_connection(api_key):
    try:
        test_data = {
            "messages": [{"role": "user", "content": "Hello"}],
            "model": "gpt-3.5-turbo"
        }
        
        resp = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=test_data,
            timeout=10
        )
        
        if resp.status_code == 200 and 'choices' in resp.json():
            return True, "OpenAI API连接成功"
        return False, f"OpenAI API返回异常: {resp.text}"
        
    except Exception as e:
        return False, f"OpenAI API连接错误: {str(e)}"