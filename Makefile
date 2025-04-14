web_container_name := desparchado-web-1
frontend_container_name := desparchado-frontend-1

build:
	docker-compose build

up:
	docker-compose up

test:
	sudo docker exec -it $(web_container_name) sh -c "cd app && pytest"

sh-frontend:
	sudo docker exec -it $(frontend_container_name) sh

sh-web:
	sudo docker exec -it $(web_container_name) sh

createsuperuser:
	docker exec -it $(web_container_name) sh -c "cd app && python3 manage.py createsuperuser"

sync_filbo_events:
	sudo docker exec -it $(web_container_name)  sh -c "cd app && python manage.py sync_filbo_events $(spreadsheet_id)"
