# ============================================================
# CyberEdu Bot — To'liq Professional Kiber Xavfsizlik o'quv boti
# Aiogram 3 | Bitta faylda
# ============================================================

import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import Bot, Dispatcher, Router, F, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatMemberStatus
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery, TelegramObject,
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


# ==================== CONFIG ====================
BOT_TOKEN = "8445478116:AAFqAQyHFshAs1zeWLpmVMYf4dMAx00-YzY"
CHANNEL_ID = -1003940243822
CHANNEL_LINK = "https://t.me/AniZone_UzBot"
ADMINS = [8318241400]
BOT_NAME = "CyberEdu Bot"
BOT_VERSION = "1.0.0 Professional"


# ==================== DATA: DARSLAR ====================
LESSONS = {
    "intro": {
        "title": "📘 1-dars: Kiber xavfsizlik nima?",
        "content": (
            "Kiber xavfsizlik — kompyuter tizimlari, tarmoqlar va ma'lumotlarni "
            "ruxsatsiz kirish, o'g'irlash, buzish yoki buzilishdan himoya qilishdir.\n\n"
            "Asosiy maqsadlar (CIA triada):\n"
            "• Confidentiality (Maxfiylik) — ma'lumotni faqat ruxsat etilganlar ko'radi\n"
            "• Integrity (Butunlik) — ma'lumot o'zgartirilmagan bo'lishi\n"
            "• Availability (Mavjudlik) — kerak paytda ishlashi\n\n"
            "Keyingi darsda asosiy tahdidlar bilan tanishamiz."
        )
    },
    "threats": {
        "title": "📘 2-dars: Asosiy tahdidlar",
        "content": (
            "Eng ko'p uchraydigan tahdidlar:\n\n"
            "1. Phishing va social engineering\n"
            "2. Malware (virus, trojan, ransomware)\n"
            "3. Zaif parollar va brute-force\n"
            "4. Yangilanmagan dasturlar (zero-day)\n"
            "5. Jamoat Wi-Fi orqali MitM\n"
            "6. Ichki tahdidlar (xodimlar)\n\n"
            "Ko'pchilik hujumlar texnik emas, balki odam omiliga asoslanadi."
        )
    },
    "password": {
        "title": "📘 3-dars: Kuchli parol va 2FA",
        "content": (
            "Yaxshi parol qoidalari:\n"
            "• Kamida 12–16 belgi\n"
            "• Katta-kichik harf + raqam + maxsus belgi\n"
            "• Har bir sayt uchun alohida\n"
            "• Parol menejeri ishlating (Bitwarden, KeePassXC)\n\n"
            "2FA ni har doim yoqing.\n"
            "SMS o'rniga Authenticator ilovasini afzal ko'ring."
        )
    },
    "safe_browsing": {
        "title": "📘 4-dars: Xavfsiz internet",
        "content": (
            "• HTTPS (qulf belgisi) bo'lgan saytlarga kiring\n"
            "• Shubhali havolalarni bosmang\n"
            "• Jamoat Wi-Fi'da VPN ishlating\n"
            "• Brauzerni va plaginlarni yangilab turing\n"
            "• Keraksiz ruxsatlarni o'chiring\n"
            "• uBlock Origin kabi bloklovchi foydali"
        )
    },
    "backup": {
        "title": "📘 5-dars: Zaxira nusxa (Backup)",
        "content": (
            "3-2-1 qoidasi:\n"
            "• 3 ta nusxa\n"
            "• 2 xil media (disk + cloud)\n"
            "• 1 ta offline / boshqa joyda\n\n"
            "Ransomware'dan eng yaxshi himoya — yaxshi zaxira."
        )
    },
    "kali_intro": {
        "title": "📘 6-dars: Kali Linux nima?",
        "content": (
            "Kali Linux — kiber xavfsizlik mutaxassislari va pentesterlar uchun "
            "mo'ljallangan Debian asosidagi distributiv.\n\n"
            "Unda yuzlab xavfsizlik vositalari oldindan o'rnatilgan:\n"
            "nmap, Metasploit, Burp Suite, Wireshark, Aircrack-ng va boshqalar.\n\n"
            "Muhim: Kali — qurol. Uni faqat qonuniy (o'z tizimingiz yoki "
            "yozma ruxsat) maqsadlarda ishlating.\n\n"
            "O'rganish uchun VirtualBox/VMware'da virtual mashinada o'rnating."
        )
    },
    "legal": {
        "title": "📘 7-dars: Qonuniy chegaralar",
        "content": (
            "Kiber xavfsizlikni o'rganish — yaxshi.\nLekin:\n\n"
            "❌ Boshqa odamlarning tizimlariga ruxsatsiz kirish — jinoyat\n"
            "❌ Boshqa Wi-Fi ni sindirish — jinoyat\n"
            "❌ DDoS qilish — jinoyat\n"
            "❌ Ma'lumot o'g'irlash — jinoyat\n\n"
            "✅ O'z tizimingizda mashq qilish — mumkin\n"
            "✅ Bug bounty dasturlari — mumkin\n"
            "✅ CTF musobaqalari — ajoyib\n"
            "✅ Yozma ruxsat bilan pentest — mumkin\n\n"
            "Har doim qonun doirasida ishlang."
        )
    },
}
LESSONS_ORDER = ["intro", "threats", "password", "safe_browsing", "backup", "kali_intro", "legal"]


