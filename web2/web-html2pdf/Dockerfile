FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y python3-pip wkhtmltopdf xvfb openssl

# Setup website.
WORKDIR /usr/src/app
COPY app.py /usr/src/app/app.py
COPY templates /usr/src/app/templates
COPY static /usr/src/app/static
COPY requirements.txt /usr/src/app/requirements.txt
RUN pip3 install --upgrade pip
RUN pip install -r requirements.txt

# Create system users.
RUN useradd -ms /bin/bash dave -p "$(openssl passwd -1 sdgoasdjg2089g982n)"
RUN useradd -ms /bin/bash john -p "$(openssl passwd -1 ag8n82pwoion2p98ad)"
RUN useradd -ms /bin/bash emma -p "$(openssl passwd -1 as98ngnu2jlsndg2as)"
RUN useradd -ms /bin/bash WeakPasswordAdmin -p "$(openssl passwd -1 sunshine)"

# Setup flag.
ARG FLAG
ENV FLAG $FLAG

# Run the website.
EXPOSE 5000
ENTRYPOINT ["python3"]
CMD ["/usr/src/app/app.py"]
