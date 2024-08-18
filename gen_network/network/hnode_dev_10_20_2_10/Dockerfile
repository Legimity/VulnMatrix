FROM jezet/drl_web:v3

COPY ./startup.sh /usr/local/bin/startup.sh

RUN chmod +x /usr/local/bin/startup.sh

EXPOSE 8086
EXPOSE 8080
EXPOSE 6379

CMD ["/bin/bash", "-c", "/usr/local/bin/startup.sh && /bin/bash"]