# ==================== DATA: TERMINLAR ====================
CYBER_TERMS = {
    "phishing": {
        "title": "🎣 Phishing",
        "description": (
            "Phishing — firibgarlar o'zlarini ishonchli tashkilot qilib ko'rsatib, "
            "maxfiy ma'lumotlarni (parol, karta, SMS-kod) olishga urinishidir.\n\n"
            "📌 Qanday ishlaydi:\n"
            "• Soxta email/xabar yuboriladi\n"
            "• Havola orqali soxta saytga olib boriladi\n"
            "• Foydalanuvchi ma'lumot kiritadi\n\n"
            "🛡️ Himoya: havolani tekshiring, 2FA yoqing, rasmiy saytni o'zingiz yozing."
        )
    },
    "malware": {
        "title": "🦠 Malware",
        "description": (
            "Malware — zararli dasturlarning umumiy nomi.\n\n"
            "Turlari: Virus, Trojan, Ransomware, Spyware, Adware, Rootkit.\n\n"
            "🛡️ Himoya: antivirus, noma'lum manbadan dastur o'rnatmang, tizimni yangilang."
        )
    },
    "ransomware": {
        "title": "🔒 Ransomware",
        "description": (
            "Fayllarni shifrlab, ochish evaziga pul talab qiladigan malware.\n\n"
            "🛡️ Himoya: yaxshi zaxira (3-2-1), shubhali qo'shimchalarni ochmang."
        )
    },
    "vpn": {
        "title": "🌐 VPN",
        "description": (
            "VPN — internet ulanishini shifrlaydi va IP ni yashiradi.\n\n"
            "Jamoat Wi-Fi da juda foydali. Bepul VPN'lardan ehtiyot bo'ling."
        )
    },
    "firewall": {
        "title": "🧱 Firewall",
        "description": (
            "Tarmoq trafigini nazorat qilib, ruxsatsiz kirishni to'sadi.\n"
            "Hardware yoki Software bo'lishi mumkin."
        )
    },
    "2fa": {
        "title": "🔐 2FA / MFA",
        "description": (
            "Paroldan tashqari qo'shimcha tasdiqlash.\n"
            "SMS, Authenticator ilovasi, hardware key.\n"
            "Tavsiya: Authenticator ilovasi (Google/Microsoft/Authy)."
        )
    },
    "social_engineering": {
        "title": "🎭 Social Engineering",
        "description": (
            "Odamlarning ishonchini suiiste'mol qilib ma'lumot olish.\n"
            "Masalan: \"Bankdanman, kodni ayting\".\n"
            "Himoya: shoshilinch so'rovlarga ishonmang."
        )
    },
    "ddos": {
        "title": "💥 DDoS",
        "description": (
            "Saytni juda ko'p so'rov bilan ishlamay qolishiga olib kelish.\n"
            "Himoya (sayt egasi): CDN, rate limiting."
        )
    },
    "zero_day": {
        "title": "🕳️ Zero-day",
        "description": (
            "Hali hech kim bilmagan va tuzatilmagan zaiflik.\n"
            "Himoya: tizimni doim yangilab turing."
        )
    },
    "encryption": {
        "title": "🔏 Encryption",
        "description": (
            "Ma'lumotni faqat kalit bilan o'qish mumkin qilib o'zgartirish.\n"
            "AES, RSA, end-to-end encryption (Signal, WhatsApp)."
        )
    },
    "hash": {
        "title": "#️⃣ Hash",
        "description": (
            "Ma'lumotdan unique 'barmoq izi' yaratish.\n"
            "Parollarni saqlashda ishlatiladi (bcrypt, Argon2)."
        )
    },
    "bruteforce": {
        "title": "🔨 Brute-force",
        "description": (
            "Barcha variantlarni sinab parol topish.\n"
            "Himoya: kuchli parol, 2FA, account lockout."
        )
    },
    "sql_injection": {
        "title": "💉 SQL Injection",
        "description": (
            "Veb-ilovaga zararli SQL so'rov yuborib bazani boshqarish.\n"
            "Himoya: prepared statements, ORM, input validatsiya."
        )
    },
    "xss": {
        "title": "📜 XSS",
        "description": (
            "Saytga zararli JavaScript kiritib boshqa foydalanuvchi brauzerida ishlatish.\n"
            "Himoya: output encoding, CSP, HttpOnly cookie."
        )
    },
    "man_in_the_middle": {
        "title": "🕵️ Man-in-the-Middle",
        "description": (
            "Hujumchi ikki tomon o'rtasidagi aloqani tutib oladi.\n"
            "Himoya: VPN, HTTPS, certificate pinning."
        )
    },
}
TERMS_LIST = list(CYBER_TERMS.keys())


