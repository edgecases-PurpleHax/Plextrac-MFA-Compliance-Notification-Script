"""
Setup script to create a virtual environment, install dependencies, and set up a scheduled task
on Linux/Mac (using cron) or Windows (using Task Scheduler) to run the main script periodically.
"""

import os
import platform
import subprocess


def setup_environment():
    """
    Set up the virtual environment, install dependencies, and create a scheduled task.

    Detects the platform (Linux/Mac or Windows) and performs the necessary steps:
    - Create and activate a virtual environment.
    - Install dependencies from requirements.txt.
    - Set up a scheduled task to run the main script periodically.

    Raises:
        subprocess.CalledProcessError: If any command fails.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    venv_path = os.path.join(base_dir, 'venv')
    requirements_path = os.path.join(base_dir, 'requirements.txt')
    main_script_path = os.path.join(base_dir, 'main.py')
    current_os = platform.system()

    # Create virtual environment
    subprocess.check_call(['python', '-m', 'venv', venv_path])

    if current_os == 'Windows':
        activate_script = os.path.join(venv_path, 'Scripts', 'activate')
    else:
        activate_script = os.path.join(venv_path, 'bin', 'activate')

    # Install dependencies
    subprocess.check_call(f'{activate_script} && pip install -r {requirements_path}', shell=True)

    # Schedule the script to run periodically
    if current_os == 'Windows':
        schedule_task_windows(main_script_path, activate_script)
    else:
        schedule_task_unix(main_script_path, activate_script)


def schedule_task_windows(script_path, activate_script):
    """
    Schedule a task in Windows Task Scheduler to run the main script periodically.

    Args:
        script_path (str): The path to the main script.
        activate_script (str): The path to the virtual environment activation script.
    """
    task_name = "RunMainScript"
    action = (
        f'SchTasks /Create /SC WEEKLY /D FRI /TN "{task_name}" /TR "'
        f'{activate_script} && python {script_path}" /ST 08:00'
    )
    subprocess.check_call(action, shell=True)


def schedule_task_unix(script_path, activate_script):
    """
    Schedule a cron job to run the main script periodically on Linux/Mac.

    Args:
        script_path (str): The path to the main script.
        activate_script (str): The path to the virtual environment activation script.
    """
    cron_job = f'0 8 * * 5 source {activate_script} && python {script_path}'
    subprocess.check_call(f'(crontab -l; echo "{cron_job}") | crontab -', shell=True)


if __name__ == "__main__":
    setup_environment()
