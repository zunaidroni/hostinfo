FROM docker.io/python:3-alpine
WORKDIR /usr/src/hostinfo
COPY ./hostinfo_server.py .
RUN chown 1000:1000 hostinfo_server.py && chmod 400 hostinfo_server.py && pip uninstall pip -y
LABEL org.opencontainers.image.ref.name=hostinfo
LABEL org.opencontainers.image.version=1.0.0-python
LABEL org.opencontainers.image.authors=rx-m
LABEL org.opencontainers.image.url=https://rx-m.com
USER 1000:1000
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python3", "hostinfo_server.py"]
CMD ["9898"]