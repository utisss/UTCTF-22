FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get update && apt-get install -y build-essential socat libseccomp-dev qemu-system

ARG FLAG
ARG USER
ENV USER $USER
ENV FLAG $FLAG

WORKDIR /
RUN useradd -m $USER

COPY start.sh /home/$USER/start.sh
RUN chmod 755 /home/$USER/start.sh


RUN echo "$FLAG" > /home/$USER/flag.txt
RUN chmod 644 /home/$USER/flag.txt

EXPOSE 9000

COPY src/* /home/$USER/

CMD ["/home/bloat/start.sh"]
