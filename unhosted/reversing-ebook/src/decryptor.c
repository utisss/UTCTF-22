#include <openssl/evp.h>
#include <stdlib.h>
#include <errno.h>
#include <strings.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <assert.h>
#include <stdio.h>
#include <time.h>
#include "decryptor.h"

#define CLOCK_REALTIME 0

EVP_CIPHER_CTX *ctx;
unsigned char *buffer = NULL;
char * strbuf = NULL;
int strbufpos = 0;
int strpos = 0;
struct timespec last;
FILE *infile;

#define check_strings(str_buff) (strstr(str_buff, "gdb") || strstr(str_buff, "ltrace") || strstr(str_buff, "strace"))

/*
 * Detect GDB by the mean of /proc/$PID/cmdline, which should no be "gdb"
 */
int dbg_cmdline(){
    char buff [24], tmp [16];
    FILE* f;
		int ppid = getppid();

    snprintf(buff, 24, "/proc/%d/cmdline", ppid);
    f = fopen(buff, "r");
    fgets(tmp, 16, f);
    fclose(f);

		if (check_strings(tmp)) {
			kill(ppid, SIGILL);
			return 1;
		} else return 0;
}

/*
 * Check the parent's name
 */
int dbg_getppid_name(){
    char buff1[24], buff2[16];
    FILE* f;
		int ppid = getppid();

    snprintf(buff1, 24, "/proc/%d/status", ppid);
    f = fopen(buff1, "r");
    fgets(buff2, 16, f);
    fclose(f);

		if (check_strings(buff2)) {
			kill(ppid, SIGBUS);
			return 1;
		} else return 0;
}


/*
void print_key(char *desc, unsigned char *key, int size) {
	printf("%s:\n", desc);
	for (int i = 0; i < size / 4; i++) {
		printf("%x ", ((unsigned int *) key)[i]);
	}
	puts("");
}
*/

int init_file(FILE* f) {
	int r;
	int i;
	char *tempstr = malloc(512 + 1);
	infile = f;
	free(buffer);
	buffer = malloc(64 + 1);
	if (!buffer) return errno;
	r = fread(buffer, 64, 1, infile);
	strbuf = malloc(512 + 1);
	if (!strbuf) return errno;
	((unsigned int *) buffer)[4] ^= 0xd4c73e84;
	((unsigned int *) buffer)[5] ^= 0x8d5aaa1c;
	((unsigned int *) buffer)[6] ^= 0x11df7364;
	((unsigned int *) buffer)[7] ^= 0x8a0bf697;
	((unsigned int *) buffer)[8] ^= 0x85f93e77;
	((unsigned int *) buffer)[9] ^= 0x1147212c;
	((unsigned int *) buffer)[10] ^= 0xe24bf61f;
	((unsigned int *) buffer)[11] ^= 0xbe2b9624;
	if (r != 1) return EINVAL;

	for (i = 1; i < 32; i+=2)
		buffer[16 + i] ^= 0xb7;

	ctx = EVP_CIPHER_CTX_new();
	dbg_getppid_name();

	for (i = 2; i < 32; i+=3)
		buffer[16+i] ^= 0xd4;

	r = clock_gettime(CLOCK_REALTIME, &last);
	if (r != 0) return errno;

	if (!ctx) return ENOMEM;

	for (i = 4; i < 32; i+=5)
		buffer[16 + i] ^= 0x62;

	// print_key("File key", buffer + 16, 32);
	// print_key("IV", buffer + 48, 16);
	EVP_DecryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, buffer + 16, buffer + 32 + 16);
	EVP_CIPHER_CTX_set_padding(ctx, 0);
	strbuf[0] = 0;

	while ((r = get_line(tempstr)) == EAGAIN);
	if (r) {
		free(tempstr);
		return r;
	} else if (strcmp(tempstr, "slowreader book")) {
		free(tempstr);
		return EINVAL;
	}
	return 0;
}

int get_line(char *result) {
	struct timespec tlast;
	struct timespec t2;
	int i;
	int r;
	char *idx;
	for (i = 0, r = clock_gettime(CLOCK_REALTIME, &tlast); i < 16; i++) {
		if (buffer[i] < 128)
			buffer[i] ^= 0x60;
		else
			buffer[i] ^= 0x54;
		r |= clock_gettime(CLOCK_REALTIME, &t2);
		if (r != 0) return errno;
#ifndef DEBUG
		if (t2.tv_sec > tlast.tv_sec + 1 || (t2.tv_sec - tlast.tv_sec) * 1000 + t2.tv_nsec - tlast.tv_nsec > 500000000)
			*((int*) fileno(stdin)) = EPERM;
#endif
		if (t2.tv_sec - last.tv_sec < 2)
			return EAGAIN;
		tlast = t2;
	}
	dbg_cmdline();

	idx = index(strbuf + strpos, '\n');
	while (!idx) {
		if (strbufpos >= 512 - 16) return ENOMEM;

		r = fread(buffer, 16, 1, infile);
		if (r != 1) return EIO;
		EVP_DecryptUpdate(ctx, (unsigned char *) strbuf + strbufpos, &i, buffer, 16);
		// print_key("Input", buffer, 16);
		// print_key("Output", (unsigned char *) strbuf + strbufpos, 16);
		idx = index(strbuf + strpos, '\n');
		strbufpos += 16;
	}

	*idx = '\0';
	
	strcpy(result, &strbuf[strpos]);

	strpos = idx - strbuf + 1;

	memmove(strbuf, strbuf + strpos, 512 - strpos);
	strbufpos -= strpos;
	strpos = 0;

	r = clock_gettime(CLOCK_REALTIME, &last);
	if (r != 0) return errno;
	return 0;
}
