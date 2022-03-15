#include "character.h"
#include "map.h"
#include <gb/gb.h>

static INT16 y_v = 0;
static INT16 x_v = 0;
#define MAX_Y_VEL 1000
#define MAX_X_VEL 500
#define MIN_X_VEL 200
#define X_DECEL 10
#define GRAVITY 10
static UINT16 x = 24 * 256;
static UINT16 y = 16 * 256;

void init_character() {
    SPRITES_8x8;
    set_sprite_tile(0, 3);
    move_sprite(0, x, y);

    SHOW_SPRITES;
}

UINT8 ready_for_jump;
static UINT16 new_x;
static UINT16 new_y;
void tick_character() {
    if(y_v < MAX_Y_VEL) {
        y_v += GRAVITY;
    }

    if(x_v > 0) {
        x_v -= X_DECEL;
    }else if(x_v < 0) {
        x_v += X_DECEL;
    }

    new_y = y + y_v;
    new_x = x + x_v;

    if(new_y / (8*256) != y / (8 * 256)) {
        //we are crossing a vertical tile boundary
        if(y_v > 0) {
            //we are going down
            if(new_y / (8 * 256) <= 18 && (MAP_GET(ROW(y / (8 * 256)), x / (8 * 256) - 1) == 1
                || MAP_GET(ROW(y / (8 * 256)), x / (8 * 256)) == 1)) {
                //we are on a floor tile
                y_v = 0;
                new_y = y / (8 * 256) * (8 * 256) + 8*256 - 1;
                ready_for_jump = 1;
            }
        }
    }

    if(new_x / (8*256) != x / (8*256)) {
        //we are crossing a horizontal tile boundary
        if(x_v > 0) {
            //we are going right
            if(new_x / (8 * 256) < 20 && MAP_GET(ROW(y / (8 * 256) - 1), new_x / (8 * 256)) == 1) {
                x_v = 0;
                new_x = x / (8 * 256) * (8 * 256) + 8*256 - 1;
            }
        }else if(x_v < 0) {
            //we are going left
            if(new_x / (8 * 256) > 1 && MAP_GET(ROW(y / (8 * 256) - 1), new_x / (8 * 256) - 1) == 1) {
                x_v = 0;
                new_x = x / (8 * 256) * (8 * 256) + 1;
            }
        }
    }

    if(new_x > (160 << 8)) {
        new_x = 8 << 8;
        change_map(1);
    }

    if(new_x < (8 << 8)) {
        new_x = 160 << 8;
        change_map(-1);
    }

    x = new_x;
    y = new_y;

    if (y > 20 * 8 * 256) {
        reset();
    }

    move_sprite(0, x >> 8, y >> 8);
}

UINT8 input;
void handle_input() {
    input = joypad();
    
    if(input & J_A) {
        //jump
        if(ready_for_jump){
            y_v = -400;
            ready_for_jump = 0;
        }
    }

    if(input & J_LEFT) {
        set_sprite_prop(0, get_sprite_prop(0) | S_FLIPX);
        if(x_v > -MIN_X_VEL) {
            x_v = -MIN_X_VEL;
        }
        x_v -= 20;
        if(x_v < -MAX_X_VEL){
            x_v = -MAX_X_VEL;
        }
    }
    
    if(input & J_RIGHT) {
        set_sprite_prop(0, get_sprite_prop(0) & ~S_FLIPX);
        if(x_v < MIN_X_VEL) {
            x_v = MIN_X_VEL;
        }
        x_v += 20;
        if(x_v > MAX_X_VEL) {
            x_v = MAX_X_VEL;
        }
    }
}