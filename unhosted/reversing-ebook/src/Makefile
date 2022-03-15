CC=gcc
TIGRESS_HOME=../tigress/3.3.2
CFLAGS=-Wall -Wextra -Wpedantic -m32
ifeq ($(DEBUG), 1)
	CFLAGS+=-g -DDEBUG
else
	CFLAGS+=-O1
endif
LDFLAGS=-lcrypto

DEPS=gdb.h decryptor.h

.PHONY: all clean

all: slowreader encryptor

clean:
	rm -f *.o slowreader encryptor *_obfs.c *_merged.c

%:
	$(CC) $(LDFLAGS) $^ -o $@ $(CFLAGS)
ifneq ($(DEBUG), 1)
	strip --strip-unneeded $@
endif

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

decryptor_obfs.o: decryptor.c
	#../Pluto-Obfuscator/build/bin/clang -c -o $@ $< $(CFLAGS) -mllvm -bcf -mllvm -sub -mllvm -rcf -mllvm -trap-angr -mllvm -vsb
	../Pluto-Obfuscator/build/bin/clang -c -o $@ $< $(CFLAGS) -mllvm -bcf -mllvm -sub -mllvm -trap-angr -mllvm -vsb

ifeq ($(DEBUG), 1)
slowreader: decryptor.o main.o gdb_outside.o
else
slowreader: decryptor_obfs.o main.o gdb_outside.o
endif

encryptor: encryptor.o
