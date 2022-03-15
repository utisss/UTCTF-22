#include "map.h"
#include "debug.h"
#include "tile_data.h"

const unsigned char *curr_map = map_data;
UINT8 curr_map_idx = 0;

#define ROW(i) (curr_map + 5*(i))
#define MAP_GET(row, j) ((row[(j / 4)] >> ((j % 4) * 2)) & 0x3)

void init_map() {
    curr_map = map_data;
    curr_map_idx = 0;
}

UINT8 i;
UINT8 j;
UINT8 tile;
const unsigned char *row;
void draw_map() {
    for(i = 0; i < 18; i++) {
        row = ROW(i);
        
        for(j = 0; j < 20; j++) {
            tile = MAP_GET(row, j);
            set_bkg_tiles(j, i, 1, 1, &tile);
        }
    }
}

void change_map(INT8 delta) {
    if(delta < 0 && curr_map_idx < -delta) {
        reset();
    }
    if(curr_map_idx + delta >= NUM_MAPS) {
        reset();
    }

    curr_map_idx += delta;

    curr_map = map_data + curr_map_idx * 5 * 18;

    draw_map();
}