#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/mman.h>
#include <string.h>

#define ARRAY_SIZE 1000000

void defineMergeableArray(int** ptr) {
    *ptr = mmap(NULL, ARRAY_SIZE * sizeof(int), PROT_READ | PROT_WRITE, MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
    if (*ptr == MAP_FAILED) {
        perror("Memory allocation failed");
        exit(EXIT_FAILURE);
    }
    for (int i = 0; i < ARRAY_SIZE; i++) {
        (*ptr)[i] = i;
    }
    if (madvise(*ptr, ARRAY_SIZE * sizeof(int), MADV_MERGEABLE) == -1) {
        perror("Error advising kernel");
    }
}

void pauseByCommand(char c) {
    switch(c) {
        case 's':
            sleep(10);
            break;
        case 'g':
        default:
            getchar();
            break;
    }
}

void modifyByCommand(char c, int* array1, int* array2) {
    int i;
    switch (c)
    {
        case 's': // single value to -1
            array1[0] = -1;
            break;
        case 'h': // half of all values to -1
            for(i = 0; i < ARRAY_SIZE/2; i++) {
                array1[i] = -1;
            }
            break;
        case 'm': // half of all values, all distinct
        default:
            for(i = 0; i < ARRAY_SIZE/2; i++) {
                array1[i] = -i;
            }
            break;
    }
}

int main() {
    printf("pid: %d\n", getpid()); // useful for /proc/<pid>/ksm_stat
    pauseByCommand('g');

    char pauseCommand = 's';

    int *array1; defineMergeableArray(&array1);
    pauseByCommand(pauseCommand);

    int *array2; defineMergeableArray(&array2);
    pauseByCommand(pauseCommand);

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

    modifyByCommand('m', array1, array2);

    pauseByCommand(pauseCommand);

    /**
     * Below is when modification is just: `array1[0] = -1`
     * i.e. case 's'
     *
     * Then we see
     *  pages_shared 977
     *  pages_sharing 976 (1 page modified above...)
     *
     * ksm_rmap_items 1954
     * ksm_merging_pages 1953
     * ksm_process_profit 7874432
    */

    // Free allocated memory
    munmap(array1, ARRAY_SIZE * sizeof(int));
    munmap(array2, ARRAY_SIZE * sizeof(int));

    return 0;
}
