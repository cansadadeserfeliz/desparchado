web_container_name := desparchado-web-1
frontend_container_name := desparchado-frontend-1

build:
	docker-compose build

up:
	docker-compose up

test:
	docker exec -it $(web_container_name) sh -c "cd app && pytest"

collectstatic:
	docker exec -it $(web_container_name) sh -c "cd app && python3 manage.py collectstatic"

sh-frontend:
	docker exec -it $(frontend_container_name) sh

run-storybook:
	docker exec -it $(frontend_container_name) sh -c "npm run storybook"

build-storybook:
	docker exec -it $(frontend_container_name) sh -c "npm run build-storybook"

sh-web:
	docker exec -it $(web_container_name) sh

createsuperuser:
	docker exec -it $(web_container_name) sh -c "cd app && python3 manage.py createsuperuser"

django-shell:
	docker exec -it $(web_container_name) sh -c "cd app && python3 manage.py shell"

sync_filbo_events:
	docker exec -it $(web_container_name)  sh -c "cd app && python manage.py sync_filbo_events $(spreadsheet_id)"
