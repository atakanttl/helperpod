FROM alpine:3.15

ENV USER=helperpod
ENV UID=1000
ENV GID=1000

RUN /bin/sh -c set -eux; \
    apk add --no-cache \
    wget \
    curl \
    vim \
    nano \
    bash \
    git \
    bash-completion \
    rsync \
    net-tools \
    nmap \
    openssh \
    netcat-openbsd \
    jq \
    bind-tools

# # Remove below comments if you don't want to run root container
# RUN /bin/sh -c set -eux; \
#     addgroup -S -g "$GID" "$USER"; \
#     adduser --disabled-password --gecos "" --home "$(pwd)" \
#         --ingroup "$USER" --no-create-home --uid "$UID" "$USER"

# USER 1000

ENTRYPOINT ["sh", "-c", "tail -f /dev/null"]
