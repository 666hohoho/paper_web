from pathlib import Path
from openai import OpenAI
from openpyxl import Workbook
import json
import os
import PyPDF2
import pandas as pd




def process_literature(file_path, api_type, api_host, api_key, headers=None):
    # 构建动态提取字段的 prompt
    fields_str = "、".join(headers)
    user_prompt = f"请分析这篇文献，提取以下信息并以json格式输出：{fields_str}。如果某个字段在文献中没有明确提及，请填写'未提及'"

    #如果api_type是moonshot，base_url是api_host加上'/v1'，如果api_type是openai，base_url是api_host加上'/v1/files'
    if api_type.lower() == 'moonshot':
        
        base_url = f"{api_host}/v1"
        client = OpenAI(
        api_key=api_key,
        base_url =base_url)


        # 上传文件到 API
        file_object = client.files.create(file=Path(file_path), purpose="file-extract")

        # 获取文件内容
        file_content = client.files.content(file_id=file_object.id).text

        messages = [
            {
                "role": "system",
                "content": "你是景观学、生态学领域的专家，具有丰富的专业知识，擅长进行中英文文献阅读。你会为用户提供安全，有帮助，准确的文献分析。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。",
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

        print(f"API 返回的内容：{completion.choices[0].message.content}")

        # 解析返回的 JSON 数据
        response_content = completion.choices[0].message.content.strip() 
        # 去掉第一个{前面的部分
        first_brace = response_content.find('{')
        if first_brace != -1:
            response_content = response_content[first_brace:]
        # 去掉最后一个}后面的部分
        last_brace = response_content.rfind('}')
        if last_brace != -1:
            response_content = response_content[:last_brace + 1]
        print(response_content)

        


    elif api_type.lower() == 'openai':
        base_url = f"{api_host}/v1"
        client = OpenAI(
        api_key=api_key,
        base_url =base_url)

        # 提取 PDF 文本内容
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            file_content = "".join(page.extract_text() for page in reader.pages[:2])
            print(f"提取的文件内容：{file_content[:500]}...")  # 打印前500个字符以检查内容


        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_prompt },
                {"role": "user", "content": file_content}
            ]
        )

        print(f"API 返回的内容：{completion.choices[0].message.content}")
        response_content = completion.choices[0].message.content.strip() 
        # 去掉第一个{前面的部分
        first_brace = response_content.find('{')
        if first_brace != -1:
            response_content = response_content[first_brace:]
        # 去掉最后一个}后面的部分
        last_brace = response_content.rfind('}')
        if last_brace != -1:
            response_content = response_content[:last_brace + 1]
        print(response_content)

    
    else:
        raise ValueError("Unsupported API type. Use 'moonshot' or 'openai'.")

    

    parsed_data = json.loads(response_content)
    print(f"解析后的数据：{type(parsed_data)}")

    # 动态提取所有字段
    def dict_to_str(val):
        return json.dumps(val, ensure_ascii=False) if isinstance(val, (dict, list)) else val

    row_data = []
    for h in headers:
        val = parsed_data.get(h, "未提及")
        row_data.append(dict_to_str(val))

    print(json.dumps(row_data, ensure_ascii=False))

    return row_data


if __name__ == "__main__":
    # 仅在直接运行此文件时使用默认路径
    headers=['研究内容']
    row_data=process_literature(file_path='./literature/01How to hide your voice.pdf', api_type='moonshot', api_host='https://api.moonshot.cn', api_key='your-api-key', headers=headers)
    #row_data=process_literature(file_path='./literature/01How to hide your voice.pdf', api_type='openai', api_host='https://api.gptsapi.net', api_key='your-api-key', headers=headers)
    print(row_data)
    df = pd.DataFrame([row_data], columns=headers)
    df.to_excel("output.xlsx")
