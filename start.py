import subprocess

def run_scripts():
    scripts = ["command1.py", "gpt.py", "roll.py", "uno.py", "image.py", "blackjack.py", "wheel.py", "connect4.py", "search.py", "roles.py", "shop.py", "create_role.py", "confess.py", "group_name.py", "group_photo.py", "reels.py", "delete_last.py", "triggers.py"]
    processes = []

    for script in scripts:
        process = subprocess.Popen(["python", script])
        processes.append(process)

    try:
        for process in processes:
            process.wait()
    except KeyboardInterrupt:
        print("Stopping all bots...")
        for process in processes:
            process.terminate()
        print("All bots stopped.")

if __name__ == "__main__":
    run_scripts()

