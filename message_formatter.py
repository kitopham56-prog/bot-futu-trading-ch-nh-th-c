"""
Message Formatter Module
Formats parsed signal data into standardized telegram messages
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)

class MessageFormatter:
    """Formats trading signals into standardized messages"""
    
    def __init__(self):
        # Message templates
        self.LONG_TEMPLATE = """{symbol}
🟢LONG X5
📊VOL 0.5%
🎯Entry : {entries}
⛔SL : {stoploss}
🏆TP : {targets}"""

        self.SHORT_TEMPLATE = """{symbol}
🔴SHORT X5
📊VOL 0.5%
🎯Entry : {entries}
⛔SL : {stoploss}
🏆TP : {targets}"""
    
    def format_signal(self, signal_data: Dict) -> str:
        """
        Format signal data into standardized message
        """
        try:
            # Validate signal data
            if not self._validate_signal_data(signal_data):
                logger.error("Invalid signal data provided")
                return ""
            
            # Get template based on signal type
            if signal_data['signal_type'].upper() == 'LONG':
                template = self.LONG_TEMPLATE
            elif signal_data['signal_type'].upper() == 'SHORT':
                template = self.SHORT_TEMPLATE
            else:
                logger.error(f"Unknown signal type: {signal_data['signal_type']}")
                return ""
            
            # Format symbol with $ prefix
            symbol = signal_data['symbol'].upper()
            if not symbol.startswith('$'):
                symbol = f"${symbol}"
            
            # Format the message
            formatted_message = template.format(
                symbol=symbol,
                entries=signal_data['entries'],
                stoploss=signal_data['stoploss'],
                targets=signal_data['targets']
            )
            
            logger.info(f"Formatted message: {formatted_message}")
            return formatted_message
            
        except Exception as e:
            logger.error(f"Error formatting signal: {e}")
            return ""
    
    def _validate_signal_data(self, signal_data: Dict) -> bool:
        """Validate signal data before formatting"""
        required_fields = ['symbol', 'signal_type', 'entries', 'targets', 'stoploss']
        
        for field in required_fields:
            if field not in signal_data:
                logger.error(f"Missing required field: {field}")
                return False
            
            if not signal_data[field]:
                logger.error(f"Empty value for field: {field}")
                return False
        
        # Validate signal type
        if signal_data['signal_type'].upper() not in ['LONG', 'SHORT']:
            logger.error(f"Invalid signal type: {signal_data['signal_type']}")
            return False
        
        return True
    
    def format_error_message(self, error_type: str, details: str = "") -> str:
        """Format error messages for user feedback"""
        error_messages = {
            'no_signal': "❌ Không tìm thấy signal trong ảnh. Vui lòng kiểm tra lại.",
            'invalid_image': "❌ Không thể đọc được ảnh. Vui lòng gửi ảnh rõ nét hơn.",
            'parsing_error': "❌ Lỗi phân tích signal. Vui lòng kiểm tra format ảnh.",
            'missing_data': "❌ Thiếu thông tin signal. Vui lòng đảm bảo ảnh có đầy đủ: Symbol, Signal Type, Entry, Target, Stop Loss."
        }
        
        message = error_messages.get(error_type, "❌ Đã xảy ra lỗi không xác định.")
        
        if details:
            message += f"\nChi tiết: {details}"
        
        return message
    
    def format_confirmation_message(self, formatted_signal: str) -> str:
        """Format confirmation message with signal preview"""
        return f"{formatted_signal}\n\n📋 Bạn có xác nhận không? Xin vui lòng chọn:"
    
    def format_success_message(self) -> str:
        """Format success message after posting to group"""
        return "✅ Đã đăng signal vào nhóm thành công!"
    
    def format_rejection_message(self) -> str:
        """Format message when user rejects the signal"""
        return (
            "❌ Signal bị từ chối. Bot sẽ làm lại bài viết.\n"
            "📸 Vui lòng gửi lại ảnh để phân tích lại."
        )
