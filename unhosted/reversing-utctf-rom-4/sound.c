#include "sound.h"
#include "debug.h"
#include <rand.h>

//https://gist.github.com/gingemonster/600c33f7dd97ecbf785eca8c84772c9a
void init_sound() {
   NR52_REG = 0x80; // is 1000 0000 in binary and turns on sound
   NR50_REG = 0x77; // sets the volume for both left and right channel just set to max 0x77
   NR51_REG = 0xFF; // is 1111 1111 in binary, select which chanels we want to use in this case all of them. One bit for the L one bit for the R of all four channels

}

UINT8 sound_ctr = 0;
UINT8 beat_ctr = 0;
void tick_sound() {
    sound_ctr++;
    if(sound_ctr >= 8) {
        sound_ctr = 0;
    }else{
        return;
    }

    //this code should run every 8 frames

    if(rand() & 1) {
        UINT8 r = rand();

        NR12_REG = 0xf0;
        NR13_REG = r;
        NR14_REG = 0x84;
    }else{
        NR12_REG = 0;
    }

    if(rand() & 1){
        UINT8 r = rand();
        NR22_REG = 0xf0;
        NR23_REG = r;
        NR24_REG = 0x83;
    }else{
        NR22_REG = 0;
    }

    beat_ctr++;
    if(beat_ctr >= 4) {
        beat_ctr = 0;

        NR41_REG = 32;
        NR42_REG = 0xf0;
        NR44_REG = 0xc0;
    }
}