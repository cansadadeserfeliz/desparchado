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

# Install pinned dependencies with hash verification (requires generated .txt files)
pip-install:
	docker exec -it $(web_container_name) sh -c "cd app && pip install --require-hashes -r requirements-dev.txt"

# Regenerate requirements.txt and requirements-dev.txt with pinned versions and hashes from .in files
pip-compile:
	docker exec -it $(web_container_name) sh -c "cd app && pip-compile --generate-hashes --output-file=requirements.txt requirements.in && pip-compile --generate-hashes --output-file=requirements-dev.txt requirements-dev.in"

# Same as pip-compile but upgrades all packages to the latest allowed versions first
pip-compile-upgrade:
	docker exec -it $(web_container_name) sh -c "cd app && pip-compile --upgrade --generate-hashes --output-file=requirements.txt requirements.in && pip-compile --upgrade --generate-hashes --output-file=requirements-dev.txt requirements-dev.in"

collectstatic:
	docker exec -it $(web_container_name) sh -c "cd app && python3 manage.py collectstatic"

migrate:
	docker exec -it $(web_container_name) sh -c "cd app && python3 manage.py migrate"

compilemessages:
	docker exec -it $(web_container_name) sh -c "cd app && django-admin compilemessages -l es"

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
	docker exec -it $(web_container_name) sh -c "cd app && python3 manage.py shell --verbosity=2"

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

## release-tag tag=<name>: Switch to main, pull latest, create and push the given tag, then return to the previous branch
release-tag:
	@scripts/create_release_tag.sh $(tag)

## latest-tag: Print the most recent tag reachable from main
latest-tag:
	@git fetch --tags -q && git tag --sort=-creatordate --merged main | head -1
