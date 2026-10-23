FROM python:3.12-slim

RUN pip install --no-cache-dir Pillow exifread piexif

WORKDIR /workspace
