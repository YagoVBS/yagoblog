set -e

flask --app src.app db upgrade
gunicorn src.wsgi:app