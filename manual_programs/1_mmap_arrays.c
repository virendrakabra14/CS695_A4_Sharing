#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/mman.h>
#include <string.h>

#define ARRAY_SIZE 1000000

int main() {
    printf("pid: %d\n", getpid()); // useful for /proc/<pid>/ksm_stat

    // Allocate memory using mmap for two identical arrays
    int *array1 = mmap(NULL, ARRAY_SIZE * sizeof(int), PROT_READ | PROT_WRITE, MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
    int *array2 = mmap(NULL, ARRAY_SIZE * sizeof(int), PROT_READ | PROT_WRITE, MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);

    if (array1 == MAP_FAILED || array2 == MAP_FAILED) {
        perror("Memory allocation failed");
        exit(EXIT_FAILURE);
    }

    // Initialize both arrays with the same values
    for (int i = 0; i < ARRAY_SIZE; i++) {
        array1[i] = i;
        array2[i] = i;
    }

    // Advise the kernel that these memory regions are mergeable
    if (madvise(array1, ARRAY_SIZE * sizeof(int), MADV_MERGEABLE) == -1 || 
        madvise(array2, ARRAY_SIZE * sizeof(int), MADV_MERGEABLE) == -1) {
        perror("Error advising kernel");
    }

    // Sleep to allow time for KSM to potentially merge identical pages
    sleep(10);

    /**
     * Now (after some time) we see
     *  pages_shared 977
     *  pages_sharing 977 (how many more sites are sharing them i.e. how much saved)
    */

    array1[0] = -1;
    printf("%d\n", *array1);

    sleep(60);

    /**
     * Now we see
     *  pages_shared 977
     *  pages_sharing 976 (1 page modified above...)
    */

    // Free allocated memory
    munmap(array1, ARRAY_SIZE * sizeof(int));
    munmap(array2, ARRAY_SIZE * sizeof(int));

    return 0;
}
