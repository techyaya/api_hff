from service.email_services import SendEmail

from apscheduler.schedulers.background import BackgroundScheduler
from service.email_services import SendEmail

scheduler = BackgroundScheduler()




def demarrer_scheduler():
    print("chronne execute")
    scheduler.add_job(
        SendEmail,
        trigger="cron",
        hour=12,
        minute=00
    )

    scheduler.add_job(
        SendEmail,
        trigger="cron",
        hour=17,
        minute=30
    )
    scheduler.start()

def arreter_scheduler():
    scheduler.shutdown()