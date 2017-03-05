workon desparchado

git pull

bower install
pip install -r requirements.txt
./manage.py migrate
./manage.py collectstatic --no-input
django-admin compilemessages
touch desparchado/local_settings.py
