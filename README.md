
# ##################################
# How To Deploy it
# ##################################

1. Clone the repository to your local PC
2. Go the the repo that you already clone (sevenretail)
3. run `docker-compose up --build -d` and wait until all the container start
4. To check if the container is started run `docker ps`
5. If all the container already start and in healthy status run 
`docker compose run --rm funnel_processor [room_id]` 
