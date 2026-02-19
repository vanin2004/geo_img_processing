FROM ghcr.io/osgeo/gdal:ubuntu-small-3.11.4
# python 3.12.3
# gdal 3.11.4

RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	   python3-venv python3-pip python3-dev build-essential \
	&& rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN python -m pip install --upgrade pip setuptools wheel

WORKDIR /backend

COPY ./base_requirements.txt ./base_requirements.txt

RUN python -m pip install -r base_requirements.txt --no-cache-dir

# Developer tools: ruff (linter/formatter) and black (formatter)
RUN python -m pip install --no-cache-dir ruff black

CMD ["tail", "-f", "/dev/null"]