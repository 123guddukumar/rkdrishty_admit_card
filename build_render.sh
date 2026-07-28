#!/opt/render/project/src/.venv/bin/activate
# (Render automatically handles virtual environment creation, so we just run standard commands)

echo "Starting Render build steps..."

# Install dependencies
pip install -r requirements.txt

# Run migrations on Supabase database
python manage.py migrate --noinput

# Collect static files for WhiteNoise serving
python manage.py collectstatic --noinput --clear

echo "Render build complete."
