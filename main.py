import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from config import Config

# Logging setup
logging.basicConfig(
    format=Config.LOG_FORMAT,
    level=getattr(logging, Config.LOG_LEVEL)
logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self):
        self.current_topic = None
        self.current_thread_id = None

    def new_session(self, topic_name, thread_id):
        self.current_topic = topic_name
        self.current_thread_id = thread_id
        logger.info(f"New session: {topic_name} (Thread: {thread_id})")

    def validate_user(self, user_id):
        if user_id not in Config.AUTHORIZED_USER_IDS:
            logger.warning(f"Unauthorized access: {user_id}")
            return False
        return True

session = SessionManager()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    if not session.validate_user(update.message.from_user.id):
        return
    await update.message.reply_text(Config.WELCOME_MESSAGE)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    if not session.validate_user(update.message.from_user.id):
        return
    await update.message.reply_text(Config.WELCOME_MESSAGE)

async def new_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create new forum topic"""
    if not session.validate_user(update.message.from_user.id):
        await update.message.reply_text("❌ Unauthorized")
        return

    try:
        topic_name = ' '.join(context.args) if context.args else None
        if not topic_name:
            await update.message.reply_text("Usage: /new <TOPIC_NAME>")
            return

        logger.info(f"Creating topic: {topic_name}")
        result = await context.bot.create_forum_topic(
            chat_id=Config.DEFAULT_GROUP_ID,
            name=topic_name
        )
        
        session.new_session(topic_name, result.message_thread_id)
        await update.message.reply_text(
            Config.TOPIC_CREATED_MSG.format(
                topic_name=topic_name,
                thread_id=result.message_thread_id
            )
        )

    except Exception as e:
        logger.error(f"Topic error: {e}", exc_info=True)
        await update.message.reply_text("⚠️ Topic creation failed")

async def copy_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all incoming content"""
    try:
        if not session.validate_user(update.message.from_user.id):
            return

        if not session.current_thread_id:
            await update.message.reply_text("⚠️ First create topic with /new <TOPIC>")
            return

        # Text messages
        if update.message.text:
            await context.bot.send_message(
                chat_id=Config.DEFAULT_GROUP_ID,
                text=update.message.text,
                message_thread_id=session.current_thread_id,
                entities=update.message.entities,
                parse_mode=None
            )
        
        # Media with captions
        elif update.message.caption:
            if update.message.photo:
                await context.bot.send_photo(
                    chat_id=Config.DEFAULT_GROUP_ID,
                    photo=update.message.photo[-1].file_id,
                    caption=update.message.caption,
                    caption_entities=update.message.caption_entities,
                    message_thread_id=session.current_thread_id,
                    parse_mode=None
                )
            elif update.message.video:
                await context.bot.send_video(
                    chat_id=Config.DEFAULT_GROUP_ID,
                    video=update.message.video.file_id,
                    caption=update.message.caption,
                    caption_entities=update.message.caption_entities,
                    message_thread_id=session.current_thread_id,
                    parse_mode=None
                )
            elif update.message.document:
                await context.bot.send_document(
                    chat_id=Config.DEFAULT_GROUP_ID,
                    document=update.message.document.file_id,
                    caption=update.message.caption,
                    caption_entities=update.message.caption_entities,
                    message_thread_id=session.current_thread_id,
                    parse_mode=None
                )
        
        # Media without captions
        else:
            if update.message.photo:
                await context.bot.send_photo(
                    chat_id=Config.DEFAULT_GROUP_ID,
                    photo=update.message.photo[-1].file_id,
                    message_thread_id=session.current_thread_id
                )
            elif update.message.video:
                await context.bot.send_video(
                    chat_id=Config.DEFAULT_GROUP_ID,
                    video=update.message.video.file_id,
                    message_thread_id=session.current_thread_id
                )
            elif update.message.document:
                await context.bot.send_document(
                    chat_id=Config.DEFAULT_GROUP_ID,
                    document=update.message.document.file_id,
                    message_thread_id=session.current_thread_id
                )

        await update.message.reply_text("✅ Content posted in group")

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        await update.message.reply_text(f"⚠️ Failed to post: {str(e)}")

def main():
    Config.validate()
    
    app = ApplicationBuilder().token(Config.TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("new", new_topic))
    
    # Content handler
    app.add_handler(MessageHandler(
        filters.ChatType.PRIVATE & (
            filters.TEXT |
            filters.VIDEO |
            filters.Document.ALL |
            filters.PHOTO
        ) & ~filters.COMMAND,
        copy_message
    ))
    
    logger.info("Bot started with welcome message and /new command")
    app.run_polling()

if __name__ == "__main__":
    main()
