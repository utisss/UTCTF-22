#include <openssl/evp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/random.h>

#define iferror(expr) if (expr) {perror("encryptor"); exit(2);}

unsigned char buffer[64];
unsigned char outbuf[16];

void print_key(char *desc, unsigned char *key, int size) {
	printf("%s:\n", desc);
	for (int i = 0; i < size / 4; i++) {
		printf("%x ", ((unsigned int *) key)[i]);
	}
	puts("");
}

int main(int argc, char* argv[]) {
	int i;
	int r;
	int amt;
	EVP_CIPHER_CTX *ctx;
	if (argc != 3) {
		puts("Usage: encryptor INFILE OUTFILE");
		exit(1);
	}

	iferror(getrandom(buffer, 64, 0) != 64);

	// memset(buffer, 0, 64);

	FILE *inf = fopen(argv[1], "r");
	iferror(!inf);

	FILE *outf = fopen(argv[2], "w");
	iferror(!outf);

	print_key("File key", buffer + 16, 32);
	print_key("IV", buffer + 48, 16);

	ctx = EVP_CIPHER_CTX_new();
	EVP_EncryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, buffer + 16, buffer + 48);
	EVP_CIPHER_CTX_set_padding(ctx, 0);


	((unsigned int *) buffer)[4] ^= 0xd4c73e84;
	((unsigned int *) buffer)[5] ^= 0x8d5aaa1c;
	((unsigned int *) buffer)[6] ^= 0x11df7364;
	((unsigned int *) buffer)[7] ^= 0x8a0bf697;
	((unsigned int *) buffer)[8] ^= 0x85f93e77;
	((unsigned int *) buffer)[9] ^= 0x1147212c;
	((unsigned int *) buffer)[10] ^= 0xe24bf61f;
	((unsigned int *) buffer)[11] ^= 0xbe2b9624;
	for (i = 1; i < 32; i+=2)
		buffer[16 + i] ^= 0xb7;
	for (i = 2; i < 32; i+=3)
		buffer[16+i] ^= 0xd4;
	for (i = 4; i < 32; i+=5)
		buffer[16 + i] ^= 0x62;

	iferror(fwrite(buffer, 64, 1, outf) != 1);

	strcpy((char *) buffer, "slowreader book\n");
	amt = 16;
	for (i = 0; ; i++) {
		if (i == 0) {
			r = 16;
		} else {
			r = fread(buffer, 1, amt, inf);
		}
		if (r == 0 || r == -1) exit(0);
		if (r < amt) {
			memset(buffer + r, 0, amt - r);
		}
		r = EVP_EncryptUpdate(ctx, outbuf, &amt, buffer, 16);
		// print_key("Input", buffer, 16);
		// print_key("Output", outbuf, 16);
		if (r != 1) exit(3);
		amt = 16;
		r = fwrite(outbuf, 16, 1, outf);
		iferror(r != 1);
	}
}
