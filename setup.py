import os
import platform
import subprocess


def setup_virtualenv_and_task():
    """
    Sets up a virtual environment, installs dependencies, and schedules a task to run a script.

    This function detects the current operating system and performs the following actions:
    - Creates a virtual environment ('venv') in the current directory if it doesn't exist.
    - Activates the virtual environment, installs dependencies from 'requirements.txt', and deactivates it.
    - For Windows, schedules a task using 'schtasks' to run the script ('script.py') every Friday at 8 AM.
    - For Unix-like systems (Linux or MacOS), sets up a cron job to run the script every Friday at 8 AM.

    Raises:
        subprocess.CalledProcessError: If any subprocess command returns a non-zero exit status.

    Notes:
        - Replace 'script.py' and 'requirements.txt' with your actual script and dependencies file names.
        - Ensure that 'python' or 'python3' is available in the system PATH for creating the virtual environment.
    """
    # Determine paths and commands based on OS
    current_dir = os.getcwd()
    venv_dir = os.path.join(current_dir, 'venv')
    requirements_file = os.path.join(current_dir, 'requirements.txt')
    script_file = os.path.join(current_dir, 'script.py')

    if platform.system() == 'Windows':
        # Windows specific commands
        venv_python = os.path.join(venv_dir, 'Scripts', 'python.exe')
        activate_cmd = os.path.join(venv_dir, 'Scripts', 'activate.bat')

        # Create virtual environment if it doesn't exist
        if not os.path.exists(venv_dir):
            subprocess.run(['python', '-m', 'venv', venv_dir], check=True)

        # Activate virtual environment and install dependencies
        subprocess.run([activate_cmd], shell=True, check=True)
        subprocess.run([venv_python, '-m', 'pip', 'install', '-r', requirements_file], check=True)
        subprocess.run(['deactivate'], shell=True, check=True)

        # Schedule the task to run every Friday at 8 AM (Windows)
        task_command = f'{venv_python} {script_file}'
        task_name = "MyPythonScript"
        task_trigger = 'weekly'
        task_day = 'FRI'
        task_time = '08:00:00'
        create_task_cmd = f'schtasks /create /tn "{task_name}" /tr "{task_command}" /sc {task_trigger} /d {task_day} /st {task_time} /ru INTERACTIVE'
        subprocess.run(create_task_cmd, shell=True, check=True)
        print(f"Scheduled task '{task_name}' created successfully.")

    elif platform.system() in ['Linux', 'Darwin']:
        # Linux/Mac specific commands
        venv_python = os.path.join(venv_dir, 'bin', 'python')
        activate_cmd = 'source ' + os.path.join(venv_dir, 'bin', 'activate')

        # Create virtual environment if it doesn't exist
        if not os.path.exists(venv_dir):
            subprocess.run(['python3', '-m', 'venv', venv_dir], check=True)

        # Activate virtual environment and install dependencies
        subprocess.run([activate_cmd], shell=True, check=True)
        subprocess.run([venv_python, '-m', 'pip', 'install', '-r', requirements_file], check=True)
        subprocess.run(['deactivate'], shell=True, check=True)

        # Setup cron job to run the script every Friday at 8 AM (Linux/Mac)
        cron_command = f'(crontab -l ; echo "0 8 * * 5 {venv_python} {script_file}") | sort - | uniq - | crontab -'
        subprocess.run(cron_command, shell=True, check=True)
        print("Cron job scheduled successfully.")

    else:
        print("Unsupported operating system. Please use Linux, MacOS, or Windows.")


if __name__ == "__main__":
    setup_virtualenv_and_task()
