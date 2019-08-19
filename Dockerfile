# Copyright 2019 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

FROM ubuntu:bionic

# install python and dependencies for mesa
RUN apt-get update \
    && apt-get install -y python3-pip python-pip python3-dev git \
    && cd /usr/local/bin \
    && ln -s /usr/bin/python3 python \
    && pip3 install --upgrade pip \
    && apt-get install -y xvfb llvm-5.0-runtime x11-utils llvm-dev libxcb-dri2-0-dev libxcb-xfixes0-dev \
    && apt-get install -y libx11-xcb-dev zlib1g-dev xorg-dev xserver-xorg-dev python-opengl

    # compile mesa to be able to use DRI with docker
RUN mkdir -p /var/tmp/build \
    && cd /var/tmp/build \
    && apt-get install -y wget \
    && wget "https://mesa.freedesktop.org/archive/mesa-18.0.1.tar.gz" \
    && tar xfv mesa-18.0.1.tar.gz \
    && rm mesa-18.0.1.tar.gz \
    && cd mesa-18.0.1 \
    && ./configure --enable-glx=gallium-xlib --with-gallium-drivers=swrast,swr --disable-dri --disable-gbm --disable-egl --enable-gallium-osmesa --prefix=/usr \
    && make -j4 \
    && make install \
    && cd .. \
    && rm -rf mesa-18.0.1

ENV USER=gymscaling
RUN useradd -ms /bin/bash $USER && mkdir /home/$USER/local

# Finalize mesa installation, remove default ubuntu mesa libs
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata \
    && ln -fs /usr/share/zoneinfo/Europe/Dublin /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata \
    && apt-get install -y mesa-utils libopenmpi-dev python3-tk \
    && dpkg --force-depends -r libgl1 libglx0 va-driver-all libglx-mesa0 libgl1-mesa-dri

# Setup our environment variables.
ENV DISPLAY=":0" \
    LIBGL_ALWAYS_SOFTWARE="1" \
    GALLIUM_DRIVER="llvmpipe" \
    LP_NO_RAST="false" \
    LP_DEBUG="" \
    LP_PERF="" \
    LP_NUM_THREADS=""

ADD requirements.txt /
RUN pip3 install -r /requirements.txt

RUN git clone https://github.com/openai/baselines.git /baselines \
    && pip install -e /baselines

ADD gym_scaling /gym/gym_scaling
ADD setup.py train_deepq.py enjoy_random.py enjoy_deepq.py /gym/
ADD models /gym/models
RUN pip3 install /gym

WORKDIR /gym

CMD ["python3", "enjoy_deepq.py"]
