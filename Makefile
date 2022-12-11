sh-webpack:
	sudo docker exec -it desparchado-webpack-1 sh

sh-web:
	sudo docker exec -it desparchado-web-1 sh

createsuperuser:
	docker exec -it desparchado-web-1 sh -c "cd app && python3 manage.py createsuperuser"

test:
	docker exec -it desparchado-web-1 sh -c "cd app && pytest"
