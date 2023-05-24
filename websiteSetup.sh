# Sprint 5

# Declaring functions
print_green () {
   echo -e "\e[1;32m$1 \e[0m"
}

print_yellow () {
   echo -e "\e[1;33m$1 \e[0m"
}

print_red () {
   echo -e "\e[1;31m$1 \e[0m"
}

print_cyan () {
   echo -e "\e[1;36m$1 \e[0m"
}

# Main code
print_cyan "Running website installation and update script...\n"

if [[ `ls | grep "websiteSetup.sh"` == "" ]]; then
	print_red "Must be run from the root of the repository"
	exit
fi

cd web

# Installing NPM if it isn't already installed
print_yellow "1. Checking if NPM is installed..."
if [[ `npm -v | grep "command not found"` -ne "" ]]; then
   print_red "NPM is not installed, installing..."
   sudo apt-get -y --force-yes install npm > /dev/null 2>&1
   print_green "NPM has been installed\n"
else
   print_green "NPM is already installed\n"
fi

# Installing JQuery if it isn't already installed
print_yellow "2. Checking if JQuery is installed..."
if [[ `npm list | grep "jquery"` == "" ]]; then
   print_red "JQuery is not installed, installing..."
   npm install jquery > /dev/null 2>&1
   print_green "JQuery has been installed\n"
else
   print_green "JQuery is already installed\n"
fi

# Installing ReactJS if it isn't already installed
print_yellow "3. Checking if ReactJS is installed..."
if [[ `npm list | grep "react"` == "" ]]; then
   print_red "ReactJS is not installed, installing..."
   npm install react > /dev/null 2>&1
   print_green "ReactJS has been installed\n"
else
   print_green "ReactJS is already installed\n"
fi

# Installing React Bootstrap if it isn't already installed
print_yellow "4. Checking if React Bootstrap is installed..."
if [[ `npm list | grep "bootstrap"` == "" ]]; then
   print_red "React Bootstrap is not installed, installing..."
   npm install react-bootstrap > /dev/null 2>&1
   print_green "React Bootstrap has been installed\n"
else
   print_green "React Bootstrap is already installed\n"
fi

# Installing Nginx if it isn't already installed
print_yellow "5. Checking if Nginx is installed..."
if [[ `sudo nginx -v | grep "command not found"` -ne "" ]]; then
   print_red "Nginx is not installed, installing..."
   sudo apt -y --force-yes install nginx > /dev/null 2>&1
   print_green "Nginx has been installed\n"
else
   print_green "Nginx is already installed\n"
fi

# Changing where html file for Nginx are found
print_yellow "6. Checking if Nginx is index.html is in the right location..."
if [[ `cat "/etc/nginx/sites-enabled/default" | grep "/var/www/html/index"` != "" ]]; then
	print_red "Nginx is not using the correct html file, fixing..."
	original=`cat "/etc/nginx/sites-enabled/default" | grep "/var/www/html/index"`
	
	#Python code to replace the old root location with the new one
	sudo python << EOF
with open('/etc/nginx/sites-enabled/default', 'r+') as f:
	file = f.read()
	file = file.replace('$original', '\troot $(pwd)/build;')
	f.seek(0)
	f.write(file)
EOF
	print_green "Nginx is now using the correct html file\n"
else
	print_green "Nginx is already using the correct html file\n"
fi

# Installing ssl
print_yellow "7. Checking if openssl is correctly installed..."
if [[ `openssl version | grep "command not found"` -ne "" ]]; then
   print_red "openssl is not installed, installing..."
   sudo apt-get install openssl
   printf 'CA\nOntario\nGuelph\nTeam1\n\n131.104.49.100\n\n' | sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/nginx.key -out /etc/ssl/certs/nginx.crt
   sudo openssl dhparam -out /etc/nginx/dhparam.pem 4096
   cat 'ssl_certificate /etc/ssl/certs/nginx.crt;
ssl_certificate_key /etc/ssl/private/nginx.key;

ssl_protocols TLSv1.2;
ssl_prefer_server_ciphers on;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
ssl_session_timeout 10m;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off;
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";

ssl_dhparam /etc/nginx/dhparam.pem;
ssl_ecdh_curve secp384r1;' > /etc/nginx/snippets/self-signed.conf
   print_green "openssl has been installed and setup\n"
else
   print_green "openssl is already installed\n"
fi

# Enabling SSL in NGINX
print_yellow "8. Enabling SSL in NGINX..."
if [[ `cat "/etc/nginx/sites-enabled/default" | grep "include snippets/self-signed.conf"` != "" ]]; then
	print_red "Nginx is not using the config file for SSL, fixing..."
	original=`cat "/etc/nginx/sites-enabled/default" | grep "include snippets/self-signed.conf"`
	
	#Python code to replace the old root location with the new one
	sudo python << EOF
with open('/etc/nginx/sites-enabled/default', 'r+') as f:
	file = f.read()
	file = file.replace('$original', '\tinclude snippets/self-signed.conf;\n\tlisten 443 ssl default_server;\n\tlisten [::]:443 ssl default_server;')
	f.seek(0)
	f.write(file)
EOF
	print_green "Nginx is now setup for self-signed SSL\n"
else
	print_green "Nginx is already using self-signed SSL\n"
fi


# Restarting Nginx
print_yellow "9. Restarting Nginx..."
sudo systemctl restart nginx
print_green "Setup complete"

