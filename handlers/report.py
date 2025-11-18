
import os
import base64
import datetime
from telegram import Update
from ..config import ADMIN_IDS
import matplotlib.pyplot as plt
from matplotlib import rcParams
import arabic_reshaper
from bidi.algorithm import get_display
from ..utils import to_jalali_str
from telegram.ext import ContextTypes
from ..db import SessionLocal, Subscription, SubscriptionStatus, User
from .registration import payment_income_stats, payment_cumulative
from .portfolio import portfolio_contracts_stats, portfolio_bar_chart

# فونت فارسی
rcParams['font.family'] = 'Tahoma'  # یا 'IRANSans', 'Vazir', 'B Nazanin'
rcParams['axes.unicode_minus'] = False  # برای نمایش منفی صحیح


async def admin_reports_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id not in ADMIN_IDS:
        await query.edit_message_text("شما دسترسی ندارید.")
        return

    # ساخت گزارش
    html_report = generate_report()
    now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"report_{now}.html"
    report_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'reports')
    os.makedirs(report_dir, exist_ok=True)
    file_path = os.path.join(report_dir, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_report)

    # ارسال فایل به ادمین
    await context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=open(file_path, "rb"),
        filename=filename,
        caption="📄 گزارش کامل فعالیت‌های کانال\n(جهت مشاهده کامل نمودارها فایل را ذخیره و با مرورگر باز کنید)"
    )


def image_to_datauri(path):
    with open(path, "rb") as img_file:
        b64 = base64.b64encode(img_file.read()).decode("utf-8")
    ext = os.path.splitext(path)[1][1:].lower()
    mime = f"image/{'png' if ext == 'png' else 'jpeg'}"
    return f"data:{mime};base64,{b64}"


# -- پای چارت اعضا
def generate_members_pie_chart(plan_6_count, plan_portfolio_count):
    import matplotlib.pyplot as plt
    import os
    import datetime

    # مسیر فولدر charts
    charts_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'charts')
    os.makedirs(charts_dir, exist_ok=True)

    # داده‌ها
    pie_vals = [plan_6_count, plan_portfolio_count]
    pie_labels = ['شش ماهه', 'سبدگردانی']
    pie_labels = [get_display(arabic_reshaper.reshape(label)) for label in pie_labels]
    pie_colors = ['#1976d2', '#ffd600']

    # اسم فایل منحصربه‌فرد
    now_str = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    pie_file = f"membership_pie_{now_str}.png"
    pie_path = os.path.join(charts_dir, pie_file)

    # رسم نمودار پای با پس‌زمینه شفاف و کادر مشکی
    fig, ax = plt.subplots(figsize=(4,4), facecolor='none')
    wedges, texts, autotexts = ax.pie(
        pie_vals,
        labels=pie_labels,
        colors=pie_colors,
        startangle=90,
        autopct='%1.0f%%',
        wedgeprops={'linewidth': 1.5, 'edgecolor': 'black'}
    )

    # استفاده از فونت فارسی برای لیبل‌ها و درصدها
    for t in texts + autotexts:
        t.set_fontname('Tahoma')
        t.set_fontsize(10)

    # عنوان نمودار
    title_text = get_display(arabic_reshaper.reshape("ترکیب اعضا"))
    ax.set_title(title_text, fontsize=13, fontname='Tahoma')
    ax.set_aspect('equal')

    # افزودن کادر مشکی دور نمودار
    for spine in ax.spines.values():
        spine.set_edgecolor('black')
        spine.set_linewidth(1.5)

    # ذخیره نمودار
    plt.tight_layout()
    plt.savefig(pie_path, transparent=True, bbox_inches='tight', pad_inches=0.2)
    plt.close()

    return pie_path


