
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import aiosqlite

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def init_db():
    async with aiosqlite.connect('bot_data.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                first_name TEXT,
                balance INTEGER DEFAULT 0,
                referrer_id INTEGER,
                referrals_count INTEGER DEFAULT 0
            )
        ''')
        await db.commit()
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    referrer_id = None
    
    if args and args[0].isdigit():
        referrer_id = int(args[0])

    async with aiosqlite.connect('bot_data.db') as db:
        async with db.execute('SELECT id FROM users WHERE id = ?', (user.id,)) as cursor:
            existing_user = await cursor.fetchone()
            
            if not existing_user:
                await db.execute(
                    'INSERT OR IGNORE INTO users (id, first_name, referrer_id) VALUES (?, ?, ?)',
                    (user.id, user.first_name, referrer_id)
                )
                if referrer_id:
                    await db.execute('UPDATE users SET referrals_count = referrals_count + 1 WHERE id = ?', (referrer_id,))
                await db.commit()
                
                await update.message.reply_text(
                    f"আসসালামু আলাইকুম {user.first_name}!\n\n"
                    "আমাদের বটে স্বাগতম। আপনি সরাসরি ব্যালেন্স পাবেন না। "
                    "নিচের ভিডিওটি দেখে কমেন্ট করুন ও স্ক্রিনশট দিন। "
                    "ভেরিফিকেশন হলেই ব্যালেন্স যুক্ত হবে।\n\n"
                    "টাস্ক: [ইউটিউব শর্টস লিংক]"
                )
            else:
                await update.message.reply_text(f"আপনার অলরেডি অ্যাকাউন্ট আছে, {user.first_name}!")
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    async with aiosqlite.connect('bot_data.db') as db:
        async with db.execute('SELECT balance, referrals_count FROM users WHERE id = ?', (user.id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                bal, ref_count = row
                ref_link = f"https://t.me/{context.bot.username}?start={user.id}"
                await update.message.reply_text(
                    f"আসসালামু আলাইকুম {user.first_name}!\n\n"
                    f"আপনার ব্যালেন্স: {bal} টাকা\n"
                    f"মোট রেফার: {ref_count} জন\n\n"
                    f"আপনার রেফারেল লিংক:\n{ref_link}"
                )

if __name__ == '__main__':
    import asyncio
    asyncio.run(init_db())
    
    application = ApplicationBuilder().token(8926494752:AAEKyeKGR0ORHI9svIz-zDW4gIOEnHRygyw).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('balance', balance))
    
    application.run_polling()
