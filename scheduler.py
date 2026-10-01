import os

from apscheduler.schedulers.background import BackgroundScheduler
from services.publish_service import publish_next_product


scheduler = BackgroundScheduler()


def start_scheduler(app):

    # Flask debug mode me duplicate scheduler se bachne ke liye
    if app.debug and os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        return

    def auto_publish():

        with app.app_context():

            try:
                result = publish_next_product()

                print("=" * 50)
                print("AUTO PUBLISH SUCCESS")
                print(result)
                print("=" * 50)

            except Exception as e:

                print("=" * 50)
                print("AUTO PUBLISH FAILED")
                print(e)
                print("=" * 50)

    # Duplicate job add na ho
    if scheduler.get_job("auto_publish") is None:

        scheduler.add_job(
            auto_publish,
            trigger="interval",
            minutes=5,
            id="auto_publish",
            replace_existing=True,
        )

    if not scheduler.running:
        scheduler.start()
        print("✅ Scheduler Started (Every 5 Minutes)")