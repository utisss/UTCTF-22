FROM ubuntu:latest
    
RUN apt update && apt install openssh-server sudo -y

RUN mkdir /home/cshackleford

#RUN chmod 776 /home/admin

RUN useradd -rm -d /home/cshackleford -s /bin/bash -g root -G sudo -u 1000 cshackleford

RUN  echo 'cshackleford:defaultpw5678!' | chpasswd

RUN service ssh start

COPY flag.txt /home/cshackleford

EXPOSE 8622/tcp

CMD ["/usr/sbin/sshd","-D"]
