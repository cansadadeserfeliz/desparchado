web_container_name := desparchado-web-1
frontend_container_name := desparchado-frontend-1

prod_web_container_name := desparchado_web

build:
	docker-compose build

up:
	docker-compose up

test:
	docker exec -it $(web_container_name) sh -c "cd app && pytest --cov-report=html"

lint:
	docker exec -it $(web_container_name) sh -c "cd app && ruff check --fix"

lint-all:
	docker exec -it $(web_container_name) sh -c "cd app && ruff check --fix"

collectstatic:
	docker exec -it $(web_container_name) sh -c "cd app && python3 manage.py collectstatic"

migrate:
	docker exec -it $(web_container_name) sh -c "cd app && python3 manage.py migrate"

sh-frontend:
	docker exec -it $(frontend_container_name) sh

build-frontend:
	docker exec -it $(frontend_container_name) sh -c "npm run build"

run-storybook:
	docker exec -it $(frontend_container_name) sh -c "npm run storybook"

build-storybook:
	docker exec -it $(frontend_container_name) sh -c "npm run build-storybook"

lint-scripts:
	docker exec -it $(frontend_container_name) sh -c "npm run lint-scripts"

sh-web:
	docker exec -it $(web_container_name) bash

createsuperuser:
	docker exec -it $(web_container_name) sh -c "cd app && python3 manage.py createsuperuser"

django-shell:
	docker exec -it $(web_container_name) sh -c "cd app && python3 manage.py shell"

axes-reset:
	docker exec -it $(web_container_name)  sh -c "cd app && python manage.py axes_reset"

migrate-markdown-to-html:
	docker exec -it $(web_container_name)  sh -c "cd app && python manage.py migrate_markdown_to_html"

sync-filbo-events:
	docker exec -it $(web_container_name)  sh -c "cd app && python manage.py sync_filbo_events $(spreadsheet_id)"

generate-random-event-data:
	docker exec -it $(web_container_name)  sh -c "cd app && python manage.py generate_random_event_data"

generate-random-history-data:
	docker exec -it $(web_container_name)  sh -c "cd app && python manage.py generate_random_history_data"
