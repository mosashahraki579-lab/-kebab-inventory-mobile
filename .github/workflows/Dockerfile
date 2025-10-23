FROM ubuntu:22.04

# نصب وابستگی‌ها
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    zip \
    unzip \
    openjdk-17-jdk \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    cmake \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# نصب Buildozer
RUN pip3 install buildozer

# کپی کردن فایل‌های پروژه
COPY . /app
WORKDIR /app

# ساخت APK
RUN buildozer android debug
