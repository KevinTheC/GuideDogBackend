#CUSTOM DOCKER FOR KEVIN $$$$$$$$$$$$$$$$$$$$$$$$$$$$
# Use an official Conda image
FROM continuumio/miniconda3

# Set up working directory
WORKDIR /app

# Copy and install the Conda environment
COPY environment.yaml .
RUN conda env create -f environment.yaml


ENV MKL_THREADING_LAYER=INTEL
ENV MKL_SERVICE_FORCE_INTEL=1
ENV MKL_NUM_THREADS=1
ENV NUMEXPR_NUM_THREADS=1
ENV OMP_NUM_THREADS=1
# Activate the environment in the container shell

# Copy app files
COPY . .
