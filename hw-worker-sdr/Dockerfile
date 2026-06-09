FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# 1. Install UHD, LimeSDR drivers, build tools, and Python3
RUN apt update && apt install -y --no-install-recommends \
    --no-install-suggests \
    soapysdr-tools libsoapysdr-dev \
    soapysdr-module-lms7 \
    uhd-soapysdr \
    uhd-host libuhd-dev \
    python3 python3-pip python3-dev \
    git cmake libfftw3-dev libmbedtls-dev libboost-program-options-dev libconfig++-dev libsctp-dev \
    libzmq3-dev libboost-system-dev libboost-test-dev libboost-thread-dev \
    g++ make pkg-config libpython2-dev swig libi2c-dev \
    libusb-1.0-0-dev \
    && rm -rf /var/lib/apt/lists/*

ENV UHD_IMAGES_DIR=/usr/share/uhd/images/
RUN uhd_images_downloader

# 2. Compile srsRAN from 4G branch with the sib_logger patch
RUN git clone https://github.com/srsran/srsRAN_4G /srsRAN_4G

# Copy the patch file from the build context
COPY sib_logger.patch /srsRAN_4G/

WORKDIR /srsRAN_4G/
RUN git checkout ec29b0c1ff79cebcbe66caa6d6b90778261c42b8 && git apply sib_logger.patch && \
    mkdir build && cd build && \
    cmake -DUSE_LTE_RATES=ON ../ && make -j`nproc` cell_search srsue && make install && \
    ldconfig

RUN cp /srsRAN_4G/build/lib/examples/cell_search /usr/bin/

# 2.5 Compile gr-gsm (bkerler fork for GNU Radio 3.10 compatibility)
RUN apt update && apt install -y --no-install-recommends \
    gnuradio gnuradio-dev gr-osmosdr swig libosmo-dsp-dev libosmocore-dev libboost-all-dev \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/bkerler/gr-gsm /gr-gsm \
    && cd /gr-gsm \
    && mkdir build && cd build \
    && cmake .. \
    && make -j`nproc` \
    && make install \
    && ldconfig

# 3. Setup Python microservice
WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy microservice source code
COPY . /app/

# Create dynamic volumes and directories
RUN mkdir -p /vol/helpers /vol/output /vol/scripts

# Compile the gRPC service proto
RUN python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. proto/sdr_worker.proto

EXPOSE 50051 5556

ENTRYPOINT ["python3", "src/main.py"]
