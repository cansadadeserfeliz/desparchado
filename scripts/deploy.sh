source /home/vero4ka/.virtualenvs/desparchado/bin/activate

git pull

bower install
pip install -r requirements.txt

source setenv.sh

./manage.py migrate
./manage.py collectstatic --no-input
django-admin compilemessages

touch desparchado/settings/production.py
