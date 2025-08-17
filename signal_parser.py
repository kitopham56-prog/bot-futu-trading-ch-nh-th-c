"""
Signal Parser Module
Parses extracted OCR text to identify trading signal components
"""

import re
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class SignalParser:
    """Parses trading signal text to extract structured data"""
    
    def __init__(self):
        # Define patterns for signal components
        self.patterns = {
            'symbol': [
                r'symbol[:\s]*([A-Z]{3,10})',
                r'coin[:\s]*([A-Z]{3,10})',
                r'pair[:\s]*([A-Z]{3,10})',
                r'([A-Z]{3,10})USDT',
                r'([A-Z]{3,10})/USDT',
                r'symbol[:\s]*(\w+)',
                r'([A-Z]{3,10})\s'
            ],
            'signal_type': [
                r'(LONG|SHORT|BUY|SELL)',
                r'signal[:\s]*(LONG|SHORT|BUY|SELL)',
                r'type[:\s]*(LONG|SHORT|BUY|SELL)'
            ],
            'entries': [
                r'entries[:\s]*\$?([0-9.,\s-]+)',
                r'entry[:\s]*\$?([0-9.,\s-]+)',
                r'entr(?:y|ies)[:\s]*\$?([0-9.,\s-]+)',
                r'buy\s*zone[:\s]*\$?([0-9.,\s-]+)',
                r'enter[:\s]*\$?([0-9.,\s-]+)',
                r'\$([0-9]+\.?[0-9]*)\s*-\s*\$([0-9]+\.?[0-9]*)',
                r'([0-9]+\.?[0-9]*)\s*-\s*([0-9]+\.?[0-9]*)'
            ],
            'targets': [
                r'targets[:\s]*\$?([0-9.,\s-]+)',
                r'target[:\s]*\$?([0-9.,\s-]+)',
                r'tp[:\s]*\$?([0-9.,\s-]+)',
                r'take\s*profit[:\s]*\$?([0-9.,\s-]+)',
                r'\$([0-9]+\.?[0-9]*(?:\s*-\s*\$[0-9]+\.?[0-9]*)*)'
            ],
            'stoploss': [
                r'stoploss[:\s]*\$?([0-9.,]+)',
                r'stop\s*loss[:\s]*\$?([0-9.,]+)',
                r'sl[:\s]*\$?([0-9.,]+)'
            ]
        }
    
    def parse_signal(self, text: str) -> Optional[Dict]:
        """
        Parse signal text and extract structured data
        """
        try:
            logger.info(f"Original text: {text}")
            text_upper = text.upper()
            signal_data = {}
            
            # Try to extract data using improved direct parsing
            parsed_data = self._parse_structured_text(text)
            if parsed_data:
                logger.info(f"Parsed signal data: {parsed_data}")
                return parsed_data
            
            # Fallback to pattern matching
            # Extract symbol
            symbol = self._extract_symbol(text_upper)
            if not symbol:
                logger.warning("No symbol found in text")
                return None
            
            signal_data['symbol'] = symbol
            
            # Extract signal type
            signal_type = self._extract_signal_type(text_upper)
            if not signal_type:
                logger.warning("No signal type found in text")
                return None
            
            signal_data['signal_type'] = signal_type
            
            # Extract entries
            entries = self._extract_entries(text_upper)
            if not entries:
                logger.warning("No entries found in text")
                return None
            
            signal_data['entries'] = entries
            
            # Extract targets
            targets = self._extract_targets(text_upper)
            if not targets:
                logger.warning("No targets found in text")
                return None
            
            signal_data['targets'] = targets
            
            # Extract stop loss
            stoploss = self._extract_stoploss(text_upper)
            if not stoploss:
                logger.warning("No stop loss found in text")
                return None
            
            signal_data['stoploss'] = stoploss
            
            logger.info(f"Parsed signal data: {signal_data}")
            return signal_data
            
        except Exception as e:
            logger.error(f"Error parsing signal: {e}")
            return None
    
    def _parse_structured_text(self, text: str) -> Optional[Dict]:
        """
        Parse structured text from OCR with line-by-line analysis
        """
        try:
            lines = text.split('\n')
            signal_data = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Symbol extraction
                if 'symbol:' in line.lower():
                    symbol_match = re.search(r'symbol[:\s]*(\w+)', line, re.IGNORECASE)
                    if symbol_match:
                        symbol = symbol_match.group(1).upper()
                        # Clean common OCR errors
                        if 'SOLUSOT' in symbol or 'SOLUSOТ' in symbol:
                            symbol = 'SOLUSDT'
                        signal_data['symbol'] = symbol
                
                # Signal type extraction
                if 'signaltype:' in line.lower() or 'signal type:' in line.lower():
                    signal_match = re.search(r'(LONG|SHORT)', line, re.IGNORECASE)
                    if signal_match:
                        signal_data['signal_type'] = signal_match.group(1).upper()
                
                # Entries extraction
                if 'entries:' in line.lower():
                    entries_match = re.search(r'entries[:\s]*(.+)', line, re.IGNORECASE)
                    if entries_match:
                        entries = entries_match.group(1).strip()
                        signal_data['entries'] = entries
                
                # Stop loss extraction
                if 'stoploss:' in line.lower():
                    sl_match = re.search(r'stoploss[:\s]*(.+)', line, re.IGNORECASE)
                    if sl_match:
                        stoploss = sl_match.group(1).strip()
                        signal_data['stoploss'] = stoploss
                
                # Targets extraction (multi-line) - FIXED VERSION
                if 'targets:' in line.lower():
                    # Find the line index and get following lines
                    line_index = lines.index(line)
                    targets_text = []
                    
                    # Check if targets are on the same line
                    targets_match = re.search(r'targets[:\s]*(.+)', line, re.IGNORECASE)
                    if targets_match and targets_match.group(1).strip() and targets_match.group(1).strip() != ':':
                        targets_text.append(targets_match.group(1).strip())
                    else:
                        # Get targets from next lines (look for multiple lines with $ signs)
                        for i in range(line_index + 1, min(line_index + 5, len(lines))):
                            if i < len(lines):
                                next_line = lines[i].strip()
                                if next_line and ('$' in next_line or re.search(r'\d+\.\d+', next_line)):
                                    targets_text.append(next_line)
                                    break  # Take the first line with targets data
                    
                    if targets_text:
                        signal_data['targets'] = ' '.join(targets_text)
            
            # Validate we have the required fields
            required_fields = ['symbol', 'signal_type', 'entries', 'targets', 'stoploss']
            if all(field in signal_data for field in required_fields):
                return signal_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing structured text: {e}")
            return None
    
    def _extract_symbol(self, text: str) -> Optional[str]:
        """Extract trading symbol/coin"""
        for pattern in self.patterns['symbol']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                symbol = match.group(1).upper()
                # Validate symbol (3-10 characters, letters only)
                if 3 <= len(symbol) <= 10 and symbol.isalpha():
                    return symbol
        return None
    
    def _extract_signal_type(self, text: str) -> Optional[str]:
        """Extract signal type (LONG/SHORT)"""
        for pattern in self.patterns['signal_type']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                signal_type = match.group(1).upper()
                # Normalize signal type
                if signal_type in ['BUY']:
                    return 'LONG'
                elif signal_type in ['SELL']:
                    return 'SHORT'
                elif signal_type in ['LONG', 'SHORT']:
                    return signal_type
        return None
    
    def _extract_entries(self, text: str) -> Optional[str]:
        """Extract entry prices"""
        for pattern in self.patterns['entries']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                entries = match.group(1).strip()
                # Clean and format entries
                entries = self._clean_price_data(entries)
                if entries:
                    return entries
        return None
    
    def _extract_targets(self, text: str) -> Optional[str]:
        """Extract target prices - IMPROVED VERSION"""
        # First try pattern matching
        for pattern in self.patterns['targets']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                targets = match.group(1).strip()
                # Clean and format targets
                targets = self._clean_price_data(targets)
                if targets:
                    return targets
        
        # Fallback: look for lines after "Targets:" containing multiple $ values
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if 'targets:' in line.lower():
                # Check next few lines for target data
                for j in range(i + 1, min(i + 3, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and ('$' in next_line or re.search(r'\d+\.\d+', next_line)):
                        # Found targets data
                        cleaned_targets = self._clean_price_data(next_line)
                        if cleaned_targets:
                            return cleaned_targets
        
        return None
    
    def _extract_stoploss(self, text: str) -> Optional[str]:
        """Extract stop loss price"""
        for pattern in self.patterns['stoploss']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                stoploss = match.group(1).strip()
                # Clean and format stop loss
                stoploss = self._clean_price_data(stoploss)
                if stoploss:
                    return stoploss
        return None
    
    def _clean_price_data(self, price_text: str) -> str:
        """Clean and format price data"""
        if not price_text:
            return ""
        
        # Remove extra spaces and clean
        price_text = re.sub(r'\s+', ' ', price_text.strip())
        
        # Handle ranges and multiple values
        # Keep original format but clean it
        cleaned = price_text.replace('  ', ' ').replace(' -', '-').replace('- ', '-')
        
        # Validate that we have at least one number
        if re.search(r'\d+\.?\d*', cleaned):
            return cleaned
        
        return ""
    
    def validate_signal_data(self, signal_data: Dict) -> bool:
        """Validate that signal data is complete and valid"""
        required_fields = ['symbol', 'signal_type', 'entries', 'targets', 'stoploss']
        
        for field in required_fields:
            if field not in signal_data or not signal_data[field]:
                return False
        
        # Additional validation
        if signal_data['signal_type'] not in ['LONG', 'SHORT']:
            return False
        
        return True
