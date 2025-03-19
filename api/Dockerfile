FROM python:3.8-alpine

# Install system dependencies, build tools, and Rclone
RUN apk add --no-cache \
    curl unzip gcc musl-dev python3-dev libffi-dev libressl-dev cargo wget && \
    curl -fsSL https://downloads.rclone.org/rclone-current-linux-amd64.zip -o rclone.zip && \
    unzip rclone.zip && \
    mv rclone-*-linux-amd64/rclone /usr/bin/ && \
    rm -rf rclone.zip rclone-*-linux-amd64

# Set up application directory
WORKDIR /usr/src/app

# Copy and install dependencies
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Ensure setup scripts are executable
RUN chmod +x local_setup/setupRClone.sh local_setup/cleanRClone.sh

# Fetch AWS RDS global trust store certificate
RUN wget -O global-bundle.pem https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem

# Expose the application port
EXPOSE 8080

# Define entrypoint and command
ENTRYPOINT ["python3"]
CMD ["-m", "swagger_server"]
