# Lightshield Proxy
Ratelimiter and API-Key handler


### Setup
- Create a secrets.env file containing the `API_KEY` key.
- Assure that the `lightshield` docker network is already running. If its not needed or was renamed remove the 
entry from the compose file.
- Expand/Reduce the compose file according to which server you need a proxy for by copying and renaming one of the existing blocks.
- Run the project.
