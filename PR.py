import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np
import random

# Función principal que implementa el algoritmo SRTN
def srtn_scheduling(processes):
    processes.sort(key=lambda x: x[1])  # Ordena los procesos por tiempo de llegada
    gantt_chart = []  # Lista para almacenar (proceso, tiempo) para el diagrama de Gantt
    remaining_time = {p[0]: p[2] for p in processes}  # Tiempo restante por proceso
    start_time = {}  # Tiempo de inicio de cada proceso
    end_time = {}  # Tiempo de finalización de cada proceso
    time = 0
    completed = 0  # Contador de procesos completados
    n = len(processes)
    executed_processes = []  # Lista del orden de ejecución de procesos

    # Simulación del tiempo del sistema
    while completed < n:
        # Procesos listos para ejecutarse en el tiempo actual
        ready_queue = [p for p in processes if p[1] <= time and remaining_time[p[0]] > 0]
        if not ready_queue:
            time += 1  # Avanza el tiempo si no hay procesos listos
            continue

        # Selecciona el proceso con menor tiempo restante
        current_process = min(ready_queue, key=lambda x: remaining_time[x[0]])
        gantt_chart.append((current_process[0], time))  # Agrega evento al diagrama de Gantt
        executed_processes.append(current_process[0])  # Guarda ejecución para mostrarla
        if current_process[0] not in start_time:
            start_time[current_process[0]] = time  # Registra el tiempo de inicio
        remaining_time[current_process[0]] -= 1  # Disminuye el tiempo restante

        if remaining_time[current_process[0]] == 0:
            completed += 1  # Marca el proceso como completado
            end_time[current_process[0]] = time + 1  # Registra su tiempo de finalización

        time += 1  # Avanza el tiempo del sistema

    # Calcula los resultados por proceso
    results = {}
    for pid, arrival, burst in processes:
        turnaround = end_time[pid] - arrival  # Tiempo de retorno
        waiting = turnaround - burst  # Tiempo de espera
        results[pid] = {
            "Llegada": arrival,
            "Ejecución": burst,
            "Inicio": start_time[pid],
            "Fin": end_time[pid],
            "Retorno": turnaround,
            "Espera": waiting
        }

    return gantt_chart, executed_processes, results  # Retorna todo para su visualización

