#include <stdio.h>
#include "local.h"

int sum_even(int *nums, int len) {
    int total = 0;
    for (int i = 0; i < len; i++) {
        if (nums[i] % 2 == 0) {
            total += nums[i];
        }
    }
    return total;
}

void greet(char *name) {
    printf("hi %s", name);
}
