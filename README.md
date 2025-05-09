# Twoblade Proxy

This proxy connects **[Twoblade](https://twoblade.com/)** (and clones), an email service built by [FaceDev](https://github.com/face-hh), and uses SHARP instead of the usual email protocol for normal email communication.
## Try out my Instance  
To send a mail from Twoblade to an normal email adress just mail `mail#twoblade.com` **with youre Receiver Email being youre Subject**.

For the other way around email `outbound.mailproxy@gmail.com` **with also youre Receiver Email being youre Subject**.
### Notice
It can take up to 1 Minute for mails to arrive and my Acc on **[Twoblade](https://twoblade.com/)** Word lenght is limited to **5 ** so every Email with longer Words wont go throw!
## Setup

### 1. Clone the repository

Clone the repository to your local machine.

```bash
git clone https://github.com/thetechnikfreak/twobladeproxy/
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

### Thanks
Thanks to [FaceDEV](https://github.com/face-hh) for youre intresting Email Provider
and [Rose](https://github.com/rosegoldd) for helping auth with auth and the hashcode.
