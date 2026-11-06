from service.email_services import SendEmail

from apscheduler.schedulers.background import BackgroundScheduler
from service.email_services import SendEmail

scheduler = BackgroundScheduler()

from service.excel_services import generer_excel_historique


def demarrer_scheduler():
    print("chronne execute")
    scheduler.add_job(
        SendEmail,
        trigger="cron",
        hour=9,
        minute=14
    )

    scheduler.add_job(
        generer_excel_historique,
        trigger="cron",
        hour=15,
        minute=37
    )
    scheduler.start()

def arreter_scheduler():
    scheduler.shutdown()