# ---- Builder Stage ----
# This stage installs dependencies into a virtual environment.
FROM python:3.11 AS builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ---- Production Stage ----
# This stage copies the installed venv and the application code.
FROM python:3.11-slim AS production

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create a non-root user
RUN addgroup --system nonroot && adduser --system --group nonroot
WORKDIR /home/nonroot/app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY . .

# Change ownership of the app directory
RUN chown -R nonroot:nonroot /home/nonroot/app

# Switch to the non-root user
USER nonroot

# Make the venv's python executable available to the user
ENV PATH="/opt/venv/bin:$PATH"

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
