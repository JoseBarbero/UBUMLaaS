import celery_worker as cw

if __name__ == "__main__":
    cw.app.run(debug = True)