FROM python:3.11-slim-bullseye

RUN apt-get update && \
    apt-get -y install ffmpeg

WORKDIR /opt/dagster/app/ytdl

ADD ytdl /opt/dagster/app/ytdl
COPY setup.py /opt/dagster/app/
WORKDIR /opt/dagster/app
RUN pip install -e .

# Run dagster gRPC server on port 4300

EXPOSE 4300

# CMD allows this to be overridden from run launchers or executors that want
# to run other commands against your repository
CMD ["dagster", "code-server", "start", "-h", "0.0.0.0", "-p", "4300", "-m", "ytdl"]