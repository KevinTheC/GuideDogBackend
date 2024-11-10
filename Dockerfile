#CUSTOM DOCKER FOR KEVIN $$$$$$$$$$$$$$$$$$$$$$$$$$$$
# Use an official Conda image
FROM continuumio/miniconda3

# Set up working directory
WORKDIR /app

# Copy and install the Conda environment
COPY environment.yaml .
RUN conda env create -f environment.yaml

# Activate the environment in the container shell

# Copy app files
COPY . .

# Expose the port
EXPOSE 443