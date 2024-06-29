FROM ubuntu:22.04

# Install necessary dependencies
RUN apt-get update && apt-get install -y curl gnupg

# Add Bazel distribution URI as a package source
RUN curl -fsSL https://bazel.build/bazel-release.pub.gpg | gpg --dearmor > /usr/share/keyrings/bazel-archive-keyring.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/bazel-archive-keyring.gpg] https://storage.googleapis.com/bazel-apt stable jdk1.8" | tee /etc/apt/sources.list.d/bazel.list

# Install Bazel
RUN apt-get update && apt-get install -y bazel

# Install Python 3
RUN apt-get update && apt-get install -y python3

# Add a user called dev with passwordless sudo permissions
RUN apt-get update -yq
RUN apt-get install -yq --no-install-recommends \
    vim \
    curl \
    ca-certificates \
    openssh-server \
    sudo \
    iputils-ping
RUN apt-get clean all
RUN useradd -m -s /bin/bash dev && echo "dev ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    usermod --append --groups sudo dev

# Run a command that spins forever
CMD tail -f /dev/null