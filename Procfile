web: gunicorn oghie.wsgi --chdir oghie --workers 2 --bind 0.0.0.0:$PORT --log-file -
release: python oghie/manage.py migrate --noinput && python oghie/manage.py collectstatic --noinput
