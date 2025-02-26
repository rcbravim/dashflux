# DASHFLUX - GERENCIADOR FINANCEIRO

## SOBRE

  ### Dashflux é uma aplicação web feita em python/flask, com banco de dados monolitico em sqlite.
    login
  ![img.png](images%2Fimg.png)

    recuperação/alteração de senha
  ![img_1.png](images/img_1.png)

    cadastros de estabelecimentos, categorias e contas
  ![img.png](images/img_2.png)

    lançamento de receitas e despesas
  ![img.png](images/img_3.png)

    upload/download csv para facil lançamentos
  ![img.png](images/img_4.png)
    

=================================================================

## DESENVOLVIMENTO

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
$ python flask init-db
  or
$ flask init-db
```

### Insert Default Users/Records

```bash
$ flask insert-default-records
```

### Run Application

```bash
$ python flask run --debug
```

### PyCharm Community
```bash
# Module name: 
    flask
# Parameters:
    init-db (to init database)
    run --debug --reload (to run application, in debug mode)
```

=================================================================

## DEPLOY (AWS EC2)
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
- clone the repository on workdir folder using ssh git clone (must match to the workflow git actions file, "app-dashflux" int this case)
- access the workir folder
- docker build -t dashflux . 
- the next step its a first run, to ensure the database its being created
- sudo docker run -d --name dashflux -p 5000:5000 --restart always dashflux
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

## For Deploy With DB Changes (AWS EC2)
- access ec2 intance
- docker exec -it dashflux bash
- flask init-db

## Hosting and Certificates (HTTPS)
- register/buy a domain (godaddy.com, registro.br, locaweb.com.br)
- if AWS -> go to route 53, create a new host zone, and put the relationship with your ec2 ipv4 instance
- create the registers (A, NS, SOA, CNAME, etc...)
- install and run certbot: https://certbot.eff.org/instructions?ws=nginx&os=pip or https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-20-04
- Cron Tab to Automatic Renewal 
  > echo "0 0,12 * * * root /opt/certbot/bin/python -c 'import random; import time; time.sleep(random.random() * 3600)' && sudo certbot renew -q" | sudo tee -a /etc/crontab > /dev/null
- Check for Renewal Certs
  > sudo certbot renew --dry-run
- Renewal Certificate
  > sudo certbot renew -q

## Nginx Config (more envs, same ec2)
```
# Aplicação UAT
  location /uat/ {
      proxy_pass http://127.0.0.1:5001;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }
# Aplicação DEV
  location /dev/ {
      proxy_pass http://127.0.0.1:5002;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }
```

## Troubleshotting
- chown -R <current_user> <repo_folder>