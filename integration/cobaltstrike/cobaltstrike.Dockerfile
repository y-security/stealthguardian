FROM ubuntu:22.04

RUN export DEBIAN_FRONTEND=noninteractive; apt-get -y update && apt-get -y upgrade
RUN export DEBIAN_FRONTEND=noninteractive; apt-get -y install python3-pip screen openjdk-21-jre

RUN pip install pexpect requests

WORKDIR /root

COPY ./integration/cobaltstrike/main.sh /main.sh
RUN chmod +x /main.sh

CMD ["/main.sh"]
