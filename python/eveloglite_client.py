#!/usr/bin/env python3
"""
Modernized EveLogLite Python client for Python 3
Based on CCP Games' original EveLogLite client
"""

import ctypes
import logging
import os
import socket
import sys
import time
from typing import Optional, Any

VERSION = 2
PORT = 0xcc9


class _ConnectionMessage(ctypes.Structure):
    _fields_ = [('version', ctypes.c_uint32), ('pid', ctypes.c_int64), ('machine_name', ctypes.c_char * 32),
                ('executable_path', ctypes.c_char * 260)]


class _TextMessage(ctypes.Structure):
    _fields_ = [('timestamp', ctypes.c_uint64), ('severity', ctypes.c_uint32), ('module', ctypes.c_char * 32),
                ('channel', ctypes.c_char * 32), ('message', ctypes.c_char * 256)]


class _TextOrConnection(ctypes.Union):
    _fields_ = [('connection', _ConnectionMessage), ('text', _TextMessage)]


class _Message(ctypes.Structure):
    _fields_ = [('type', ctypes.c_uint32), ('body', _TextOrConnection)]


class _MessageType(object):
    CONNECTION_MESSAGE = 0
    SIMPLE_MESSAGE = 1
    LARGE_MESSAGE = 2
    CONTINUATION_MESSAGE = 3
    CONTINUATION_END_MESSAGE = 4


class Severity(object):
    INFO = 0
    NOTICE = 1
    WARNING = 2
    ERROR = 3


class LogLiteClient(object):
    def __init__(self, server: str = '127.0.0.1', pid: Optional[int] = None, 
                 machine_name: Optional[str] = None, executable_path: Optional[str] = None) -> None:
        if pid is None:
            pid = os.getpid()
        if machine_name is None:
            machine_name = socket.gethostname()
        if executable_path is None:
            executable_path = sys.argv[0]

        try:
            self.socket = socket.create_connection((server, PORT))
            self.connected = True
        except (socket.error, ConnectionRefusedError):
            print(f"Warning: Could not connect to LogLite server at {server}:{PORT}")
            self.connected = False
            return

        msg = _Message()
        msg.type = _MessageType.CONNECTION_MESSAGE
        msg.body.connection.version = VERSION
        msg.body.connection.pid = pid
        msg.body.connection.machine_name = machine_name.encode('utf-8')[:31]
        msg.body.connection.executable_path = executable_path.encode('utf-8')[:259]
        
        # Python 3 compatible - use bytes() instead of buffer()
        self.socket.sendall(bytes(msg))

    def log(self, severity: Any, message: str, timestamp: Optional[Any] = None, 
            module: str = '', channel: str = '') -> None:
        if not self.connected:
            return
            
        msg = _Message()
        msg.body.text.timestamp = timestamp or int(time.time() * 1000)
        msg.body.text.severity = severity
        msg.body.text.module = module.encode('utf-8')[:31]
        msg.body.text.channel = channel.encode('utf-8')[:31]
        
        if len(message) < 255:
            msg.type = _MessageType.SIMPLE_MESSAGE
            msg.body.text.message = message.encode('utf-8')[:255]
            self.socket.sendall(bytes(msg))
        else:
            offset = 0
            msg.type = _MessageType.LARGE_MESSAGE
            while offset < len(message):
                chunk = message[offset:offset + 255]
                msg.body.text.message = chunk.encode('utf-8')[:255]
                self.socket.sendall(bytes(msg))
                offset += 255
                if offset + 255 >= len(message):
                    msg.type = _MessageType.CONTINUATION_END_MESSAGE
                else:
                    msg.type = _MessageType.CONTINUATION_MESSAGE

    def close(self):
        if self.connected:
            self.socket.close()
            self.connected = False


LEVEL_MAP = {
    logging.CRITICAL:   Severity.ERROR,
    logging.ERROR:      Severity.ERROR,
    logging.WARNING:    Severity.WARNING,
    logging.INFO:       Severity.NOTICE,
    logging.DEBUG:      Severity.INFO,
    logging.NOTSET:     Severity.INFO}


class LogLiteHandler(logging.Handler):
    def __init__(self, client: Any) -> None:
        super(LogLiteHandler, self).__init__()
        self.client = client

    def emit(self, record: logging.LogRecord) -> None:
        try:
            if '.' in record.name:
                channel, module = record.name.split('.', 1)
            else:
                channel, module = record.name, 'General'
            self.client.log(LEVEL_MAP.get(record.levelno, Severity.INFO), self.format(record), module=module,
                            channel=channel)
        except Exception:
            self.handleError(record)


# Convenience functions for direct use
def create_client(server: str = '127.0.0.1') -> LogLiteClient:
    """Create a LogLite client connection."""
    return LogLiteClient(server)

def log_crash(client: Any, crash_type: str, process_name: str, details: str, timestamp: Optional[Any] = None) -> None:
    """Log a crash event to LogLite."""
    if client.connected:
        message = f"CRASH: {crash_type} - Process: {process_name} - Details: {details}"
        client.log(Severity.ERROR, message, timestamp, module='CrashMonitor', channel='Crashes')
