FROM alpine

RUN mkdir -p /opt/micromdm

WORKDIR /opt/micromdm

ARG RELEASE_URL=https://github.com/micromdm/micromdm/releases/download/v1.12.1/micromdm_v1.12.1.zip
ARG RELEASE_HASH=7cbaa5bc2976fb370c8e940979c8c8a73d13e7650b8a017b082eca0b65cd6398

RUN wget -O micromdm.zip $RELEASE_URL \
	&& echo "$RELEASE_HASH  micromdm.zip" | sha256sum -c - \
	&& unzip micromdm.zip 'build/linux/*' \
	&& rm -f micromdm.zip

EXPOSE 8080/tcp

CMD ["/opt/micromdm/build/linux/micromdm", "serve"]

