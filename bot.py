import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

LESSONS = {
    'intro': {
        'title': '📚 Introduction to Forex',
        'content': """Welcome to Forex Trading! 

What is Forex? 🤔
Forex (Foreign Exchange) is where currencies are traded. It's the largest financial market in the world!

Think of it this way:
• When you travel and exchange money, that's forex
• Trading forex means buying one currency and selling another

Simple Example:
• EUR/USD = 1.10 means 1 Euro = 1.10 US Dollars
• If you think Euro will go up, you BUY
• If you think Euro will go down, you SELL

📊 Key Terms:
• PIP: Smallest price move (like 0.0001)
• Spread: Difference between buy and sell price
• Leverage: Borrowing money to trade bigger amounts

✅ Your first lesson: Start small, learn the basics!""",
        'next': 'basics'
    },
    'basics': {
        'title': '📈 Trading Basics',
        'content': """Simple Trading Rules:

1️⃣ NEVER risk more than 2% of your money per trade
2️⃣ Always use Stop Loss (protects your money)
3️⃣ Don't trade when you're emotional
4️⃣ Practice first with demo accounts

🎯 How to Read Charts:
• Green candle = Price went UP 📗
• Red candle = Price went DOWN 📕
• Lines connect the prices

💡 Pro Tip: Watch the news! Big news moves prices.

Remember: 90% of traders lose money. Be patient and learn!""",
        'next': 'strategies'
    },
    'strategies': {
        'title': '🎯 Simple Strategies',
        'content': """3 Easy Strategies for Beginners:

1️⃣ Support & Resistance
• Support = Price floor (like a trampoline) 
• Resistance = Price ceiling (like a roof)
• Buy at Support, Sell at Resistance

2️⃣ Trend Following
• If prices are going UP → BUY
• If prices are going DOWN → SELL
• "The trend is your friend!"

3️⃣ Moving Averages
• Average price over time
• If price crosses above average → BUY signal
• If price crosses below average → SELL signal

🚀 Start with Strategy 1, it's the simplest!""",
        'next': 'risk_management'
    },
    'risk_management': {
        'title': '🛡️ Risk Management',
        'content': """Most Important Lesson: PROTECT YOUR MONEY!

💰 Golden Rules:
1. Use Stop Loss EVERY time
2. Risk only 1-2% per trade
3. Never average down (adding to losing trades)
4. Take profits early (don't be greedy)

📝 Risk Calculator:
• Account Balance: $1000
• Risk: 2% = $20 per trade
• Stop Loss: 50 pips
• Position size = $20 / 50 pips = 0.4 lots

🚨 Warning: Leverage is dangerous!
1:100 leverage means $100 controls $10,000
Great profits... but huge losses too!

Always think: \"Can I lose this money?\"""",
        'next': 'psychology'
    },
    'psychology': {
        'title': '🧠 Trading Psychology',
        'content': """Your Mind is Your Biggest Enemy! 😱

Common Mistakes:
❌ FOMO (Fear Of Missing Out)
❌ Revenge Trading (chasing losses)
❌ Overtrading (too many trades)
❌ Moving Stop Loss (bad idea!)

✅ Winning Mindset:
• Stay calm and patient
• Accept losses - they're part of trading
• Follow your plan, not emotions
• Take breaks between trades

💪 Daily Routine:
1. Check economic calendar
2. Analyze 1-2 pairs only
3. Wait for setup
4. Execute plan
5. Review trades

Remember: Trading is 80% psychology, 20% strategy!""",
        'next': 'practice'
    },
    'practice': {
        'title': '🏋️ Practice Time!',
        'content': """Ready to Practice?

🎮 Demo Account:
• Open a demo account (free virtual money)
• Practice with $10,000 virtual money
• No risk, real skills!

📝 Your Homework:
1. Open a demo account
2. Practice 1 trade per day
3. Write down why you entered
4. Review results weekly

🔗 Demo Platforms (free):
• MetaTrader 4/5
• TradingView
• Thinkorswim

📊 Start with 1 currency pair (EUR/USD)
Trade small amounts first!

Next step: Try a demo trade and come back!""",
        'next': 'quiz'
    },
    'quiz': {
        'title': '📝 Quick Quiz!',
        'content': """Let's test what you learned! 

1️⃣ What does a green candle mean?
a) Price went up 
b) Price went down
c) Market is closed

2️⃣ How much should you risk per trade?
a) 50%
b) 2%
c) 100%

3️⃣ What is a Stop Loss?
a) A tool to protect your money
b) A type of currency
c) A trading platform

4️⃣ What's the first thing to do?
a) Open a demo account
b) Invest all your savings
c) Quit your job

Reply with your answers (e.g., "1a, 2b, 3a, 4a")""",
        'next': 'intro'
    }
}

user_progress = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message when /start is issued."""
    user = update.effective_user
    user_id = user.id
    
    user_progress[user_id] = {'current_lesson': 'intro'}
    
    welcome_text = f"""👋 Welcome {user.first_name} to Forex University!

I'll teach you Forex and Trading in simple, easy-to-understand lessons.

🎯 What you'll learn:
• Forex basics (what it is and how it works)
• Trading strategies (simple ones that work)
• Risk management (protect your money)
• Trading psychology (master your mind)
• And much more!

Let's start your journey to becoming a trader!

