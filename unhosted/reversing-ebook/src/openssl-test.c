//#include <openssl/evp.h>

#define NULL 0
struct evp_cipher_ctx_st;
typedef struct evp_cipher_ctx_st EVP_CIPHER_CTX;
struct evp_cipher_st;
typedef struct evp_cipher_st EVP_CIPHER;
struct engine_st;
typedef struct engine_st ENGINE;
EVP_CIPHER_CTX *EVP_CIPHER_CTX_new(void);
int EVP_EncryptInit_ex(EVP_CIPHER_CTX *ctx, const EVP_CIPHER *type, ENGINE *impl, const unsigned char *key, const unsigned char *iv);
const EVP_CIPHER *EVP_aes_256_cbc(void);
int EVP_CIPHER_CTX_set_padding(EVP_CIPHER_CTX *x, int padding);
int EVP_EncryptUpdate(EVP_CIPHER_CTX *ctx, unsigned char *out, int *outl, const unsigned char *in, int inl);
void EVP_CIPHER_CTX_free(EVP_CIPHER_CTX *ctx);
int EVP_DecryptInit_ex(EVP_CIPHER_CTX *ctx, const EVP_CIPHER *type, ENGINE *impl, const unsigned char *key, const unsigned char *iv);
int EVP_DecryptUpdate(EVP_CIPHER_CTX *ctx, unsigned char *out, int *outl, const unsigned char *in, int inl);
int EVP_DecryptFinal_ex(EVP_CIPHER_CTX *ctx, unsigned char *outm, int *outl);
int printf(const char *restrict format, ...);
int puts(const char *s);
void *memcpy(void *restrict dest, const void *restrict src, __SIZE_TYPE__ n);

unsigned filekey[8] = {0, 0, 0, 0, 0, 0, 0, 0};
unsigned iv[4] = {0, 0, 0, 0};
unsigned char *text_input = (unsigned char *) "slowreader book\n";
unsigned input[4] = {0, 0, 0, 0};

void init_tigress() {}

void print_key(char *desc, unsigned char *key, int size) {
	printf("%s:\n", desc);
	for (int i = 0; i < size / 4; i++) {
		printf("%x ", ((unsigned int *) key)[i]);
	}
	puts("");
}

int main() {
	unsigned char buffer[32];
	int r = 42;
	int r2;
	EVP_CIPHER_CTX *ctx;

	ctx = EVP_CIPHER_CTX_new();

	print_key("File key", (unsigned char *) filekey, 32);
	print_key("IV", (unsigned char *) iv, 16);

	EVP_EncryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, (unsigned char *) filekey, (unsigned char *) iv);
	EVP_CIPHER_CTX_set_padding(ctx, 0);

	print_key("Input", text_input, 16);

	r2 = EVP_EncryptUpdate(ctx, buffer, &r, text_input, 16);
	printf("r: %d\n", r);
	printf("r2: %d\n", r2);

	print_key("Encrypted", buffer, 16);
	print_key("File key", (unsigned char *) filekey, 32);
	print_key("IV", (unsigned char *) iv, 16);

	EVP_CIPHER_CTX_free(ctx);
	ctx = EVP_CIPHER_CTX_new();

	EVP_DecryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, (unsigned char *) filekey, (unsigned char *) iv);
	EVP_CIPHER_CTX_set_padding(ctx, 0);

	memcpy(input, buffer, 16);
	r2 = EVP_DecryptUpdate(ctx, buffer, &r, (unsigned char *) input, 16);
	printf("r: %d\n", r);
	printf("r2: %d\n", r2);

	r2 = EVP_DecryptFinal_ex(ctx, buffer + 16, &r);
	printf("r: %d\n", r);
	printf("r2: %d\n", r2);

	puts((char *) buffer);
	print_key("Output", buffer, 16);
}
