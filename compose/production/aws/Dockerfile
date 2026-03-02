FROM docker.io/amazon/aws-cli:2.33.31

ENTRYPOINT []

COPY ./compose/production/aws/maintenance /usr/local/bin/maintenance
COPY ./compose/production/postgres/maintenance/_sourced /usr/local/bin/maintenance/_sourced

RUN chmod +x /usr/local/bin/maintenance/* \
    && mv /usr/local/bin/maintenance/* /usr/local/bin/ \
    && rmdir /usr/local/bin/maintenance

CMD ["/bin/bash"]
