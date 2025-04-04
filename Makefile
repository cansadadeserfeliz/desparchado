build:
	docker-compose build

up:
	docker-compose up

sync_filbo_events:
	sudo docker exec -it desparchado-web-1  sh -c "cd app && python manage.py sync_filbo_events $(spreadsheet_id)"


