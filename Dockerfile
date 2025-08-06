# Use the official Python image from the Docker Hub. This image acts as our base 
# image that we build from.
FROM python:3.11

# For INL machines on the INL Network:
# Configure INL certs and environment variables, set environment variables for 
# certificates, configure pip to trust INL’s custom CA, and upgrade pip
RUN wget -q -P /usr/local/share/ca-certificates/ http://certstore.inl.gov/pki/CAINLROOT_B64.crt
RUN /usr/sbin/update-ca-certificates
ENV NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_DIR=/etc/ssl/certs/
RUN git config --global http.sslcainfo /etc/ssl/certs/ca-certificates.crt
RUN pip install pip_system_certs --trusted-host files.pythonhosted.org --trusted-host pypi.org
RUN pip install --upgrade pip

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