# ==================== DATA: KALI ====================
KALI_COMMANDS = {
    "nmap": {
        "title": "🗺️ nmap",
        "description": (
            "Tarmoq skaneri. Qurilmalar va ochiq portlarni aniqlash.\n\n"
            "• `nmap 192.168.1.1`\n"
            "• `nmap -sV target`\n"
            "• `nmap -p 80,443 target`\n\n"
            "⚠️ Faqat o'zingizga tegishli tarmoqda ishlating."
        )
    },
    "whoami": {
        "title": "👤 whoami",
        "description": "`whoami` — hozirgi foydalanuvchi nomi.\n`id` — batafsil ma'lumot."
    },
    "ifconfig_ip": {
        "title": "📡 ifconfig / ip",
        "description": (
            "• `ip a` — interfeyslar\n"
            "• `ip route` — marshrutlar\n"
            "• `ifconfig` — eski variant"
        )
    },
    "ls_cd_pwd": {
        "title": "📁 ls, cd, pwd",
        "description": (
            "• `pwd` — hozirgi papka\n"
            "• `ls -la` — batafsil ro'yxat\n"
            "• `cd papka` — o'tish\n"
            "• `cd ..` — yuqoriga"
        )
    },
    "cat_less_nano": {
        "title": "📄 cat, less, nano",
        "description": (
            "• `cat fayl` — ko'rish\n"
            "• `less fayl` — sahifalab\n"
            "• `nano fayl` — tahrirlash"
        )
    },
    "chmod_chown": {
        "title": "🔑 chmod, chown",
        "description": (
            "• `chmod 755 script.sh`\n"
            "• `chmod +x script.sh`\n"
            "• `chown user:group fayl`"
        )
    },
    "apt": {
        "title": "📦 apt",
        "description": (
            "• `sudo apt update`\n"
            "• `sudo apt upgrade`\n"
            "• `sudo apt install paket`\n"
            "• `sudo apt remove paket`"
        )
    },
    "sudo": {
        "title": "👑 sudo",
        "description": (
            "`sudo buyruq` — root huquqi bilan bajarish.\n"
            "`sudo -i` — root shell."
        )
    },
    "grep_find": {
        "title": "🔍 grep, find",
        "description": (
            "• `grep -r \"matn\" /papka`\n"
            "• `find / -name \"*.conf\"`"
        )
    },
    "ps_top_htop": {
        "title": "📊 ps, top, htop",
        "description": (
            "• `ps aux` — jarayonlar\n"
            "• `top` / `htop` — monitoring\n"
            "• `kill PID` — to'xtatish"
        )
    },
    "netstat_ss": {
        "title": "🔌 netstat / ss",
        "description": (
            "• `ss -tuln` — tinglayotgan portlar\n"
            "• `ss -tunap` — ulanishlar + jarayon"
        )
    },
    "tcpdump": {
        "title": "📦 tcpdump",
        "description": (
            "Paket ushlash (faqat o'quv/ruxsat bilan).\n"
            "• `sudo tcpdump -i eth0`\n"
            "• `sudo tcpdump port 80`"
        )
    },
    "wireshark": {
        "title": "🦈 Wireshark",
        "description": "Grafik paket analizatori. Trafikni ko'rish va tahlil qilish uchun."
    },
    "metasploit": {
        "title": "💣 Metasploit",
        "description": (
            "Penetration testing platformasi.\n"
            "⚠️ Faqat o'z tizimingiz yoki yozma ruxsat bilan."
        )
    },
    "burpsuite": {
        "title": "🔶 Burp Suite",
        "description": "Veb-ilovalar xavfsizligini sinash vositasi (Proxy, Scanner va h.k.)."
    },
    "john_hashcat": {
        "title": "🔓 John / Hashcat",
        "description": "Parol hashlarini sinash (faqat o'z hashlaringiz yoki ruxsat bilan)."
    },
    "hydra": {
        "title": "🐉 Hydra",
        "description": "Tarmoq xizmatlariga brute-force (faqat ruxsat bilan)."
    },
    "aircrack": {
        "title": "📶 Aircrack-ng",
        "description": "Wi-Fi xavfsizligini sinash. Faqat o'z tarmog'ingizda."
    },
}
KALI_LIST = list(KALI_COMMANDS.keys())


