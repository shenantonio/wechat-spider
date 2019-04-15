

python manage.py runserver 0.0.0.0:8001 &

python bin/extractor.py &
python bin/processor.py &
python bin/downloader.py &
python bin/scheduler.py  &
