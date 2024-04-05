ARG PYTHON_BASE=3.10-slim
# build stage
FROM python:$PYTHON_BASE AS builder

# install PDM
RUN pip install -U pdm
# disable update check
ENV PDM_CHECK_UPDATE=false
# copy files
COPY pyproject.toml pdm.lock README.md /app/
COPY src/ /app/src
COPY tests/ /app/tests

# install dependencies and app into the local packages directory
WORKDIR /app
RUN pdm install --check --prod --no-editable

# run stage
FROM python:$PYTHON_BASE

# retrieve packages from build stage
COPY --from=builder /app/.venv/ /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
# set command/entrypoint, adapt to fit your needs
COPY src /app/src
CMD ["python", "src/__main__.py"]