# ==================== DATA: HIMOYA MASLAHATLARI ====================
TIPS_CONTENT = {
    "password": "🔐 <b>Parol va 2FA</b>\n\n• Har sayt uchun alohida kuchli parol\n• Parol menejeri ishlating\n• 2FA yoqing (Authenticator afzal)\n• Parolni hech kimga aytmang",
    "browsing": "🌐 <b>Xavfsiz internet</b>\n\n• Faqat HTTPS\n• Shubhali havolani bosmang\n• Brauzerni yangilang\n• uBlock Origin o'rnating",
    "backup": "💾 <b>Zaxira</b>\n\n• 3-2-1 qoidasi\n• Cloud + tashqi disk\n• Avtomatik zaxira sozlang",
    "mobile": "📱 <b>Telefon</b>\n\n• Ekran qulfi + biometrik\n• Faqat rasmiy do'kondan ilova\n• Ruxsatlarni tekshiring\n• Noma'lum APK o'rnatmang",
    "email": "📧 <b>Email</b>\n\n• Phishingni tanib oling\n• Qo'shimchalarni ochmang\n• 2FA yoqing\n• Maxfiy ma'lumotni email orqali yubormang",
    "home_network": "🏠 <b>Uy tarmog'i</b>\n\n• Router parolini o'zgartiring\n• WPA3/WPA2\n• Guest tarmoq oching\n• Firmware yangilang",
}


