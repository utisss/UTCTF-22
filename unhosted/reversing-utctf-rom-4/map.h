#include <gb/gb.h>

extern const unsigned char *curr_map;
extern UINT8 curr_map_idx;

#define ROW(i) (curr_map + 5*(i))
#define MAP_GET(row, j) (((row)[((j) / 4)] >> (((j) % 4) * 2)) & 0x3)

void init_map();
void draw_map();

void change_map(INT8 delta);
