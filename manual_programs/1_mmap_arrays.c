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
    getchar();

    /**
     * Now (after some time) we see
     *  pages_shared 977
     *  pages_sharing 977 (how many more sites are sharing them i.e. how much saved)
    */

    /**
     * cat /proc/<pid>/ksm_stat
     * ksm_rmap_items 1954
     * ksm_merging_pages 1954
     * ksm_process_profit 7878528
     *  https://elixir.bootlin.com/linux/v6.5/source/mm/ksm.c#L3092
     *  computation:    ksm_saved_pages * sizeof(page) -
                        ksm_rmap_items * sizeof(rmap_item)
        On my system, sizeof(page)=4096, sizeof(rmap_item)=64
     *
     * From https://elixir.bootlin.com/linux/v6.5/source/mm/ksm.c#L2090,
     * we can see that ksm_merging_pages is ksm_pages_sharing+ksm_pages_shared
     * Hence process_profit quite different from general_profit
    */

    array1[0] = -1;
    printf("%d\n", *array1);

    getchar();

    /**
     * Now we see
     *  pages_shared 977
     *  pages_sharing 976 (1 page modified above...)
    */

    /**
     * ksm_rmap_items 1954
     * ksm_merging_pages 1953
     * ksm_process_profit 7874432
    */

    // Free allocated memory
    munmap(array1, ARRAY_SIZE * sizeof(int));
    munmap(array2, ARRAY_SIZE * sizeof(int));

    return 0;
}
