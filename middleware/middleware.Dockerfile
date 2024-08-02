FROM ubuntu:22.04

RUN export DEBIAN_FRONTEND=noninteractive; apt-get -y update && apt-get -y upgrade
RUN export DEBIAN_FRONTEND=noninteractive; apt-get -y install python3-pip screen curl

RUN pip install "uvicorn[standard]" fastapi validators Jinja2 python-multipart

EXPOSE 8000

COPY ./main.sh /main.sh
CMD ["/main.sh"]
