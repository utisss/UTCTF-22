FROM ubuntu:20.04

RUN apt-get update
RUN apt-get update && apt-get install -y build-essential socat libseccomp-dev

ARG USER
ENV USER $USER

RUN apt-get update && apt-get install -y python3 vim

WORKDIR /
COPY run.py /
COPY template.c /

COPY start.sh /start.sh
RUN chmod 755 /start.sh

RUN useradd -m $USER

RUN chown root:root /home/$USER/flag.txt
RUN chmod 644 /home/$USER/flag.txt

EXPOSE 9000

CMD ["/start.sh"]