Click 'Start Learning' below 👇"""
    
    keyboard = [
        [InlineKeyboardButton("🚀 Start Learning", callback_data='lesson_intro')],
        [InlineKeyboardButton("📊 Check Progress", callback_data='progress')],
        [InlineKeyboardButton("❓ Help", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if user_id not in user_progress:
        user_progress[user_id] = {'current_lesson': 'intro'}
    
    if data.startswith('lesson_'):
        lesson_key = data.replace('lesson_', '')
        await send_lesson(query, lesson_key)
    
    elif data == 'progress':
        await show_progress(query)
    
    elif data == 'help':
        await show_help(query)
    
    elif data == 'menu':
        await start_menu(query)
    
    elif data == 'next_lesson':
        current = user_progress[user_id].get('current_lesson', 'intro')
        if current in LESSONS and LESSONS[current].get('next'):
            next_lesson = LESSONS[current]['next']
            await send_lesson(query, next_lesson)

async def send_lesson(query, lesson_key):
    """Send a specific lesson."""
    user_id = query.from_user.id
    
    if user_id not in user_progress:
        user_progress[user_id] = {'current_lesson': 'intro'}
        
    if lesson_key in LESSONS:
        lesson = LESSONS[lesson_key]
        user_progress[user_id]['current_lesson'] = lesson_key
        
        keyboard = [
            [InlineKeyboardButton("📖 Next Lesson", callback_data='next_lesson')],
            [InlineKeyboardButton("📚 Main Menu", callback_data='menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = f"📘 {lesson['title']}\n\n{lesson['content']}"
        await query.edit_message_text(message, reply_markup=reply_markup)
    else:
        await query.edit_message_text("Lesson not found. Returning to main menu...")
        await start_menu(query)

async def show_progress(query):
    """Show user's progress."""
    user_id = query.from_user.id
    if user_id not in user_progress:
        user_progress[user_id] = {'current_lesson': 'intro'}
        
    current = user_progress[user_id].get('current_lesson', 'intro')
    
    lesson_keys = list(LESSONS.keys())
    current_index = lesson_keys.index(current) if current in lesson_keys else 0
    total = len(lesson_keys)
    
    progress_text = f"""📊 Your Progress:

Current Lesson: {LESSONS[current]['title']}
Progress: {current_index + 1}/{total} lessons

💪 Keep going! You're doing great!

Tips:
• Complete all lessons for best results
• Practice what you learn
• Ask questions anytime"""
    
    keyboard = [
        [InlineKeyboardButton(f"📖 Continue: {LESSONS[current]['title']}", callback_data=f'lesson_{current}')],
        [InlineKeyboardButton("🏠 Main Menu", callback_data='menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(progress_text, reply_markup=reply_markup)

async def show_help(query):
    """Show help message."""
    help_text = """❓ Need Help?

📚 Commands:
• /start - Welcome & Main Menu
• /help - This help message

📖 How to use:
1. Click "Start Learning" to begin
2. Read each lesson carefully
3. Click "Next Lesson" to continue
4. Use "Main Menu" to navigate

💡 Tips:
• Take notes while learning
• Practice each strategy
• Ask if something is unclear

Got questions? Just ask me!"""
    
    keyboard = [
        [InlineKeyboardButton("🏠 Main Menu", callback_data='menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(help_text, reply_markup=reply_markup)

async def start_menu(query):
    """Show main menu."""
    keyboard = [
        [InlineKeyboardButton("🚀 Start Learning", callback_data='lesson_intro')],
        [InlineKeyboardButton("📊 Check Progress", callback_data='progress')],
        [InlineKeyboardButton("❓ Help", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🏠 Main Menu\n\nWhat would you like to do?",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages (for quiz answers)."""
    message_text = update.message.text.lower()
    
    if '1' in message_text and '2' in message_text and '3' in message_text and '4' in message_text:
        answers = message_text.replace(' ', '').split(',')
        correct = 0
        
        correct_answers = {
            '1a': True,
            '2b': True,
            '3a': True,
            '4a': True
        }
        
        for answer in answers:
            if answer in correct_answers:
                correct += 1
        
        if correct == 4:
            response = """🎉 PERFECT! You got all answers right!

You're ready to start trading (on demo first)!

🏆 What's next:
1. Open a demo account (takes 5 minutes)
2. Practice 1 trade per day
3. Keep learning and improving

Remember: Every expert was once a beginner! 🚀"""
        elif correct >= 2:
            response = f"""Good try! You got {correct}/4 correct.

📖 Review these lessons:
• Basics (for questions 1-2)
• Risk Management (for question 3)
• Intro (for question 4)

Keep learning, you're getting there! 💪"""
        else:
            response = """Let's review the basics again!

📚 Start from the beginning:
/start

Don't worry, forex takes time to learn! 😊"""
        
        await update.message.reply_text(response)
    else:
        response = """I'm here to teach you forex! 📚

Use the buttons below to navigate:
• Start Learning - Begin your journey
• Check Progress - See how far you've come
• Help - Get assistance

Or type /start to begin! 🚀"""
        
        keyboard = [
            [InlineKeyboardButton("🚀 Start Learning", callback_data='lesson_intro')],
            [InlineKeyboardButton("📊 Check Progress", callback_data='progress')],
            [InlineKeyboardButton("❓ Help", callback_data='help')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = """❓ Need Help?

📚 Commands:
• /start - Welcome & Main Menu
• /help - This help message

📖 How to use:
1. Click "Start Learning" to begin
2. Read each lesson carefully
3. Click "Next Lesson" to continue

Got questions? Just ask me!"""
    
    keyboard = [
        [InlineKeyboardButton("🏠 Main Menu", callback_data='menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(help_text, reply_markup=reply_markup)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log exceptions."""
    logger.error("Exception while handling an update:", exc_info=context.error)

def main():
    """Start the bot."""
    print("Starting Forex Teaching Bot...")
    
    if not TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN environment variable is not set!")
        return

    application = (
        Application.builder()
        .token(TOKEN)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .write_timeout(30.0)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    print("Bot is polling for updates...")
    application.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
