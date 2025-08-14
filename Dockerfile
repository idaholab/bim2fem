# Use the official Python image from the Docker Hub. This image acts as our base 
# image that we build from.
FROM python:3.11

# Set the working directory in the container. The Docker container will be an isolated 
# machine with empty folders. Set the working directory of this empty isolated machine 
# as /app. /app will not exist yet, so a new /app folder will be created in the 
# container.
WORKDIR /app

# Copy the requirements.txt file from the local directory to the remote working 
# directory of the container (aka ./app) 
COPY requirements.txt ./requirements.txt

# Install any needed packages specified in requirements.txt. If you have a 
# contraints.txt file, then run this instead: 
# RUN pip install --no-cache-dir -r requirements.txt --constraint constraints.txt
RUN pip install --no-cache-dir -r requirements.txt

# Launch the website
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]


