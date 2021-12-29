# https://docs.docker.com/engine/install/centos/ --- instructions here

#uninstall any old docker stuff
sudo yum remove docker \
                  docker-client \
                  docker-client-latest \
                  docker-common \
                  docker-latest \
                  docker-latest-logrotate \
                  docker-logrotate \
                  docker-engine

#install utils
sudo yum install -y yum-utils
sudo yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

#install docker engine
sudo yum install docker-ce docker-ce-cli containerd.io

#turn on the docker service
sudo systemctl start docker # This will need done each time the system is restarted

#verify docker is running
sudo docker run hello-world


#set up docker compose
#https://docs.docker.com/compose/install/

#download it
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose


#change the permissions
sudo chmod +x /usr/local/bin/docker-compose

#make a symlink
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

#test it and make sure it works
docker-compose --version


#download the data from S3 --- jonathans bucket was cco-trainbot
#aws s3 cp cco-trainbot/Chat_Bot_API.zip Chat_Bot_API.zip

#unzip it
unzip Chat_Bot_API.zip

#remove the zip folder
rm Chat_Bot_API.zip

#move into the folder
cd Chat_Bot_API

#build the image
docker-compose build

#create a screen to run our image
screen -S Chat_Bot_API

#start the image
docker-compose up

#while the API is running, press the following key combo to detach from the screen keeping the API running

#hold down control and a and then press d

#now you are detached, you can shut down the instance

#to test the instance, you can run curl:
curl -X GET "http://0.0.0.0:8888/chat_bot/?text=hello%20my%20name%20is%20joe" -H  "accept: application/json"

#to reconnect to the instance with screen
screen -r #if there is only one screen

#to find out if there are more
screen -ls

#then reconnect to a screen with the screen-name
screen -r <replace-with-screen-name> 