from pathlib import Path
from openai import OpenAI
from openpyxl import Workbook
import json
import os

def process_literature(file_path, api_key, headers=None):
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.moonshot.cn/v1",
    )

    # 上传文件到 API
    file_object = client.files.create(file=Path(file_path), purpose="file-extract")

    # 获取文件内容
    file_content = client.files.content(file_id=file_object.id).text


    # 构建动态提取字段的 prompt
    fields_str = "、".join(headers)
    user_prompt = f"请分析这篇文献，提取以下信息并以json格式输出：{fields_str}。如果某个字段在文献中没有明确提及，请填写'未提及'"

    messages = [
        {
            "role": "system",
            "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。",
        },
        {
            "role": "system",
            "content": file_content,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]

    # 调用 chat-completion API 获取回答
    completion = client.chat.completions.create(
        model="moonshot-v1-32k",
        messages=messages,
        temperature=0.3,
    )

    # 解析返回的 JSON 数据
    response_content = completion.choices[0].message.content
    #print("大模型输出的结果:")
    #print(response_content)


    parsed_data = json.loads(response_content)

    # 动态提取所有字段
    def dict_to_str(val):
        return json.dumps(val, ensure_ascii=False) if isinstance(val, (dict, list)) else val

    row_data = []
    for h in headers:
        if h == "文件名":
            val = Path(file_path).name
        else:
            val = parsed_data.get(h, "未提及")
        row_data.append(dict_to_str(val))

    print(json.dumps(row_data, ensure_ascii=False))
    return row_data

if __name__ == "__main__":
    # 仅在直接运行此文件时使用默认路径
    default_file_path = os.path.join(os.path.dirname(__file__), 'literature', 'test.pdf')
    process_literature(default_file_path)
