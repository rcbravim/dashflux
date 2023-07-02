# DASHFLUX - GERENCIADOR FINANCEIRO MIN

## [Setup]

> Python Version: 3.10

### Create virtual environment

```bash
$ python3 -m venv venv
```
 
### Activate env with the following command in the project folder

```bash
$ source venv/bin/activate
```

### Install requirements

```bash
$ pip install -r requirements.txt
```

>Create a .env file to keep all env variables with their respective values.
>The variables names are located in .env-example

### Initiate Database

```bash
$ python flask --app home init-db
```

### Run Application

```bash
$ python flask --app home run
```

### PyCharm Community
```bash
# Module name: 
    flask
# Parameters:
    --app home init-db (to init database)
    --app home run (to run application)
```

## Deploy (AWS EC2)
- up an ec2 instance: aws > ec2 > executar instâncias > criar par de chaves 
- get the .pem file and save it on local folder
- put the all content of .pem file in a secret inside GitHub project (secrets.EC2_PRIVATE_KEY)
- connect to the ec2 instance (ssh, mobaxterm, putty) user: ec2-user
- install the follow dependencies that will be used in future steps:
  - sudo yum install -y git
  - sudo yum install -y docker
  - sudo service docker start
  - sudo service docker status (to check it out)
- generate an ssh key: ssh-keygen -t rsa
- put the .pub file content on GitHub as a deployment key
- clone the repository in some ec2 folder (e.g. /app) using ssh git clone
- access the project folder (cd flask-invofinance)
- docker build -t flask-invofinance . 
- sudo docker run -d --name flask-invofinance -p 5000:5000 -v $(pwd)/instance:/app/instance --restart always flask-invofinance
- install and configure nginx
  - sudo yum install nginx
  - sudo service nginx start
  - sudo vi /etc/nginx/nginx.conf
  - add in http block:
    ```
    server {
      listen 80;
      server_name example.com;  # EC2 IP or domain

      location / {
          proxy_pass http://127.0.0.1:5000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      }
    }
    ```
  - sudo service nginx restart
- make http rule on ec2 security group

## Hosting and Certificates (HTTPS)
- register/buy a domain (godaddy.com, registro.br, locaweb.com.br)
- if AWS -> go to route 53, create a new host zone, and put the relationship with your ec2 ipv4 instance
- create the registers (A, NS, SOA, CNAME, etc...)
- install and run certbot: https://certbot.eff.org/instructions?ws=nginx&os=pip or https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-20-04