import numpy as np
import os
from multiprocessing import Process

# Define the computation to perform
def compute_slice(start_row, end_row, shm_path):
    # Load a slice of the array memory-mapped from /dev/shm
    print(f"Process {os.getpid()} loading slice [{start_row}:{end_row}] from shared memory")
    mmapped_array = np.load(shm_path, mmap_mode='r+')
    slice_view = mmapped_array[start_row:end_row]

    # Perform some computation on the slice
    # For example, we'll multiple each element by 2 in the slice
    slice_view[...] = slice_view * 2

    # The changes are automatically saved to the shared memory array
    # due to memory-mapping

# Create a large NumPy array
array_shape = (10000, 10000)
large_array = np.ones(array_shape)

# Define the path in shared memory
shm_path = '/dev/shm/large_array.npy'

# Ensure /dev/shm is available
if not os.path.exists('/dev/shm'):
    raise RuntimeError("/dev/shm is not available on this system.")

# Save the array to the shared memory area
np.save(shm_path, large_array)

# Define the number of processes and rows each process should handle
num_processes = 4
rows_per_process = array_shape[0] // num_processes

# Create and start the processes
processes = []
for i in range(num_processes):
    start_row = i * rows_per_process
    # Ensure the last process gets any remaining rows
    end_row = (i + 1) * rows_per_process if i < num_processes - 1 else array_shape[0]
    p = Process(target=compute_slice, args=(start_row, end_row, shm_path))
    processes.append(p)
    p.start()

# Wait for all processes to finish
for p in processes:
    p.join()

# Load the modified array from shared memory to verify changes
# Should be all 2s
modified_array = np.load(shm_path, mmap_mode='r')
print("Modified array:\n", modified_array)

# Clean up the shared memory file
os.remove(shm_path)
