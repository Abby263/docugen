#!/usr/bin/env python
"""Server Manager - API and Worker Process Manager"""

import sys
import time
import signal
import subprocess
from pathlib import Path
from loguru import logger


class ServerManager:
    """Server Manager for API and Worker processes"""

    def __init__(self):
        self.api_process = None
        self.worker_process = None
        self.is_running = False

    def start_api(self):
        """API"""
        logger.info("API...")

        self.api_process = subprocess.Popen(
            [sys.executable, "run_api.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        # API
        time.sleep(2)

        if self.api_process.poll() is None:
            logger.success(" API (PID: {})", self.api_process.pid)
            return True
        else:
            logger.error(" API")
            return False

    def start_worker(self):
        """Start the background worker process."""
        logger.info("...")

        self.worker_process = subprocess.Popen(
            [sys.executable, "start_worker.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        # Worker
        time.sleep(2)

        if self.worker_process.poll() is None:
            logger.success("  (PID: {})", self.worker_process.pid)
            return True
        else:
            logger.error(" ")
            return False

    def start_all(self):
        """Start both API and worker processes."""
        logger.info("=" * 60)
        logger.info("Server Manager Starting")
        logger.info("=" * 60)
        logger.info("")

        # 
        Path("tasks").mkdir(exist_ok=True)
        Path("storage").mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)

        # API
        if not self.start_api():
            logger.error("API")
            return False

        time.sleep(1)

        # 
        if not self.start_worker():
            logger.error("API")
            self.stop_all()
            return False

        self.is_running = True

        logger.info("")
        logger.info("=" * 60)
        logger.success(" ")
        logger.info("=" * 60)
        logger.info("")
        logger.info(" :")
        logger.info("   API:    http://localhost:8000")
        logger.info("   API:      http://localhost:8000/docs")
        logger.info("   :     http://localhost:8000/health")
        logger.info("")
        logger.info(" :")
        logger.info("    Ctrl+C ")
        logger.info("")
        logger.info(" :")
        logger.info("   - API: ")
        logger.info("   - API: python scripts/test_api.py")
        logger.info("   - : python examples/async_api_client.py")
        logger.info("")
        logger.info("  Ctrl+C ...")
        logger.info("")

        return True

    def stop_all(self):
        """Stop both API and worker processes gracefully."""
        logger.info("")
        logger.info("...")

        # 
        if self.worker_process and self.worker_process.poll() is None:
            logger.info("...")
            self.worker_process.terminate()
            try:
                self.worker_process.wait(timeout=5)
                logger.success(" ")
            except subprocess.TimeoutExpired:
                logger.warning("...")
                self.worker_process.kill()
                self.worker_process.wait()

        # API
        if self.api_process and self.api_process.poll() is None:
            logger.info("API...")
            self.api_process.terminate()
            try:
                self.api_process.wait(timeout=5)
                logger.success(" API")
            except subprocess.TimeoutExpired:
                logger.warning("API...")
                self.api_process.kill()
                self.api_process.wait()

        self.is_running = False
        logger.success(" ")

    def monitor_processes(self):
        """Monitor API and worker processes, restart if they crash."""
        while self.is_running:
            try:
                # API
                if self.api_process and self.api_process.poll() is not None:
                    logger.error("API: {}", self.api_process.returncode)
                    self.is_running = False
                    break

                # Worker
                if self.worker_process and self.worker_process.poll() is not None:
                    logger.error(": {}", self.worker_process.returncode)
                    self.is_running = False
                    break

                time.sleep(1)

            except KeyboardInterrupt:
                logger.info("")
                break

    def run(self):
        """Main run loop: start services, monitor, and handle shutdown."""
        # 
        def signal_handler(signum, frame):
            logger.info(" {}, ...", signum)
            self.stop_all()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # 
        if not self.start_all():
            sys.exit(1)

        try:
            # 
            self.monitor_processes()
        finally:
            # 
            self.stop_all()


def main():
    """Main entry point for starting the server."""
    server = ServerManager()
    server.run()


if __name__ == "__main__":
    main()
