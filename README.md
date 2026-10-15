# Nginx Proxy Lab

A small hands-on project that shows how **Nginx** works as a **web server**, a **reverse proxy** and a **load balancer** in front of two identical backend containers.

```
Browser
   |  port 8080 (the only port open to the outside)
   v
+-------------------------------+
| Nginx                         |
|  /      -> serves index.html  |   web server
|  /api/  -> backend_pool       |   reverse proxy + load balancer
+---------------+---------------+
                | private Docker network (not reachable from outside)
        +-------+-------+
        v               v
   backend1:8000   backend2:8000      FastAPI apps
```

## What it demonstrates

| Concept | Where to see it |
|---|---|
| Web server (static files) | `location /` in `nginx/default.conf` serves `frontend/index.html` |
| Reverse proxy | `proxy_pass http://backend_pool;` forwards `/api/` requests to the apps |
| Load balancing (round robin) | `upstream backend_pool { ... }` with two servers; the response shows `served_by` alternating |
| Exposing only what is needed | Only `nginx` has `ports:`; the backends are reachable only inside the Docker network |
| Containers + Docker Compose | `docker-compose.yml` starts all three services together |

## Project structure

```
nginx-proxy-lab/
├── docker-compose.yml     # starts nginx + backend1 + backend2
├── nginx/default.conf     # the Nginx configuration (the heart of the project)
├── backend/               # small FastAPI app (Dockerfile, main.py, requirements.txt)
└── frontend/index.html    # static page with buttons that call /api/hello
```

## Run it

Requirements: Docker with Docker Compose.

```bash
docker compose up --build -d
docker compose ps
```

Open http://localhost:8080 and press **"Dergo 6 kerkesa"**. The `served_by` value alternates between `backend1` and `backend2`.

Or from the terminal:

```bash
for i in 1 2 3 4 5 6; do curl -s localhost:8080/api/hello | grep -o '"served_by":"[a-z0-9]*"'; done
```

## Experiments (this is where you learn)

1. **The backends are private.** Try `curl localhost:8000/api/hello`. It fails, because the backends have no published port. Only Nginx is reachable.
2. **Failover.** Stop one backend and keep sending requests:
   ```bash
   docker compose stop backend1
   for i in 1 2 3 4; do curl -s localhost:8080/api/hello | grep -o '"served_by":"[a-z0-9]*"'; done
   ```
   Everything still works, served by `backend2` only. Start it again with `docker compose start backend1`.
3. **502 Bad Gateway.** Stop both backends: `docker compose stop backend1 backend2`, then `curl -i localhost:8080/api/hello`. Nginx is alive but the app behind it is down, so you get `502`.
4. **Read the logs.** `docker compose logs -f nginx` shows every request.
5. **Break the config on purpose.** Remove a `;` in `nginx/default.conf`, then run:
   ```bash
   docker compose exec nginx nginx -t
   ```
   Fix it and reload without downtime: `docker compose exec nginx nginx -s reload`.
6. **Add a third backend.** Copy `backend2` in `docker-compose.yml` as `backend3`, add `server backend3:8000;` to the upstream block, then `docker compose up -d` and reload Nginx.

## Useful commands

```bash
docker compose up --build -d     # build and start in the background
docker compose logs -f nginx     # follow Nginx logs
docker compose exec nginx nginx -t        # test the config
docker compose exec nginx nginx -s reload # reload the config without downtime
docker compose down              # stop and remove everything
```

## Next steps (ideas)

- Add HTTPS with Let's Encrypt (Certbot) on a cloud VM and a real domain.
- Deploy to an Azure/DigitalOcean VM using a GitHub Actions pipeline.
- Add a database container and a `/api/items` endpoint.
- Try other balancing methods: `least_conn;` or `ip_hash;` inside the `upstream` block.
