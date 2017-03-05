workon desparchado

git pull

pip install -r requirements.txt
./manage.py migrate
./manage.py collectstatic --no-input
django-admin compilemessages
