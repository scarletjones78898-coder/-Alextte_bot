async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error("Exception while handling an update:", exc_info=context.error)

def main():
    """Start the bot."""
    print("Starting Forex Teaching Bot...")
    
    if not TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN environment variable is not set!")
        return

    # Build application with higher connection timeouts for hosting stability
    application = (
        Application.builder()
        .token(TOKEN)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .write_timeout(30.0)
        .build()
    )

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Add global error logging
    application.add_error_handler(error_handler)

    print("Bot is polling for updates...")
    application.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
