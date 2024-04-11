# Use the official Python image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the contents of the src directory to the working directory
COPY src/ src/

# Copy the config directory to the working directory
COPY config/ config/

# Expose port
EXPOSE 8080

# Set the PYTHONPATH for Docker
ENV PYTHONPATH=/app
ENV LANGCHAIN_TRACING_V2="true"
ENV LANGCHAIN_API_KEY=""
ENV OPENAI_API_KEY=""

# Specify the command to run on container start
CMD ["uvicorn", "src.api.api:app", "--host", "0.0.0.0", "--port", "8080"]
