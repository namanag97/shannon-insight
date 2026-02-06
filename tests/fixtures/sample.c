/* Sample C file for testing tree-sitter parsing. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Struct for greeter */
struct Greeter {
    char prefix[64];
};

/* Initialize greeter */
void greeter_init(struct Greeter *g, const char *prefix) {
    strncpy(g->prefix, prefix, sizeof(g->prefix) - 1);
    g->prefix[sizeof(g->prefix) - 1] = '\0';
}

/* Greet function */
void greeter_greet(struct Greeter *g, const char *name) {
    printf("%s, %s!\n", g->prefix, name);
}

/* Process data with nested loops */
int process_data(int *data, int len) {
    int sum = 0;
    for (int i = 0; i < len; i++) {
        if (data[i] > 0) {
            for (int j = 0; j < data[i]; j++) {
                sum += j;
            }
        }
    }
    return sum;
}

/* Helper function */
static int helper(int x) {
    return x * 2;
}

int main(int argc, char *argv[]) {
    struct Greeter g;
    greeter_init(&g, "Hello");
    greeter_greet(&g, "World");
    return 0;
}
