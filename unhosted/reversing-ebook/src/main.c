#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "gdb.h"
#include "decryptor.h"

#define VERSION_MAJOR 6
#define VERSION_MINOR 96
#define VERSION_PATCH 9

// while(getline(result) == EAGAIN)

int main(int argc, char *argv[]) {
	if (argc != 2
#ifndef DEBUG
			|| strcmp(argv[0], "slowreader")
#endif
			) {
		puts("Usage: slowreader FILE");
		exit(1);
	}
	FILE* inf = fopen(argv[1], "r");
	int r;
	char *line = NULL;
	char *outline = malloc(513);
	size_t len = 0;
	if (!inf) {
		perror("slowreader");
		exit(2);
	}
	printf("Welcome to SlowReader(c) %d.%d.%d\nYou are allowed to read 1 line every %d seconds\nLoading file...\n", VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH, 2);
	r = init_file(inf);
	puts("Press ENTER to load a line.");
	if (r) {
		printf("slowreader: %s\n", strerror(r));
		exit(2);
	}
	while (getline(&line, &len, stdin) != -1) {
		while ((r = get_line(outline)) == EAGAIN);
		if (!r) {
			puts(outline);
		} else if (r == EIO) {
			puts("End of file.");
			exit(0);
		} else {
			printf("slowreader: %s\n", strerror(r));
			exit(2);
		}
	}
}
