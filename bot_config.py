"""
Bot Configuration
Contains all bot settings and constants
"""

import os

class BotConfig:
    """Bot configuration class"""
    
    def __init__(self):
        # Bot credentials
        self.BOT_TOKEN = os.getenv("BOT_TOKEN", "8390072196:AAHHtb1AxJvrxOQ4FR2MePfHTAJ5r1QeKzQ")
        self.GROUP_ID = os.getenv("GROUP_ID", "-1002845367780")
        self.BOT_USERNAME = os.getenv("BOT_USERNAME", "@Malena122")
        
        # OCR settings
        self.TESSERACT_CONFIG = '--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz./$:%-'
        
        # Signal parsing keywords
        self.SIGNAL_KEYWORDS = {
            'symbol': ['symbol', 'coin', 'pair'],
            'signal_type': ['long', 'short', 'buy', 'sell'],
            'entries': ['entry', 'entries', 'enter', 'buy zone'],
            'targets': ['target', 'targets', 'tp', 'take profit'],
            'stoploss': ['stop loss', 'stoploss', 'sl', 'stop']
        }
        
        # Message templates
        self.LONG_TEMPLATE = """${symbol}
🟢LONG X5
📊VOL 0.5%
🎯Entry : {entries}
⛔SL : {stoploss}
🏆TP : {targets}"""

        self.SHORT_TEMPLATE = """${symbol}
🔴SHORT X5
📊VOL 0.5%
🎯Entry : {entries}
⛔SL : {stoploss}
🏆TP : {targets}"""
