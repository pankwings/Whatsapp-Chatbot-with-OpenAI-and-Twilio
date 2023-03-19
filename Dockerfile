# Set base image
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the required packages
RUN pip install -r requirements.txt

# Copy the application code to the container
COPY . .

# Set the environment variables from the .env file
ENV $(cat .env | xargs)

# Expose the application port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