# Dibuja el diagrama de Gantt usando matplotlib
def draw_gantt_chart(gantt_chart, executed_processes):
    fig, ax = plt.subplots(figsize=(10, 5))
    y_labels = list(set(executed_processes))
    y_labels.sort()
    spacing = 0.6  # tamaño del interlineado entre procesos
    y_positions = {p: i * spacing for i, p in enumerate(y_labels)}


    colors = {p: "#" + ''.join(random.choices('0123456789ABCDEF', k=6)) for p in y_labels}
    start_flags = set()  # Guardará qué procesos ya tienen marcada su 'X'

    # Líneas horizontales punteadas y etiquetas de proceso
    for process in y_labels:
        y = y_positions[process]
        ax.hlines(y, xmin=0, xmax=gantt_chart[-1][1] + 2, color='black', linestyle='--', linewidth=1)
        ax.text(-0.5, y, process, va='center', ha='right', fontsize=10, fontweight='bold')

    # Dibujar barras y una sola X de inicio por proceso
    for process, start_time in gantt_chart:
        y = y_positions[process]
        ax.broken_barh([(start_time, 1)], (y - 0.3, 0.3), facecolors=colors[process], edgecolor='black')

        if process not in start_flags:
            ax.plot(start_time, y, marker='x', color='purple', markersize=8)
            start_flags.add(process)

    ax.set_yticks([y_positions[p] for p in y_labels])
    ax.set_yticklabels(y_labels)
    ax.set_xticks(range(gantt_chart[-1][1] + 2))
    ax.set_xlim(0, gantt_chart[-1][1] + 2)
    ax.set_ylim(-0.5, max(y_positions.values()) + 1)
    ax.set_xlabel("")
    ax.set_ylabel("")

    # Flechas estéticas en los ejes
    ax.annotate("", xy=(gantt_chart[-1][1] + 1.8, -1), xytext=(0, -1),
                arrowprops=dict(arrowstyle="->", color="black"))
    ax.annotate("", xy=(-0.5, len(y_labels) - 0.5), xytext=(-0.5, -1),
                arrowprops=dict(arrowstyle="->", color="black"))

    ax.set_title("Diagrama de Gantt", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show(block=False)



# Muestra los resultados de ejecución en una tabla usando Tkinter
def show_results_table(results):
    result_window = tk.Toplevel(root)  # Ventana emergente
    result_window.title("Resultados de Planificación")

    # Encabezados de la tabla
    headers = ["Proceso", "T.Llegada", "T.Ejecución", "T.Inicio", "T.Fin", "T.Retorno", "T.Espera"]
    for i, header in enumerate(headers):
        tk.Label(result_window, text=header, font=('Arial', 10, 'bold'),
                borderwidth=1, relief='solid', width=10).grid(row=0, column=i)

    total_espera = 0
    total_retorno = 0

    # Filas con los datos de cada proceso
    for row, (pid, data) in enumerate(results.items(), start=1):
        tk.Label(result_window, text=pid, borderwidth=1, relief='solid', width=10).grid(row=row, column=0)
        for col, key in enumerate(["Llegada", "Ejecución", "Inicio", "Fin", "Retorno", "Espera"], start=1):
            valor = data[key]
            tk.Label(result_window, text=str(valor), borderwidth=1, relief='solid', width=10).grid(row=row, column=col)
            if key == "Retorno":
                total_retorno += valor
            elif key == "Espera":
                total_espera += valor

    # Calcula y muestra los promedios
    n = len(results)
    avg_retorno = total_retorno / n
    avg_espera = total_espera / n

    # Fila de promedios
    tk.Label(result_window, text="PROMEDIO", font=('Arial', 10, 'bold'),
            borderwidth=1, relief='solid', width=10).grid(row=row+1, column=0)
    for col in range(1, 7):
        if col == 5:
            val = f"{avg_retorno:.2f}"
        elif col == 6:
            val = f"{avg_espera:.2f}"
        else:
            val = "-"
        tk.Label(result_window, text=val, borderwidth=1, relief='solid', width=10).grid(row=row+1, column=col)

# Extrae los datos ingresados por el usuario y ejecuta el algoritmo
def get_process_data():
    try:
        processes = []
        for pid_entry, arrival_entry, burst_entry, _ in process_entries:
            pid = pid_entry.get().strip()
            arrival = int(arrival_entry.get())
            burst = int(burst_entry.get())

            # Validación básica de datos
            if not pid or arrival < 0 or burst <= 0:
                raise ValueError("Datos inválidos")

            processes.append((pid, arrival, burst))

        # Ejecuta el algoritmo y muestra resultados
        gantt_chart, executed_processes, results = srtn_scheduling(processes)
        draw_gantt_chart(gantt_chart, executed_processes)
        show_results_table(results)
    except Exception as e:
        messagebox.showerror("Error", f"Entrada inválida: {e}")  # Muestra error si algo falla

# Agrega una nueva fila para ingresar datos de un proceso
def add_process_input():
    row_frame = tk.Frame(process_container)
    row_frame.pack(pady=2)

    pid_entry = tk.Entry(row_frame, width=10)
    pid_entry.pack(side=tk.LEFT, padx=5)
    arrival_entry = tk.Entry(row_frame, width=10)
    arrival_entry.pack(side=tk.LEFT, padx=5)
    burst_entry = tk.Entry(row_frame, width=10)
    burst_entry.pack(side=tk.LEFT, padx=5)

    # Botón para eliminar esta fila
    delete_button = tk.Button(row_frame, text="X", command=lambda: remove_process_input(row_frame))
    delete_button.pack(side=tk.LEFT, padx=5)

    process_entries.append((pid_entry, arrival_entry, burst_entry, row_frame))

# Elimina una fila de entrada de proceso
def remove_process_input(row_frame):
    for i, (entry, frame_ref) in enumerate(process_entries):
        if frame_ref == row_frame:
            frame_ref.destroy()
            process_entries.pop(i)
            break

# Elimina todas las filas de entrada
def clear_all_processes():
    for *_, frame_ref in process_entries:
        frame_ref.destroy()
    process_entries.clear()

# ---------------- INTERFAZ PRINCIPAL ----------------

root = tk.Tk()
root.title("Planificador SRTN")  # Título de la ventana

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Ingrese los procesos (uno por fila):").pack()

# Encabezados de columnas
header = tk.Frame(frame)
header.pack()

tk.Label(header, text="ID", width=10, font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
tk.Label(header, text="Llegada", width=10, font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
tk.Label(header, text="Ejecución", width=10, font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
tk.Label(header, text="Eliminar", width=10, font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

process_container = tk.Frame(frame)  # Contenedor para entradas de procesos
process_container.pack()
process_entries = []  # Lista que guarda todas las entradas

add_process_input()  # Agrega la primera fila por defecto

# Botones de la interfaz
btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

tk.Button(btn_frame, text="Agregar Proceso", command=add_process_input).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Limpiar Procesos", command=clear_all_processes).pack(side=tk.LEFT, padx=5)
tk.Button(root, text="Generar Gantt", command=get_process_data).pack(pady=10)

root.mainloop()  # Inicia el bucle principal de la interfaz
