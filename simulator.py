import subprocess
import threading
import time
import re
import signal
import sys
import numpy as np

# Global lists to store extracted numbers and steps
saving_numbers = []
saving_steps = []
debug_message = ""
temp_nos = 0
temp_goal = 0
temp_verificacao = 0
temp_exec = 0
max_step = 0

nos_abertos = []
nos_fechados = []
max_depth = []
temp_verificacao = []

# Function to read output from a process
def read_output(pipe, process_name):
    global saving_numbers, saving_steps, temp_nos, temp_goal, temp_verificacao ,temp_exec, debug_message, temp_verificacao, max_step, nos_abertos, nos_fechados, max_depth


    for line in iter(pipe.readline, b''):
        print("\033[H\033[J")
        
        decoded_line = line.decode().strip()
        
        # Extract numbers inside angle brackets
        match_numbers = re.search(r'<(\d+)>', decoded_line)
        if match_numbers:
            saving_numbers.append(int(match_numbers.group(1)))
            debug_message = ""


        # Extract numbers inside square brackets
        match_steps = re.search(r'\[(\d+)\]', decoded_line)
        if match_steps:

            if int(match_steps.group(1)) < max_step:
                saving_steps.append(max_step)
            
            max_step = int(match_steps.group(1))

            match_debug = re.search(r'\[(\d+)\] SCORE (\w+): (\d+)', decoded_line)

            debug_message = debug_message + f"\n\t[{match_debug.group(1)}] SCORE {match_debug.group(2)}: {match_debug.group(3)}"

        match_time_nos = re.search(r'Tempo para encontrar nós:\s*([\d\.e-]+)', decoded_line)
        if match_time_nos:
            temp_nos = max(temp_nos, float(match_time_nos.group(1)))

        match_time_goal = re.search(r'Tempo que demorou para encontrar a solução:\s*([\d\.e-]+)', decoded_line)
        if match_time_goal:
            temp_goal = max(temp_goal, float(match_time_goal.group(1)))

        match_time_exec = re.search(r'Tempo de execução:\s*([\d\.e-]+)', decoded_line)
        if match_time_exec:
            temp_exec = max(temp_exec, float(match_time_exec.group(1)))


        # Extract "Tempo de Verificação"
        match_verificacao = re.search(r'Tempo de Verificação:\s*([\d\.e-]+)', decoded_line)
        if match_verificacao:
            temp_verificacao.append(float(match_verificacao.group(1)))

        # Extract "Nós Abertos"
        match_nos_abertos = re.search(r'Nós Abertos:\s*(\d+)', decoded_line)
        if match_nos_abertos:
            nos_abertos.append(int(match_nos_abertos.group(1)))

        # Extract "Nós Fechados"
        match_nos_fechados = re.search(r'Nós Fechados:\s*(\d+)', decoded_line)
        if match_nos_fechados:
            nos_fechados.append(int(match_nos_fechados.group(1)))

        # Extract "Máx Depth"
        match_max_depth = re.search(r'Máx Depth:\s*(\d+)', decoded_line)
        if match_max_depth:
            max_depth.append(int(match_max_depth.group(1)))


        print(f"Testes Realizados = {len(saving_numbers)}, com média de {(sum(saving_numbers) / len(saving_numbers)) if len(saving_numbers) > 0 else 0} POINTS e {(sum(saving_steps) / len(saving_steps)) if len(saving_steps) > 0 else 0} STEPS" )
        print("Pontuação atual:" ,end="")
        print(debug_message)
        print("Tempos máximos:")
        print(f"\t-Tempo para encontrar nós: {temp_nos}")
        print(f"\t-Tempo que demorou para encontrar a solução: {temp_goal}")
        #print(f"\t-Tempo de Verificação: {temp_verificacao}")
        print(f"\t-Tempo de Execução: {temp_exec}")


    pipe.close()

# Function to terminate all running processes
def terminate_processes(processes):
    for proc in processes:
        if proc.poll() is None:  # Check if the process is running
            proc.terminate()
            try:
                proc.wait(timeout=5)  # Wait for graceful termination
            except subprocess.TimeoutExpired:
                #print(f"Force killing process {proc.pid}")
                proc.kill()

# Signal handler for Ctrl+C
def signal_handler(sig, frame):
    print("\nCtrl+C detected! Terminating all processes...")
    terminate_processes(processes)
    print("Processes terminated. Exiting...")

    print("Trials:", len(saving_numbers))
    print("Average numbers:", sum(saving_numbers) / len(saving_numbers), saving_numbers)
    print("Average steps:", sum(saving_steps) / len(saving_steps), saving_steps)


    #media de pontos por step por jogo

    lista = []

    count = 0
    while True:
        
        if count < len(saving_numbers) and count < len(saving_steps):
            lista.append(saving_numbers[count] / saving_steps[count])
        else:
            break

        count += 1
            

    print("Average points per step:", sum(lista) / len(lista), lista)


    #faz um gráfico com um x de 0 a 0.3 com intervalos de 0.001 sempre que algum tempo de verificação pertencer a um intervalo incrementar 1
    import matplotlib.pyplot as plt

    # Create histogram data
    bins = np.arange(0, 0.301, 0.001)
    hist, bin_edges = np.histogram(temp_verificacao, bins=bins)

    # Plot histogram
    plt.figure(figsize=(10, 6))
    plt.bar(bin_edges[:-1], hist, width=0.001, edgecolor='black')
    plt.xlabel('Tempo de Verificação')
    plt.ylabel('Frequência')
    plt.title('Distribuição dos Tempos de Verificação')
    plt.grid(True)
    plt.show()


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
            #print(f"Server started with PID: {server_process.pid}")
            threading.Thread(target=read_output, args=(server_process.stdout, 'Server')).start()
            threading.Thread(target=read_output, args=(server_process.stderr, 'Server Error')).start()
            processes.append(server_process)

            # Start the student process in a loop
            while True:

                print("Starting student process...")
                student_process = subprocess.Popen(
                    ["python3", "student.py", "hemapefe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                #print(f"Student started with PID: {student_process.pid}")
                processes.append(student_process)

                # Read the student process output
                threading.Thread(target=read_output, args=(student_process.stdout, 'Student')).start()
                threading.Thread(target=read_output, args=(student_process.stderr, 'Student Error')).start()


                # Wait for the student process to finish
                student_process.wait()
                processes.remove(student_process)  # Remove finished process
                print("Student process finished. Restarting...")

                # If server or viewer is no longer running, restart them
                if server_process.poll() is not None:
                    #print("Server process stopped unexpectedly. Restarting...")
                    terminate_processes([server_process])
                    break

            # Restart server and viewer if needed
            terminate_processes([server_process])
            processes.remove(server_process)

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