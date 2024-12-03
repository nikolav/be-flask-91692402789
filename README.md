# Reverse proxy nginx letsencrypt
# https://github.com/christianlempa/videos/tree/main/nginx-reverseproxy


# install nginx; stats default process
$ apt install nginx

# default server setup
# @/etc/nginx/sites-enabled/default
--
server {

  listen 80 default_server;
  listen [::]:80 default_server;

  server_name <SERVER_NAME>;

  location / {
    proxy_pass http://127.0.0.1:5000
    # additional attributes
  }

}
--

# reload nginx config
$ systemctl reload nginx

# install cerbot, and python plugin
$ apt install certbot python3-certbot-nginx

# get letsencrypt certificates with dns challenge
$ certbot --nginx -d <SERVER_NAME> [-d <SERVER_NAME2>] 

# verify scheduled cron autorenew job
$ cat /etc/cron.d/certbot

# test autorenew cron job
$ certbot renew --dry-run


# failed to solve: failed to register layer: write /usr/share/perl/5.36.0/File/Temp.pm: no space left on device

