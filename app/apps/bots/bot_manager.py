import os
import subprocess
import threading

# Для простоты: bot_id -> process
bot_processes = {}

def start_bot(bot_id):
    if bot_id in bot_processes:
        return False  # Уже запущен

    my_env = os.environ.copy()
    my_env["BOT_ID"] = str(bot_id)

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    proc = subprocess.Popen(["python", "telegram_client/app.py"], cwd=base_dir, env=my_env)
    bot_processes[bot_id] = proc
    return True

def stop_bot(bot_id):
    proc = bot_processes.get(bot_id)
    if proc:
        proc.terminate()
        proc.wait()
        del bot_processes[bot_id]
        return True
    return False

def is_bot_running(bot_id):
    proc = bot_processes.get(bot_id)
    return proc is not None and proc.poll() is None
