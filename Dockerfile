#CUSTOM DOCKER FOR KEVIN $$$$$$$$$$$$$$$$$$$$$$$$$$$$
# Use an official Conda image
FROM continuumio/miniconda3

# Set up working directory
WORKDIR /app

# Create a base conda environment with only Python
RUN conda create -n midas-py310 python=3.10.8 -y

# Activate the environment and install cudatoolkit first (as it might use a lot of memory)
RUN conda run -n midas-py310 conda install -y cudatoolkit=11.8.0 && conda clean -a -y

# Install PyTorch and torchvision in a separate step
RUN conda run -n midas-py310 conda install -y pytorch=1.13.0 torchvision=0.14.0 && conda clean -a -y

# Install remaining dependencies
RUN conda run -n midas-py310 conda install -y numpy=1.23.4 && conda clean -a -y

# Install pip packages separately
RUN conda run -n midas-py310 pip install opencv-python==4.6.0.66 imutils==0.5.4 timm==0.6.12 einops==0.6.0 flask flask-limiter gunicorn && conda clean -a -y

# Clean up to save space
RUN conda clean -a -y
# Activate the environment in the container shell
SHELL ["conda", "run", "-n", "midas-py310", "/bin/bash", "-c"]
COPY . .
EXPOSE 443
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:443", "outscript:app"]