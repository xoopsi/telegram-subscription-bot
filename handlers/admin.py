import re
import logging
import asyncio
from decimal import Decimal
from sqlalchemy import func
from bot.main import logger
from ..messages import MESSAGES
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from ..config import ADMIN_IDS, ACCESS_CODE_EXPIRY_HOURS, ONE_TIME_LINK_MAX_USES, CHANNEL_ID, MANAGERS_SHARE
from ..utils import export_csv, format_currency, generate_sequential_transaction_id, to_jalali_str, jalali_to_gregorian_datetime, pad_jalali, to_jalali_date_str
from ..db import SessionLocal, User, Payment, PaymentStatus, Subscription, SubscriptionStatus, PortfolioRequest, PortfolioStatus, SupportMessage, PortfolioContract, ContractStatus 


logger = logging.getLogger(__name__)

logger.debug("module handlers.admin loaded")

# استیت‌ها
ASKING_PORTFOLIO_AMOUNT = "ASKING_PORTFOLIO_AMOUNT"
ASKING_START_JALALI = "ASKING_START_JALALI"
ASKING_END_JALALI = "ASKING_END_JALALI"


# Conversation states for broadcast
BROADCAST_TEXT = 0

REPLY_SUPPORT = 1001

MAIN_MENU_KB = InlineKeyboardMarkup([
    [InlineKeyboardButton("بازگشت به منوی اصلی 🔙", callback_data="cancel")]
])


def normalize_jalali_input(s: str) -> str:

async def cmd_report(update: Update, context: ContextTypes.DEFAULT_TYPE):

def count_pending_payments(session):

def count_new_portfolios(session):

def count_new_support_messages(session):

def sum_approved_payments_this_month(session):

def sum_approved_payments_this_jalaliweek(session):

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

async def admin_new_deposits_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):

async def admin_approve_payment_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):

async def admin_reject_payment_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):

async def admin_new_portfolios_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):

async def admin_contact_portfolio_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):

async def admin_reject_portfolio_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):

async def admin_approve_portfolio_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):

async def handle_portfolio_amount_input(update: Update, context: ContextTypes.DEFAULT_TYPE):

async def handle_portfolio_start_date(update: Update, context: ContextTypes.DEFAULT_TYPE):

async def handle_portfolio_end_date_and_finalize(update: Update, context: ContextTypes.DEFAULT_TYPE):

async def admin_new_messages_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):

async def admin_prepare_reply_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):

async def admin_send_reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

async def admin_close_support_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):

async def admin_month_sum_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):

async def admin_week_sum_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):

sync def admin_broadcast_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):

async def admin_receive_broadcast_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

async def send_weekly_settlement(bot):

async def handle_portfolio_wizard(update, context):

admin_support_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(admin_prepare_reply_cb, pattern="^admin_replymsg_")],
    states={
        REPLY_SUPPORT: [
            MessageHandler(filters.TEXT & (~filters.COMMAND), admin_send_reply_message),
        ],
    },
    fallbacks=[],
    allow_reentry=True,
    block=False,
)
