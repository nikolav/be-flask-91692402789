FROM python:3.12

WORKDIR /home/app

# requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# add chrome --headless for pdfs
RUN apt update
RUN apt-get update -y
RUN curl -LO https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb
RUN rm ./google-chrome-stable_current_amd64.deb

COPY . .

CMD ["./wserver.sh" ]
