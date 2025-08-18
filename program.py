import subprocess
import threading
import time
import re
import signal
import sys

# Global lists to store extracted numbers and steps
saving_numbers = []
saving_steps = []


# Function to read output from a process
def read_output(pipe, process_name):
    global saving_numbers, saving_steps
    for line in iter(pipe.readline, b''):
        decoded_line = line.decode().strip()
        
        # Extract numbers inside angle brackets
        match_numbers = re.search(r'<(\d+)>', decoded_line)
        if match_numbers:
            saving_numbers.append(int(match_numbers.group(1)))

        # Extract numbers inside square brackets
        
        match_steps = re.search(r'\[(\d+)\]', decoded_line)
        if match_steps:
            saving_steps.append(int(match_steps.group(1)))

        # Print the process output
        print(f"{process_name} output: {decoded_line}")
    pipe.close()

# Function to terminate all running processes
def terminate_processes(processes):
    for proc in processes:
        if proc.poll() is None:  # Check if the process is running
            proc.terminate()
            try:
                proc.wait(timeout=5)  # Wait for graceful termination
            except subprocess.TimeoutExpired:
                print(f"Force killing process {proc.pid}")
                proc.kill()

# Signal handler for Ctrl+C
def signal_handler(sig, frame):
    print("\nCtrl+C detected! Terminating all processes...")
    terminate_processes(processes)
    print("Processes terminated. Exiting...")

    
    
    print("Trials:", len(saving_numbers))
    print("Average numbers:", sum(saving_numbers) / len(saving_numbers), saving_numbers)
    print("Average steps:", sum(saving_steps) / len(saving_steps), saving_steps)
    print("Finished runs: ", saving_steps.count(3000))
    
    sys.exit(0)

# Main function to run the programs
def run_programs():
    global processes
    processes = []  # List to keep track of subprocesses

    try:
        while True:
            # Start the server process
            server_process = subprocess.Popen(
                ["python3", "server.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            print(f"Server started with PID: {server_process.pid}")
            threading.Thread(target=read_output, args=(server_process.stdout, 'Server')).start()
            threading.Thread(target=read_output, args=(server_process.stderr, 'Server Error')).start()
            processes.append(server_process)

            # Start the viewer process
            viewer_process = subprocess.Popen(
                ["python3", "viewer.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            print(f"Viewer started with PID: {viewer_process.pid}")
            threading.Thread(target=read_output, args=(viewer_process.stdout, 'Viewer')).start()
            threading.Thread(target=read_output, args=(viewer_process.stderr, 'Viewer Error')).start()
            processes.append(viewer_process)

            # Start the student process in a loop
            while True:
                print("Starting student process...")
                student_process = subprocess.Popen(
                    ["python3", "student.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                print(f"Student started with PID: {student_process.pid}")
                processes.append(student_process)

                # Start threads to read student output
                threading.Thread(target=read_output, args=(student_process.stdout, 'Student')).start()
                threading.Thread(target=read_output, args=(student_process.stderr, 'Student Error')).start()

                # Wait for the student process to finish
                student_process.wait()
                processes.remove(student_process)  # Remove finished process
                print("Student process finished. Restarting...")

                # If server or viewer is no longer running, restart them
                if server_process.poll() is not None:
                    print("Server process stopped unexpectedly. Restarting...")
                    terminate_processes([server_process])
                    break

                if viewer_process.poll() is not None:
                    print("Viewer process stopped unexpectedly. Restarting...")
                    terminate_processes([viewer_process])
                    break

            # Restart server and viewer if needed
            terminate_processes([server_process, viewer_process])
            processes.remove(server_process)
            processes.remove(viewer_process)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Terminating all processes...")
        terminate_processes(processes)
        print("Goodbye!")

if __name__ == "__main__":
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    run_programs()
