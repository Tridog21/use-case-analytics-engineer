FROM apache/superset:6.1.0@sha256:16b50bbef6648912a79e3293d418fefa743ce555d36c5af6b85d859119ed7f88
USER root
COPY requirements.txt /tmp/case-requirements.txt
RUN uv pip install --python /app/.venv/bin/python --no-deps -r /tmp/case-requirements.txt
USER superset
