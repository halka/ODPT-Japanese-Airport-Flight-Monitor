# 1. Use a slim base image
FROM python:3.12-slim

# 2. Set the working directory
WORKDIR /app

# 3. Create the virtual environment
RUN python -m venv /opt/venv

# 4. "Activate" the venv by setting environment variables
# This ensures that 'python' and 'pip' commands use the venv by default
ENV PATH="/opt/venv/bin:$PATH"

# 5. Install dependencies
# No need to activate; the PATH change handles it
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy your application code
COPY . .

# 7. Run the application
CMD ["python", "monitor_airport.py"]