def generate_report():
    session = SessionLocal()
    now = datetime.datetime.now()
    now_jalali_full = to_jalali_str(now)
    parts = now_jalali_full.split(' ')
    now_jalali = parts[0] if len(parts) > 0 else '-'
    now_time = parts[1] if len(parts) > 1 else '-'

    # -- آمار اعضا
    plan_6_count = session.query(Subscription).filter(
        Subscription.plan_type == "6month",
        Subscription.status == SubscriptionStatus.active
    ).count()
    plan_portfolio_count = session.query(Subscription).filter(
        Subscription.plan_type == "portfolio",
        Subscription.status == SubscriptionStatus.active
    ).count()
    total_members = plan_6_count + plan_portfolio_count

    # تولید پای چارت و Data URI
    PIE_PATH = generate_members_pie_chart(plan_6_count, plan_portfolio_count)
    PIE_URI = image_to_datauri(PIE_PATH)

    # -- گزارش درآمد (پلن شش ماهه)
    payment_stats = payment_income_stats()
    pie_path = payment_cumulative()
    INC_CHART_URI = image_to_datauri(pie_path) if pie_path else ""

    # -- گزارش قرارداد سبدگردانی
    portfolio_stats = portfolio_contracts_stats()
    portfolio_chart_path = portfolio_bar_chart()
    PORTF_CHART_URI = image_to_datauri(portfolio_chart_path) if portfolio_chart_path else ""

    # -- ۱۰ نفر جدید
    new_joined = session.query(Subscription, User).join(User, Subscription.user_id == User.id).filter(
        Subscription.status == SubscriptionStatus.active
    ).order_by(Subscription.start_date.desc()).limit(10).all()
    recent_members = []
    for s, u in new_joined:
        telegram_id = u.telegram_id
        username = u.username or (u.full_name or "-")
        plan_str = "شش ماهه" if s.plan_type == "6month" else ("سبدگردانی" if s.plan_type == "portfolio" else s.plan_type)
        join_date = to_jalali_str(s.start_date) if s.start_date else "-"
        recent_members.append({
            "telegram_id": telegram_id,
            "username": username,
            "plan": plan_str,
            "join_date": join_date
        })

    # -- اعضای نزدیک پایان مهلت (تا 10 روز دیگر)
    soon_expiring = session.query(Subscription, User).join(User, Subscription.user_id == User.id).filter(
        Subscription.status == SubscriptionStatus.active,
        Subscription.end_date != None,
        Subscription.end_date >= now,
        Subscription.end_date <= now + datetime.timedelta(days=10)
    ).order_by(Subscription.end_date).limit(10).all()
    expiring_members = []
    for s, u in soon_expiring:
        telegram_id = u.telegram_id
        username = u.username or (u.full_name or "-")
        plan_str = "شش ماهه" if s.plan_type == "6month" else ("سبدگردانی" if s.plan_type == "portfolio" else s.plan_type)
        end_date = to_jalali_str(s.end_date) if s.end_date else "-"
        expiring_members.append({
            "telegram_id": telegram_id,
            "username": username,
            "plan": plan_str,
            "end_date": end_date
        })

    session.close()

    # --- HTML template (Embed images)
    html = f"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<link href="https://cdn.jsdelivr.net/gh/rastikerdar/iransansfanum-font@v2.2.0/dist/font-face.css" rel="stylesheet" />
<title>گزارش فعالیت کانال اختصاصی دکتر کریمی</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.rtl.min.css">

<style>
body {{
    font-family: iransansfanum, sans-serif;
    background: #f8fafb;
    color: #222;
}}
.rbox {{
    background: #f1f1f8;
    border-radius: 20px;
    box-shadow: 0 2px 7px #d3d3d3a8;
    margin-bottom: 40px;
    padding: 1.7rem 1.3rem 1.5rem 1.3rem;
    overflow-x: auto;
}}
.section-title {{
    background: #d6d6e3;
    color: #000;
    font-weight: bold;
    text-align: center;
    padding: 12px;
    border-radius: 12px;
    font-size: 18px;
    margin-bottom: 20px;
}}
.label {{
    font-weight: normal;
    margin-left: 7px;
}}
.headtd {{
    font-weight: bold;
    background: #e0e0e0;
}}
td, th {{
    font-size: 15px !important;
    vertical-align: middle;
}}
.table {{
    margin-bottom: 0 !important;
}}
@media (max-width: 768px) {{
    .rbox {{
        padding: 1rem;
    }}
    table {{
        font-size: 13px;
    }}
    img {{
        max-width: 100% !important;
        height: auto;
    }}
}}
</style>
</head>

