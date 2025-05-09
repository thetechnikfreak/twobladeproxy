# Twoblade Proxy

This proxy connects Twoblade (and other clones), an email service built by FaceDev, and uses SHARP instead of the usual email protocol for normal email communication.

## Setup

### 1. Clone the repository

Clone the repository to your local machine.

```bash
git clone github.com/thetechnikfreak/twobladeproxy
```

### 2. Configure logins

Update the login credentials in the following scripts:

* `2b_to_email.py`
* `email_to_2b.py`

Make sure you replace the placeholder login information with your own credentials.

### 3. Build the Docker image

Build the Docker image using the following command:

```bash
docker build -t twoblade-proxy .
```

### 4. Run the Docker container

You can now run the Docker container using:

```bash
docker run twoblade-proxy
```

Alternatively, if you prefer, you can run the scripts directly without using Docker.

