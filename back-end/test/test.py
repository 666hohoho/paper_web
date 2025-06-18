from pathlib import Path
from openai import OpenAI
import openai
import PyPDF2

client = OpenAI(
    api_key = "sk-fW6ed3b49f7fa03dbb8b1f28396f4d69f3f1878bd0aoatl2",
    base_url = "https://api.gptsapi.net/v1",
)

# 提取 PDF 文本内容
with open("back-end/literature/1.调整街道照明以限制光污染对蝙蝠的影响.pdf", "rb") as f:
    reader = PyPDF2.PdfReader(f)
    file_content = "".join(page.extract_text() for page in reader.pages[:8])


response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "请总结主要内容"},
        {"role": "user", "content": file_content}
    ]
)



print(response.choices[0].message.content)