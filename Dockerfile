# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r ./app/requirements.txt

# Set the PYTHONPATH to include the /app directory
ENV PYTHONPATH /app

# Expose port 8000 to the outside world
EXPOSE 8000

# Define environment variables, if needed
# ENV MY_ENV_VAR=value

# Run FastAPI using Uvicorn when the container launches
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
