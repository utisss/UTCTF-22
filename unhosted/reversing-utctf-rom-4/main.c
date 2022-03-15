#include <gb/gb.h>
#include <stdio.h>
#include <rand.h>
#include "character.h"
#include "tile_data.h"
#include "map.h"
#include "sound.h"

UINT8 blank_bg[20];

void update_switches() {
   HIDE_WIN;
   SHOW_SPRITES;
   SHOW_BKG;
}

static UINT8 i;
void init() {
   DISPLAY_ON;
   set_bkg_data(0, 17, tile_data);
   set_bkg_data(17, 40, font_data);
   set_sprite_data(0, 15, tile_data+16);

   for(i = 0; i < 20; i++) {
      blank_bg[i] = 0;
   }

   for(i = 0; i < 18; i++) {
      set_bkg_tiles(0, i, 20, 1, blank_bg);
   }

   init_character();
   init_map();
   init_sound();
   draw_map();
}

UINT16 rand_counter;
void main() {
   printf(" \n UTCTF ROM 4\n BY GG\n\n");
   printf(" NOW WITH MUSIC\n\n");
   printf("PRESS START TO BEGIN\n");
   
   while(!(joypad() & J_START)){
      rand_counter++;
   }

   initrand(rand_counter);

   init();

   while(1) {
      rand_counter++;
      handle_input();
      tick_sound();
      tick_character();
      wait_vbl_done();
   }
}
