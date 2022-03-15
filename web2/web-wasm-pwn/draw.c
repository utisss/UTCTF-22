#include "spng.h"
#include "inttypes.h"
#include <emscripten/emscripten.h>

void draw_to_canvas(uint8_t* buf, int width, int height) {
    char cmd[100];
    
    sprintf(cmd, "draw_buf(%u, %u, %u)", (uint32_t)buf, width, height);
    emscripten_run_script(cmd);
}

#define COOKIE0 0x42042042
#define COOKIE1 0xdeadbeef

void EMSCRIPTEN_KEEPALIVE draw_img(uint8_t* buf, int buf_len) {
    uint32_t cookie[2];
    cookie[0] = COOKIE0;
    cookie[1] = COOKIE1;
    uint8_t out[3000000];
    size_t sz;
    struct spng_ihdr ihdr;

    spng_ctx *ctx = spng_ctx_new(0);

    spng_set_png_buffer(ctx, buf, buf_len);

    spng_get_ihdr(ctx, &ihdr);

    spng_decoded_image_size(ctx, SPNG_FMT_RGBA8, &sz);

    spng_decode_image(ctx, out, sz, SPNG_FMT_RGBA8, 0);

    for(int i = 0; i < sz; i++) {
        if(i % 4 != 3) {
            out[i] = ~out[i];
        }
    }

    if(cookie[0] != COOKIE0 || cookie[1] != COOKIE1) {
        return;
    }

    draw_to_canvas(out, ihdr.width, ihdr.height);
}