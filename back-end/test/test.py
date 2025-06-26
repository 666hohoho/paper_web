from pathlib import Path
from openai import OpenAI
import openai
import PyPDF2
from pathlib import Path
from openai import OpenAI

# client = OpenAI(
#     api_key = "your-api-key",
#     base_url = "https://api.gptsapi.net/v1",
# )

# 方法一：提取 PDF 文本内容
# with open("back-end/literature/1.调整街道照明以限制光污染对蝙蝠的影响.pdf", "rb") as f:
#     reader = PyPDF2.PdfReader(f)
#     file_content = "".join(page.extract_text() for page in reader.pages[:8])

# 方法二：上传 PDF 文件并获取内容,不成功

# file_object = client.files.create(
#     file=Path("back-end/literature/1.调整街道照明以限制光污染对蝙蝠的影响.pdf"),
#     purpose="fine-tune",
# )
# file_content = client.files.content(file_id=file_object.id).text

# response = client.chat.completions.create(
#     model="gpt-3.5-turbo",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "请总结主要内容"},
#         {"role": "user", "content": file_content}
#     ]
# )



from openai import OpenAI
import http.client

import json
conn = http.client.HTTPSConnection("api.openai.com")

import http.client
import mimetypes
from codecs import encode

dataList = []
boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
dataList.append(encode('--' + boundary))
dataList.append(encode('Content-Disposition: form-data; name=file; filename={0}'.format('')))

fileType = mimetypes.guess_type('')[0] or 'application/octet-stream'
dataList.append(encode('Content-Type: {}'.format(fileType)))
dataList.append(encode(''))

with open('back-end/literature/1.调整街道照明以限制光污染对蝙蝠的影响.pdf', 'rb') as f:
   dataList.append(f.read())
dataList.append(encode('--' + boundary))
dataList.append(encode('Content-Disposition: form-data; name=purpose;'))

dataList.append(encode('Content-Type: {}'.format('text/plain')))
dataList.append(encode(''))

dataList.append(encode("fine-tune"))
dataList.append(encode('--'+boundary+'--'))
dataList.append(encode(''))
body = b'\r\n'.join(dataList)
payload = body
headers = {
   'Authorization': 'Bearer your-api-key',
   'Content-type': 'multipart/form-data; boundary={}'.format(boundary)
}
conn.request("POST", "/v1/files", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))




# print(response.choices[0].message.content)