<body class="container mt-4 p-3">

    <h3 class="mb-3 text-center fw-bold">گزارش فعالیت‌های کانال اختصاصی دکتر کریمی</h3>
    <div class="text-center mb-4">
        <p class="mb-1"><b>تاریخ گزارش:</b> {now_jalali}</p>
        <p class="text-muted" style="font-size:14px;">🕒 ساعت گزارش: {now_time}</p>
    </div>

    <!-- اعضای کانال -->
    <div class="section-title">اعضای کانال</div>
    <div class="row align-items-center rbox">
        <div class="col-md-7 mb-3 mb-md-0">
            <table class="w-100">
                <tr>
                    <td class="label">۱- تعداد اعضای پلن ۶ ماهه:</td>
                    <td class="text-primary">{plan_6_count}</td>
                </tr>
                <tr>
                    <td class="label">۲- تعداد اعضای پلن سبدگردانی:</td>
                    <td class="text-warning">{plan_portfolio_count}</td>
                </tr>
                <tr>
                    <td class="label">۳- مجموع کل اعضا:</td>
                    <td class="text-success fw-bold">{total_members}</td>
                </tr>
            </table>
        </div>
        <div class="col-md-5 text-center">
            <img src="{PIE_URI}" alt="PieChart" style="max-width:220px;"/>
        </div>
    </div>

    <!-- گزارش درآمدهای پلن شش ماهه -->
    <div class="section-title">گزارش درآمدهای پلن شش ماهه</div>
    <div class="row align-items-center rbox">
        <div class="col-md-7 mb-3 mb-md-0">
            <table class="w-100">
                <tr>
                    <td class="label">درآمد یک ماه اخیر:</td>
                    <td class="text-success fw-bold">{payment_stats['1_month']['total_amount']:,} <span>تومان</span></td>
                </tr>
                <tr>
                    <td class="label">درآمد سه ماه اخیر:</td>
                    <td class="text-success fw-bold">{payment_stats['3_months']['total_amount']:,} <span>تومان</span></td>
                </tr>
                <tr>
                    <td class="label">درآمد شش ماه اخیر:</td>
                    <td class="text-success fw-bold">{payment_stats['6_months']['total_amount']:,} <span>تومان</span></td>
                </tr>
                <tr>
                    <td class="label">درآمد یک سال اخیر:</td>
                    <td class="text-success fw-bold">{payment_stats['1_year']['total_amount']:,} <span>تومان</span></td>
                </tr>
            </table>
        </div>
        <div class="col-md-5 text-center">
            <img src="{INC_CHART_URI}" alt="LineChart" style="max-width:340px;"/>
        </div>
    </div>

    <!-- گزارش قراردادهای پلن سبدگردانی -->
    <div class="section-title">گزارش قراردادهای پلن سبدگردانی</div>
    <div class="row align-items-center rbox">
        <div class="col-md-7 mb-3 mb-md-0">
            <table class="w-100">
                <tr>
                    <td class="label">قرارداد یک ماه اخیر:</td>
                    <td class="text-info">{portfolio_stats['1_month']['count']}</td>
                    <td class="text-success fw-bold">{portfolio_stats['1_month']['total_amount']:,} تومان</td>
                </tr>
                <tr>
                    <td class="label">قرارداد سه ماه اخیر:</td>
                    <td class="text-info">{portfolio_stats['3_months']['count']}</td>
                    <td class="text-success fw-bold">{portfolio_stats['3_months']['total_amount']:,} تومان</td>
                </tr>
                <tr>
                    <td class="label">قرارداد شش ماه اخیر:</td>
                    <td class="text-info">{portfolio_stats['6_months']['count']}</td>
                    <td class="text-success fw-bold">{portfolio_stats['6_months']['total_amount']:,} تومان</td>
                </tr>
                <tr>
                    <td class="label">قرارداد یک سال اخیر:</td>
                    <td class="text-info">{portfolio_stats['1_year']['count']}</td>
                    <td class="text-success fw-bold">{portfolio_stats['1_year']['total_amount']:,} تومان</td>
                </tr>
            </table>
        </div>
        <div class="col-md-5 text-center">
            <img src="{PORTF_CHART_URI}" alt="BarChart" style="max-width:340px;"/>
        </div>
    </div>

    <!-- اعضای تازه و اعضای نزدیک به پایان -->
    <div class="row">
        <div class="col-lg-6 col-md-12 col-12 rbox mb-4">
            <div class="section-title">اعضای تازه عضو شده به کانال</div>
            <div class="table-responsive">
                <table class="table table-striped table-sm">
                    <thead>
                        <tr class="headtd text-center">
                            <th>ردیف</th>
                            <th>آیدی تلگرام</th>
                            <th>نام کاربری/نام کامل</th>
                            <th>پلن</th>
                            <th>تاریخ عضویت</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([
                            f"<tr><td>{i+1}</td><td>{m['telegram_id']}</td><td>{m['username']}</td><td>{m['plan']}</td><td>{m['join_date']}</td></tr>"
                            for i, m in enumerate(recent_members)
                        ])}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="col-lg-6 col-md-12 col-12 rbox mb-4">
            <div class="section-title">اعضای نزدیک به پایان مهلت عضویت</div>
            <div class="table-responsive">
                <table class="table table-striped table-sm">
                    <thead>
                        <tr class="headtd text-center">
                            <th>ردیف</th>
                            <th>آیدی تلگرام</th>
                            <th>نام کاربری/نام کامل</th>
                            <th>پلن</th>
                            <th>تاریخ پایان عضویت</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([
                            f"<tr><td>{i+1}</td><td>{m['telegram_id']}</td><td>{m['username']}</td><td>{m['plan']}</td><td>{m['end_date']}</td></tr>"
                            for i, m in enumerate(expiring_members)
                        ])}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
"""
    return html
