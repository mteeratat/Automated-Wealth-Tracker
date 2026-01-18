# 1. Use a compatible slim image (SRE Requirement)
FROM python:3.13-slim

# 2. Set the working directory
WORKDIR /app

# 3. Copy dependencies first (Caching trick!)
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the code
COPY . .

# 6. Run the script
CMD ["python", "tracker.py"]