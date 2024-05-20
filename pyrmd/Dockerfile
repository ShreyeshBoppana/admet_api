FROM continuumio/miniconda3:latest

# Create and activate the environment
COPY pyrmd_environment.yml /
RUN conda env create -f /pyrmd_environment.yml
SHELL ["conda", "run", "-n", "pyrmd", "/bin/bash", "-c"]

# Install dependencies
RUN pip install fastapi python-multipart uvicorn pydantic arq redis

# Copy the application files
COPY . /app

# Create the 'uploads' folder
RUN mkdir /app/uploads

# Set the working directory
WORKDIR /app

# Expose port 8000
EXPOSE 8005

# Start the application
CMD ["conda", "run", "-n", "pyrmd", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8005", "--reload"]
