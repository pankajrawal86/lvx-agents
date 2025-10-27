# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Define environment variable
ENV PORT 8080
ENV GOOGLE_CLOUD_PROJECT=lvx-dev-391407

# Run the application
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
