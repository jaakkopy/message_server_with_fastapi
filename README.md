1. Add the following to a .env file at the root of the project:
- CONNECTION_STR=\<connection string for a database\>
- SECRET_KEY=\<secret key for JWT\>
- ALGORITHM=\<algorithm used for signing the JWT\>
- ACCESS_TOKEN_EXPIRE_MINUTES=\<desired expiration time for the token in minutes\>

2. Start the container with:

```sh
sudo docker-compose up -d --build
```

3. Now the service should be running on port 5000 on localhost. Visit FastAPI's Swagger UI at: http://localhost:5000/docs