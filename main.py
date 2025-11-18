import logging
from datetime import time
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, filters, ContextTypes
)
from .config import BOT_TOKEN, SCHEDULER_INTERVAL, ADMIN_IDS
from .handlers import common, registration, payments, portfolio, admin, report
from .db import init_db
from .scheduler import check_subscriptions


# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.NOTSET,
    handlers=[
        logging.FileHandler("bot.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.disabled = False


def build_app():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # --- ثبت نام 6 ماهه ---
    reg_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(registration.reg_6_start, pattern="^reg_6$"),
        ],
        states={
            registration.REG_RECEIPT: [
                CallbackQueryHandler(registration.reg_6_start, pattern="^reg_6_continue$"),
                CallbackQueryHandler(registration.send_receipt_prompt, pattern="^send_receipt$"),
                MessageHandler(filters.PHOTO | filters.Document.IMAGE, registration.receive_receipt),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(common.back_to_main_menu, pattern="^back_to_main_menu$"),
        ],
        block=False,
    )

    # --- تمدید 6 ماهه ---
    renew_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(registration.renew_start, pattern="^renew$"),
            CallbackQueryHandler(registration.renew_send_receipt_prompt, pattern="^renew_send_receipt$"),
        ],
        states={
            registration.RENEW_RECEIPT: [
                MessageHandler(filters.PHOTO | filters.Document.IMAGE, registration.renew_receive_receipt),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(common.back_to_main_menu, pattern="^back_to_main_menu$"),
            CallbackQueryHandler(common.back_to_main_menu, pattern="^cancel$"),
        ],
        block=False,
    )

    # === ConversationHandlerها باید ابتدا اضافه شوند ===
    app.add_handler(reg_conv)
    app.add_handler(renew_conv)

    # === ویزارد مرحله‌ای قرارداد پرتفوی (با priority بالا) ===
    # group=-10 تا قبل از MessageHandlerهای عمومی اجرا شوند
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin.handle_portfolio_wizard), group=-10)

    # === سایر CommandHandler و CallbackQueryHandlerها ===
    app.add_handler(CommandHandler("start", common.start))
    app.add_handler(CallbackQueryHandler(common.my_status_callback, pattern="^my_status$"))
    app.add_handler(CallbackQueryHandler(common.start, pattern="^main_menu$"))
    app.add_handler(CommandHandler("admin", admin.admin_menu))
    app.add_handler(CallbackQueryHandler(registration.send_receipt_prompt, pattern="^send_receipt$"))
    app.add_handler(CallbackQueryHandler(common.start, pattern="^cancel$"))
    app.add_handler(CommandHandler("list_payments", payments.list_payments))
    app.add_handler(CallbackQueryHandler(payments.approve_payment_cb, pattern="^approve_"))
    app.add_handler(CallbackQueryHandler(payments.reject_payment_cb, pattern="^reject_"))
    app.add_handler(CallbackQueryHandler(portfolio.portfolio_short_cb, pattern="^portfolio$"))
    app.add_handler(CallbackQueryHandler(portfolio.portfolio_details_cb, pattern="^portfolio_details$"))
    app.add_handler(CallbackQueryHandler(portfolio.portfolio_agree_cb, pattern="^portfolio_agree$"))
    app.add_handler(CallbackQueryHandler(admin.admin_new_portfolios_cb, pattern="^admin_new_portfolios$"))
    app.add_handler(CallbackQueryHandler(admin.admin_approve_portfolio_cb, pattern="^admin_approve_portfolio_"))
    app.add_handler(CallbackQueryHandler(admin.admin_contact_portfolio_cb, pattern="^admin_contact_portfolio_"))
    app.add_handler(CallbackQueryHandler(admin.admin_reject_portfolio_cb, pattern="^admin_reject_portfolio_"))
    app.add_handler(CallbackQueryHandler(report.admin_reports_cb, pattern="^admin_reports$"))
    app.add_handler(CommandHandler("report", admin.cmd_report))
    app.add_handler(admin.admin_support_conv)
    app.add_handler(CallbackQueryHandler(admin.admin_new_deposits_cb, pattern="^admin_new_deposits$"))
    app.add_handler(CallbackQueryHandler(admin.admin_approve_payment_cb, pattern="^admin_approve_"))
    app.add_handler(CallbackQueryHandler(admin.admin_reject_payment_cb, pattern="^admin_reject_"))
    app.add_handler(CallbackQueryHandler(admin.admin_new_messages_cb, pattern="^admin_new_messages$"))
    app.add_handler(CallbackQueryHandler(admin.admin_prepare_reply_cb, pattern="^admin_replymsg_"))
    app.add_handler(CallbackQueryHandler(admin.admin_close_support_cb, pattern="^admin_closemsg_"))
    app.add_handler(CallbackQueryHandler(admin.admin_month_sum_cb, pattern="^admin_month_sum$"))
    
    app.add_handler(CallbackQueryHandler(admin.admin_broadcast_cb, pattern="^admin_broadcast$"), group=-20)
    app.add_handler(CallbackQueryHandler(common.contact_support_cb, pattern="^contact_support$"), group=-20)

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), common.support_message_handler), group=0)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), admin.admin_receive_broadcast_text), group=1)


    # MessageHandlerهای عمومی در گروه پیش‌فرض 0
    # توصیه: در ابتدای این توابع، اگر state ویزارد فعال است، return کنید تا مزاحم ویزارد نشوند.
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), admin.admin_receive_broadcast_text))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), common.support_message_handler))

    async def unauthorized_message(update, context):
        user_id = None
        if update.message:
            user_id = update.message.from_user.id
        elif update.callback_query:
            user_id = update.callback_query.from_user.id
        if user_id not in ADMIN_IDS:
            if update.message:
                await update.message.reply_text(
                    "❌ لطفاً فقط از دکمه‌های منو برای استفاده از ربات استفاده کنید."
                )
    app.add_handler(MessageHandler(filters.ALL, unauthorized_message))

    return app

def schedule_weekly_settlement(app):
    # جمعه ساعت ۱۲:۰۰ تهران == ۸:۳۰ UTC (اگر سرور بر اساس UTC است)
    app.job_queue.run_daily(
        admin.send_weekly_settlement,
        time=time(hour=8, minute=30),    # زمان UTC
        days=(4,),                       # 4 = جمعه
        name="weekly_settlement"
    )


def main():
    init_db()
    app = build_app()

    # برنامه‌ریزی وظیفه تسویه هفتگی
    schedule_weekly_settlement(app)

    # schedule periodic job using job_queue
    interval_seconds = int(SCHEDULER_INTERVAL) if SCHEDULER_INTERVAL else (60 * 60 * 6)

    async def periodic_job(context: ContextTypes.DEFAULT_TYPE):
        bot = context.application.bot
        try:
            check_subscriptions(bot)
        except Exception as e:
            logger.exception("Error in periodic subscription check: %s", e)

    app.job_queue.run_repeating(periodic_job, interval=interval_seconds, first=10)

    logger.info("Starting bot (run_polling)...")
    app.run_polling()
    logger.info("Bot stopped.")


if __name__ == "__main__":
    main()
