#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CustomerDaisy - DaisySMS & Customer Creation System
==================================================
"""

__version__ = "1.0.0"
__author__ = "Claude AI"
__description__ = "DaisySMS & Customer Creation System with Mail.tm Integration"

from .daisy_sms import DaisySMSManager
from .mail_tm import MailTmManager
from .customer_db import CustomerDatabase
from .config_manager import ConfigManager
from .sms_monitor import SMSMonitor

__all__ = [
    'DaisySMSManager',
    'MailTmManager', 
    'CustomerDatabase',
    'ConfigManager',
    'SMSMonitor'
]
