import time

import matplotlib.pyplot as plt
import numba
import numpy as np
import pandas as pd

plt.style.use('ggplot')

# Define the custom rolling apply function
def root_mean_square(x):
    return np.sqrt(np.mean(x**2))

def bench(df: pd.DataFrame, use_numba: bool, use_parallel: bool = False, n_times: int = 10):
    engine = 'numba' if use_numba else None
    engine_kwargs = {'parallel': True, 'nopython': True} if use_parallel else None
    df.rolling(window_size).apply(root_mean_square, raw=True, engine=engine, engine_kwargs=engine_kwargs)

    elapsed_time_list = []
    for _ in range(n_times):
        start_time = time.time()
        df.rolling(window_size).apply(root_mean_square, raw=True, engine=engine, engine_kwargs=engine_kwargs)
        elapsed_time_list.append(time.time() - start_time)
    return np.mean(elapsed_time_list)


# Generate sample data
np.random.seed(42)
data = np.random.rand(int(1e5), 4)
df = pd.DataFrame(data)

window_sizes = range(10, 1001, 100)
mean_time_without_numba = []
mean_time_with_numba = []
mean_time_with_numba_parallel = []
# Benchmark the performance for different window sizes
for window_size in window_sizes:
    # Without Numba
    mean_time = bench(df, use_numba=False)
    mean_time_without_numba.append(mean_time)
    
    mean_time = bench(df, use_numba=True)
    mean_time_with_numba.append(mean_time)

    mean_time = bench(df, use_numba=True, use_parallel=True)
    mean_time_with_numba_parallel.append(mean_time)

mean_time_without_numba = np.array(mean_time_without_numba)
mean_time_with_numba = np.array(mean_time_with_numba)
mean_time_with_numba_parallel = np.array(mean_time_with_numba_parallel)
print("mean_time_without_numba", mean_time_without_numba)
print("mean_time_with_numba", mean_time_with_numba)
print("mean_time_with_numba_parallel", mean_time_with_numba_parallel)

fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(window_sizes, mean_time_without_numba / mean_time_with_numba, label='Numba')
ax.plot(window_sizes, mean_time_without_numba / mean_time_with_numba_parallel, label='Numba + Parallel')

ax.set_xlabel('Window Size')
ax.set_ylabel('Speedup')
ax.set_title('Speedup compared to without Numba: Pandas Rolling Apply')
ax.legend()
fig.savefig("numba_speedup_pandas_rolling_apply.png")
