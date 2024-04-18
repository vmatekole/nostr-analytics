# Use the official Python image as the base image
FROM python:3.9

# Set the working directory to /app
WORKDIR /app

# Copy the project files into the container
COPY pyproject.toml pdm.lock README.md /app/
COPY src /app/src
COPY orchestration /app/orchestration
COPY tests /app/tests

# Install PDM
RUN pip install --no-cache-dir pdm

# Install project dependencies using PDM
RUN pdm install

COPY entrypoint.sh /app

ENTRYPOINT [ "./entrypoint.sh" ]