# ==================== QUIZ ====================
QUIZ_QUESTIONS = [
    {"q": "Phishing nima?", "options": ["Virus turi", "Firibgarlik orqali ma'lumot olish", "Firewall turi", "VPN"], "correct": 1},
    {"q": "2FA nima uchun kerak?", "options": ["Tezlikni oshirish", "Parol o'g'irlansa ham qo'shimcha himoya", "Fayl shifrlash", "Reklama bloklash"], "correct": 1},
    {"q": "Ransomware nima qiladi?", "options": ["Reklama ko'rsatadi", "Fayllarni o'chiradi", "Fayllarni shifrlab pul talab qiladi", "Tarmoqni tezlash tiradi"], "correct": 2},
    {"q": "Eng yaxshi parol qanday?", "options": ["Ism + yil", "12345678", "Uzun, murakkab va har sayt uchun alohida", "Faqat harflar"], "correct": 2},
    {"q": "Kali Linux asosan nima uchun?", "options": ["O'yin", "Kiber xavfsizlik va pentest (qonuniy)", "Video montaj", "Ofis"], "correct": 1},
    {"q": "Jamoat Wi-Fi da nima qilish kerak?", "options": ["Hech narsa", "VPN ishlatish", "Parollarni kiritish", "Firewall o'chirish"], "correct": 1},
    {"q": "CIA triadadagi 'C' nima?", "options": ["Computer", "Confidentiality (Maxfiylik)", "Cyber", "Control"], "correct": 1},
    {"q": "Zero-day nima?", "options": ["Bayram", "Hali tuzatilmagan zaiflik", "Antivirus", "Parol menejeri"], "correct": 1},
]


# ==================== KEYBOARDS ====================
def main_menu_kb() -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    b.row(KeyboardButton(text="📚 Darslar"), KeyboardButton(text="📖 Terminlar"))
    b.row(KeyboardButton(text="🐉 Kali Linux"), KeyboardButton(text="🛡️ Himoya maslahatlari"))
    b.row(KeyboardButton(text="❓ Quiz"), KeyboardButton(text="ℹ️ Bot haqida"))
    b.row(KeyboardButton(text="📢 Kanalga obuna"))
    return b.as_markup(resize_keyboard=True)


def lessons_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for key in LESSONS_ORDER:
        b.button(text=LESSONS[key]["title"], callback_data=f"lesson:{key}")
    b.adjust(1)
    b.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main"))
    return b.as_markup()


def lesson_nav_kb(current: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    idx = LESSONS_ORDER.index(current)
    nav = []
    if idx > 0:
        nav.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"lesson:{LESSONS_ORDER[idx-1]}"))
    if idx < len(LESSONS_ORDER) - 1:
        nav.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"lesson:{LESSONS_ORDER[idx+1]}"))
    if nav:
        b.row(*nav)
    b.row(
        InlineKeyboardButton(text="📋 Barcha darslar", callback_data="show_lessons"),
        InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="back_main")
    )
    return b.as_markup()


def terms_kb(page: int = 0, per_page: int = 8) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    start, end = page * per_page, (page + 1) * per_page
    for key in TERMS_LIST[start:end]:
        b.button(text=CYBER_TERMS[key]["title"], callback_data=f"term:{key}")
    b.adjust(1)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"terms_page:{page-1}"))
    if end < len(TERMS_LIST):
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"terms_page:{page+1}"))
    if nav:
        b.row(*nav)
    b.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main"))
    return b.as_markup()


def term_back_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="📖 Barcha terminlar", callback_data="show_terms"),
        InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="back_main")
    )
    return b.as_markup()


def kali_kb(page: int = 0, per_page: int = 8) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    start, end = page * per_page, (page + 1) * per_page
    for key in KALI_LIST[start:end]:
        b.button(text=KALI_COMMANDS[key]["title"], callback_data=f"kali:{key}")
    b.adjust(1)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"kali_page:{page-1}"))
    if end < len(KALI_LIST):
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"kali_page:{page+1}"))
    if nav:
        b.row(*nav)
    b.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main"))
    return b.as_markup()


def kali_back_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="🐉 Barcha buyruqlar", callback_data="show_kali"),
        InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="back_main")
    )
    return b.as_markup()


def tips_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for text, cb in [
        ("🔐 Parol va 2FA", "tip:password"),
        ("🌐 Xavfsiz internet", "tip:browsing"),
        ("💾 Zaxira nusxa", "tip:backup"),
        ("📱 Telefon himoyasi", "tip:mobile"),
        ("📧 Email xavfsizligi", "tip:email"),
        ("🏠 Uy tarmog'i", "tip:home_network"),
    ]:
        b.button(text=text, callback_data=cb)
    b.adjust(1)
    b.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main"))
    return b.as_markup()


