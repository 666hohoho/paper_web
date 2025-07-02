FROM docker-0.unsee.tech/python:3.9

# 设置工作目录为容器中的 /paper-web
WORKDIR /paper-web

# 将整个项目文件夹复制到容器中
COPY . /paper-web

# 切换到后端工作目录
WORKDIR /paper-web/back-end

RUN pip install --upgrade pip

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 暴露端口（根据 server.py 实际监听端口修改，假设为5000）
EXPOSE 5002

# 启动服务
CMD ["python3","server.py"]

