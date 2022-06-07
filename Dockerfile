FROM debian

WORKDIR /

RUN apt-get update -y && \
    apt -y upgrade && \
    apt install -y python3-pip -y && \
    apt install build-essential libssl-dev libffi-dev python3-dev -y

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python3", "./app.py" ]
EXPOSE 1862