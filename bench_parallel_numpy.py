from multiprocessing import shared_memory
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time

import numpy as np

def process_large_numpy_arr(arr):
    # expensive
    return np.sin(arr) ** 2 + np.cos(arr) ** 2

def sequential_process(arr):
    return process_large_numpy_arr(arr)


def multithreaded_process(arr, num_threads):
    num_elements = len(arr)
    chunk_size = num_elements // num_threads
    chunks = []
    for i in range(num_threads):
        start_index = i * chunk_size
        end_index = start_index + chunk_size
        if i == num_threads - 1:
            end_index = num_elements
        chunk = arr[start_index:end_index]
        chunks.append(chunk)

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = executor.map(process_large_numpy_arr, chunks)

    return np.concatenate(list(results))


def multiprocessing_process(arr, num_processes):
    num_elements = len(arr)
    chunk_size = num_elements // num_processes
    chunks = []
    for i in range(num_threads):
        start_index = i * chunk_size
        end_index = start_index + chunk_size
        if i == num_threads - 1:
            end_index = num_elements
        chunk = arr[start_index:end_index]
        chunks.append(chunk)

    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        results = executor.map(process_large_numpy_arr, chunks)

    return np.concatenate(list(results))



def multiprocessing_process_shm(arr, num_processes):
    num_elements = len(arr)
    chunk_size = num_elements // num_processes
    processes = []

    # create shared memory block
    shm = shared_memory.SharedMemory(create=True, size=arr.nbytes)
    results = np.ndarray(arr.shape, dtype=arr.dtype, buffer=shm.buf)

    def process_function(process_index):
        start_index = process_index * chunk_size
        end_index = start_index + chunk_size
        if process_index == num_processes - 1:
            end_index = num_elements
        results[start_index:end_index] = process_large_numpy_arr(arr[start_index:end_index])

    for i in range(num_processes):
        process = mp.Process(target=process_function, args=(i,))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    results = np.array(results[:])

    # release shared memory block
    shm.close()
    shm.unlink()
    return results

if __name__ == '__main__':
    # Generate random input array
    input_size = int(1e8)
    input_array = np.random.rand(input_size)

    # Sequential processing with NumPy
    start_time = time.time()
    seq_result = sequential_process(input_array)
    seq_time = time.time() - start_time
    print(f"Sequential processing time: {seq_time:.3f} seconds")

    # Multithreading with NumPy
    for num_threads in [2, 4, 8, 16]:
        start_time = time.time()
        mt_result = multithreaded_process(input_array, num_threads)
        mt_time = time.time() - start_time
        print(f"Multithreading with {num_threads} threads time: {mt_time:.3f} seconds")

    # Multiprocessing with NumPy and shared memory
    for num_processes in [2, 4, 8, 16]:
        start_time = time.time()
        mp_result = multiprocessing_process(input_array, num_processes)
        mp_time = time.time() - start_time
        print(f"Multiprocessing with {num_processes} processes time: {mp_time:.3f} seconds")

    # Multiprocessing with shared memory
    for num_processes in [2, 4, 8, 16]:
        start_time = time.time()
        mp_shared_result = multiprocessing_process_shm(
            input_array, num_processes)
        mp_shared_time = time.time() - start_time
        print(f"Multiprocessing with {num_processes} processes and shared memory time: {mp_shared_time:.3f} seconds")

    # Check results
    print("Sequential and multithreaded results match:",
          np.allclose(seq_result, mt_result))
    print("Sequential and multiprocessing results match:",
          np.allclose(seq_result, mp_result))
    print("Sequential and multiprocessing with shared memory results match:",
          np.allclose(seq_result, mp_shared_result))
