#!/usr/bin/env python3
"""
Telegram Trading Signal Bot - Main Entry Point
Scans trading signal images, extracts data, and formats messages with confirmation workflow
"""

import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from bot_config import BotConfig
from ocr_processor import OCRProcessor
from signal_parser import SignalParser
from message_formatter import MessageFormatter

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TradingSignalBot:
    def __init__(self):
        self.config = BotConfig()
        self.ocr_processor = OCRProcessor()
        self.signal_parser = SignalParser()
        self.message_formatter = MessageFormatter()
        self.pending_messages = {}  # Store pending messages for confirmation
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        welcome_message = (
            "🤖 *Bot Trading Signal Scanner* đã kết nối thành công!\n\n"
            "📸 Gửi ảnh trading signal để bot phân tích\n"
            "🔍 Bot sẽ tự động nhận diện LONG/SHORT và extract thông tin\n"
            "✅ Xác nhận tin nhắn trước khi đăng vào nhóm\n\n"
            "Sẵn sàng phục vụ!"
        )
        await update.message.reply_text(welcome_message, parse_mode='Markdown')

    async def handle_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle received images and process OCR"""
        try:
            # Send processing message
            processing_msg = await update.message.reply_text("🔍 Đang phân tích ảnh...")
            
            # Get the largest photo size
            photo = update.message.photo[-1]
            
            # Download the image
            file = await context.bot.get_file(photo.file_id)
            image_path = f"temp_image_{update.message.chat_id}.jpg"
            await file.download_to_drive(image_path)
            
            # Process OCR
            extracted_text = self.ocr_processor.extract_text_from_image(image_path)
            
            # Clean up temp file
            if os.path.exists(image_path):
                os.remove(image_path)
            
            if not extracted_text:
                await processing_msg.edit_text("❌ Không thể đọc được nội dung từ ảnh. Vui lòng thử lại với ảnh rõ nét hơn.")
                return
            
            # Parse signal data
            signal_data = self.signal_parser.parse_signal(extracted_text)
            
            if not signal_data:
                await processing_msg.edit_text("❌ Không tìm thấy signal hợp lệ trong ảnh. Vui lòng kiểm tra lại.")
                return
            
            # Format message
            formatted_message = self.message_formatter.format_signal(signal_data)
            
            # Create confirmation keyboard
            keyboard = [
                [
                    InlineKeyboardButton("✅ YES", callback_data=f"confirm_{update.message.chat_id}"),
                    InlineKeyboardButton("❌ NO", callback_data=f"reject_{update.message.chat_id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Store pending message
            self.pending_messages[update.message.chat_id] = {
                'message': formatted_message,
                'signal_data': signal_data,
                'original_text': extracted_text
            }
            
            # Send formatted message with confirmation
            confirmation_text = f"{formatted_message}\n\n📋 Bạn có xác nhận không? Xin vui lòng chọn:"
            await processing_msg.edit_text(confirmation_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            await update.message.reply_text("❌ Lỗi khi xử lý ảnh. Vui lòng thử lại.")

    async def handle_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle YES/NO confirmation callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        chat_id = int(data.split('_')[1])
        action = data.split('_')[0]
        
        if chat_id not in self.pending_messages:
            await query.edit_message_text("❌ Session hết hạn. Vui lòng gửi lại ảnh.")
            return
        
        pending_data = self.pending_messages[chat_id]
        
        if action == "confirm":
            try:
                # Send to target group
                await context.bot.send_message(
                    chat_id=self.config.GROUP_ID,
                    text=pending_data['message'],
                    parse_mode='Markdown'
                )
                
                await query.edit_message_text("✅ Đã đăng signal vào nhóm thành công!")
                
                # Clean up
                del self.pending_messages[chat_id]
                
            except Exception as e:
                logger.error(f"Error posting to group: {e}")
                await query.edit_message_text("❌ Lỗi khi đăng vào nhóm. Vui lòng thử lại.")
                
        elif action == "reject":
            # Regenerate message - for now just ask to send image again
            await query.edit_message_text(
                "❌ Signal bị từ chối. Bot sẽ làm lại bài viết.\n"
                "📸 Vui lòng gửi lại ảnh để phân tích lại."
            )
            
            # Clean up
            del self.pending_messages[chat_id]

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors"""
        logger.error(f"Exception while handling an update: {context.error}")

def main():
    """Main function to run the bot"""
    # Get bot token from environment
    bot_token = os.getenv("BOT_TOKEN", "8390072196:AAHHtb1AxJvrxOQ4FR2MePfHTAJ5r1QeKzQ")
    
    if not bot_token:
        raise ValueError("BOT_TOKEN environment variable is required")
    
    # Create bot instance
    bot = TradingSignalBot()
    
    # Create application
    application = Application.builder().token(bot_token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(MessageHandler(filters.PHOTO, bot.handle_image))
    application.add_handler(CallbackQueryHandler(bot.handle_confirmation))
    application.add_error_handler(bot.error_handler)
    
    # Start the bot
    logger.info("Starting Trading Signal Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
