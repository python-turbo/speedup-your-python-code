#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

int main() {
    const char *shm_name = "/my_shared_memory";
    const int SIZE = 10000 * 10000 * sizeof(double); // Size of the memory region

    // Create a new shared memory object
    int shm_fd = shm_open(shm_name, O_CREAT | O_RDWR, 0666);
    if (shm_fd == -1) {
        perror("shm_open");
        return EXIT_FAILURE;
    }

    // Define the size of the shared memory object
    if (ftruncate(shm_fd, SIZE) == -1) {
        perror("ftruncate");
        return EXIT_FAILURE;
    }


    // List the contents of /dev/shm to show the shared memory file
    printf("Contents of /dev/shm after creating the shared memory object:\n");
    system("ls -lh /dev/shm/");

    // Map the shared memory object
    double *shared_memory = (double *)mmap(0, SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);
    if (shared_memory == MAP_FAILED) {
        perror("mmap");
        return EXIT_FAILURE;
    }

    // Now you can use the shared memory array
    // Example: Initialize the array with some values
    for (size_t i = 0; i < (SIZE / sizeof(double)); i++) {
        shared_memory[i] = i;
    }

    // Unmap the shared memory segment
    if (munmap(shared_memory, SIZE) == -1) {
        perror("munmap");
        return EXIT_FAILURE;
    }

    // Close the shared memory object
    if (close(shm_fd) == -1) {
        perror("close");
        return EXIT_FAILURE;
    }

    // Remove the shared memory object
    if (shm_unlink(shm_name) == -1) {
        perror("shm_unlink");
        return EXIT_FAILURE;
    }

    // List contents of /dev/shm after unlinking to show it has been removed
    printf("Contents of /dev/shm after creating the shared memory object:\n");
    system("ls -lh /dev/shm/");

    return EXIT_SUCCESS;
}
