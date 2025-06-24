

install:
	pip install -r requirements.txt

clear_space:
	docker image prune -f
	docker container prune -f

build:
	git pull
	docker compose build web

release:
	make build
	docker compose stop web_run
	make clear_space
	docker compose up -d web_run

dump:
	docker exec -it db_1 sh -c "pg_dump db > dump.sql"
	docker cp db_1:/dump.sql dump.sql
	curl -X POST "https://api.telegram.org/bot<backup_bot_token>/sendDocument?chat_id=<chat_id>" --form "document=@dump.sql;type=text/csv" -H "Content-Type: multipart/form-data"

load_dump:
	docker cp ~/dump.sql db_1:/dump.sql
	docker exec -it db_1 sh -c "psql db < dump.sql"

run:
	gunicorn app.server.wsgi:application --bind 0.0.0.0:8000
