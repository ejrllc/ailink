# 1. Start with an official Python base image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of your application code into the container
COPY ./ailink_at /app/ailink_at
COPY ./data /app/data

# 5. Expose the port the app runs on
EXPOSE 8000

# 6. The command to run your application
CMD ["uvicorn", "ailink_at.main:app", "--host", "0.0.0.0", "--port", "8000"]