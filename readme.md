# What is this thing and how does it work?
This is a simple application that monitors your internet connection and logs the downtime.
It works by sending regular get requests to a few sites. 
If the request is through (no matter if the site is up or not), your internet is working. 
If there's an exception or timeout, your internet is down.

I bet there's more elegant ways to do this, but this is good enough.

If the variables TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are set, you'll receive a message in your Telegram when your
internet is back up.

There's also an API that shows you the current info. 


# How to use
You need to install Docker on your machine, in a raspberry or in some machine that wil lbe connected to the internet.

## Installing Docker
### On windows or Mac:
Follow these instructions: https://www.docker.com/products/docker-desktop

### On Linux:
Follow these instructions: https://runnable.com/docker/install-docker-on-linux

## Building the Docker image
In the root directory of this project, run the command:
```shell script
docker build -t raccoon_conn_monitor:latest .
```
You can use the scripts ```build.bat``` or ```build.sh``` as a shortcut. 

## Running the application
### Using docker compose
```shell script
docker-compose up -d
```  

### Command line
```shell script
docker run -d --env-file=deploy.env -p 10044:10044 --restart=unless-stopped --name conn_monitor -it raccoon_conn_monitor:latest
```


# Configuration
## Sending a message to notify when internet is back (using Telegram)
Edit the ```deploy.env``` and add/change the following lines:
```shell script
TELEGRAM_BOT_TOKEN=[the token to your telegram bot. be careful with it]
TELEGRAM_CHAT_ID=[id of the chat that will receive the message]
```

## Changing delay between internet checks.
The default delay/pause is 60 seconds
Edit the ```deploy.env``` and add/change the following lines:
```shell script
SECONDS_BETWEEN_CHECKS=60
```

## Changing host and port for the info api
The default host is **0.0.0.0** and the default port is **10044**.
Edit the ```deploy.env``` and add/change the following line:
```shell script
STATISTICS_API_HOST=0.0.0.0
```

To change the port, you also need to:
 1. change the EXPOSE value in the Dockerfile.
 2. change the port in the -p parameter in the run command.
 or
 3. change the port in the docker-compose file.


# History Database
## How to use the database 
You need something that can access the database info. I recommend using DBeaver (https://dbeaver.io)

## Copying the database from the container to the host
```shell script
docker cp conn_monitor:/app/statistics.db .
```
You can use the scripts ```copy_statistics_to_host.bat``` or ```copy_statistics_to_host.sh``` as a shortcut.

## Sample queries
### SQL
Here's some queries to see whats going on.
```sqlite
-- All events logged.
select * from connection_history;

-- Every time the internet went down.
select * from connection_history where event = 'disconnected';

-- Orphan events
select ch.correlation_id as "Correlation Id", count(correlation_id) as "Count" from connection_history ch
    where (select count(correlation_id) from connection_history ch2 where ch2.correlation_id = ch.correlation_id) != 2
    group by ch.correlation_id;

-- Select summary (with my crappy query)
select
       distinct ch.correlation_id as "Correlation ID"
     , (select event_timestamp from connection_history down where down.correlation_id = ch.correlation_id and event = 'disconnected') as "Disconnected At"
     , (select event_timestamp from connection_history up where up.correlation_id = ch.correlation_id and event = 'connected') as "Reconnected At"
     , (julianday((select event_timestamp from connection_history up where up.correlation_id = ch.correlation_id and event = 'connected')) -
        julianday((select event_timestamp from connection_history down where down.correlation_id = ch.correlation_id and event = 'disconnected')))as "Downtime in Days"
    from connection_history ch;
```


# Information API
(Considering default host and ports. Change accordinly)

## Home
```api
[GET] http://localhost:10044
```
Not yet implemented... 
Theoretically, will show a dashboard with all info.

## Getting all events
```api
[GET] http://localhost:10044/api/v1/statistics
```
#### Curl Example
```shell script
curl --request GET --url http://localhost:10044/api/v1/statistics
```

## Getting events for a specific correlation_id
```api
[GET] http://localhost:10044/api/v1/statistics/<correlation_id>
```
#### Curl Example
```shell script
curl --request GET --url http://localhost:10044/api/v1/statistics/30c993b3-0aae-48cb-a137-d5980b56269f
```

## Showing summary with downtime for every event.
```api
[GET] http://localhost:10044/api/v1/statistics/summary
```
#### Curl Example
```shell script
curl --request GET --url http://localhost:10044/api/v1/statistics/summary
```

## Showing summary with downtime for all events of a specific correlation_id
```api
[GET] http://localhost:10044/api/v1/statistics/<correlation_id>/summary
```
#### Curl Example
```shell script
curl --request GET --url http://localhost:10044/api/v1/statistics/30c993b3-0aae-48cb-a137-d5980b56269f/summary
```

## Import events from another instance of the API
```api
[POST] http://localhost:10044/api/v1/statistics
```
#### Post body
```json
{
   "url": "http://another_host:10044/api/v1/statistics"
}
```

#### Curl Example
```shell script
curl --request POST \
  --url http://localhost:10044/api/v1/statistics \
  --header 'content-type: application/json' \
  --data '{
	"url": "http://skyrasp4:10044/api/v1/statistics"
}'
```
