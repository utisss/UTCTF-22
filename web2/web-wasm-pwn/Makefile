a.out.wasm: *.c *.h Makefile
	emcc *.c -Wl,--stack-first -s "EXTRA_EXPORTED_RUNTIME_METHODS=['ccall', 'cwrap']"

a.out.js: a.out.wasm

a.out.wat: a.out.wasm
	wasm2wat a.out.wasm -o a.out.wat