def subscription_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="📢 Kanalga obuna bo'lish", url=CHANNEL_LINK))
    b.row(InlineKeyboardButton(text="✅ Obuna bo'ldim, tekshirish", callback_data="check_sub"))
    return b.as_markup()


def quiz_start_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="▶️ Quizni boshlash", callback_data="quiz_start"))
    b.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main"))
    return b.as_markup()


def quiz_answer_kb(qid: int, options: list) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for i, opt in enumerate(options):
        b.button(text=opt, callback_data=f"quiz_ans:{qid}:{i}")
    b.adjust(1)
    return b.as_markup()


# ==================== MIDDLEWARE ====================
class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: Dict[str, Any]) -> Any:
        bot = data.get("bot")
        user = None
        if isinstance(event, Message):
            user = event.from_user
            if event.text and event.text.startswith("/start"):
                return await handler(event, data)
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            if event.data == "check_sub":
                return await handler(event, data)
        if not user or not bot:
            return await handler(event, data)
        if user.id in ADMINS:
            return await handler(event, data)
        try:
            member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user.id)
            if member.status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR):
                return await handler(event, data)
        except Exception:
            return await handler(event, data)
        text = "⚠️ <b>Botdan foydalanish uchun kanalimizga obuna bo'lishingiz shart!</b>\n\nQuyidagi tugma orqali obuna bo'ling, keyin «Obuna bo'ldim» ni bosing."
        if isinstance(event, Message):
            await event.answer(text, reply_markup=subscription_kb(), parse_mode="HTML")
        elif isinstance(event, CallbackQuery):
            await event.answer("Avval kanalga obuna bo'ling!", show_alert=True)
            await event.message.answer(text, reply_markup=subscription_kb(), parse_mode="HTML")
        return


# ==================== ROUTER & HANDLERS ====================
router = Router()


class QuizState(StatesGroup):
    answering = State()


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    user = message.from_user
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user.id)
        is_sub = member.status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR)
    except Exception:
        is_sub = True
    if not is_sub:
        await message.answer(
            f"👋 Salom, <b>{user.full_name}</b>!\n\nBu bot — <b>Kiber Xavfsizlik</b> o'quv boti.\nAvval kanalga obuna bo'ling 👇",
            reply_markup=subscription_kb(), parse_mode="HTML"
        )
        return
    await message.answer(
        f"👋 Salom, <b>{user.full_name}</b>!\n\n🛡️ <b>{BOT_NAME}</b> ga xush kelibsiz!\n\n"
        f"• Kiber xavfsizlik asoslarini o'rganasiz\n• Terminlarni tushunasiz\n"
        f"• Kali Linux buyruqlarini bilib olasiz\n• Himoya usullarini o'rganasiz\n\nQuyidagi menyudan tanlang 👇",
        reply_markup=main_menu_kb(), parse_mode="HTML"
    )


@router.callback_query(F.data == "check_sub")
async def check_sub(callback: CallbackQuery, bot: Bot):
    user = callback.from_user
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user.id)
        is_sub = member.status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR)
    except Exception:
        is_sub = True
    if is_sub:
        await callback.answer("✅ Obuna tasdiqlandi!", show_alert=True)
        await callback.message.answer(f"✅ Rahmat! Endi botdan foydalanishingiz mumkin.\n\n🛡️ <b>{BOT_NAME}</b>", reply_markup=main_menu_kb(), parse_mode="HTML")
        try:
            await callback.message.delete()
        except Exception:
            pass
    else:
        await callback.answer("❌ Hali obuna bo'lmadingiz!", show_alert=True)


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("📖 <b>Yordam</b>\n\n/start — qayta ishga tushirish\n/help — yordam\n/about — bot haqida\n\nMenyudagi tugmalar orqali barcha bo'limlarga kirasiz.", parse_mode="HTML")


@router.message(F.text == "ℹ️ Bot haqida")
@router.message(Command("about"))
async def cmd_about(message: Message):
    await message.answer(
        f"🛡️ <b>{BOT_NAME}</b>\nVersiya: <code>{BOT_VERSION}</code>\n\n"\
    
