"""
Minimal standalone critic agent process for Docker compose deployments.
It currently keeps the service alive and ready for future queue-based work.
"""
import time
from agentic_os.utils.logger import logger


def run_critic_loop() -> None:
    logger.info("Critic Agent: started and waiting for work.")
    while True:
        # Keep container healthy until task queue integration is added.
        time.sleep(30)


if __name__ == "__main__":
    run_critic_loop()
