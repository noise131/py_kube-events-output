FROM docker.io/library/python:3.10.5-alpine3.15

COPY ./ /kube-events-output

WORKDIR /kube-events-output

RUN set -uex; \
        pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt;

ENTRYPOINT [ "python3", "main.py" ]


# 以下构建命令在项目的根目录执行
# docker build -f deployment/docker/Dockerfile -t py_kube-events-outputs:v1 .
# 
# 启动容器命令 (参数为 mongodb 的地址)
# docker run -d py_kube-events-outputs:v1 10.0.0.75
