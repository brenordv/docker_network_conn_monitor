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
docker run -d --env-file=deploy.env --restart=unless-stopped --name conn_monitor -it raccoon_conn_monitor:latest
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
Edit the ```deploy.env``` and add/change the following lines:
```shell script
STATISTICS_API_PORT=10044
STATISTICS_API_HOST=0.0.0.0
```

To change the port, you also need to change the EXPOSE value in the Dockerfile.

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

# API routes
(Considering default host and ports. Change accordinly)

## Home
```flaskurlpath
https://localhost:10044/
```
Not yet implemented... 
Theoretically, will show a dashboard with all info.

## Getting all events
```flaskurlpath
https://localhost:10044/api/v1/statistics
```

## Getting all logs for a specific correlation_id
```flaskurlpath
https://localhost:10044/api/v1/statistics/<correlation_id>
```

## Showing summary with downtime.
```flaskurlpath
https://localhost:10044/api/v1/statistics?show=summary
https://localhost:10044/api/v1/statistics/<correlation_id>?show=summary
```