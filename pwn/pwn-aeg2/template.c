#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#define N 512

int exit_code = 0;

//reverse
void permute1(char *buf) {
    char tmp[N];
    for(int i=0;i<N;i++)
        tmp[i] = buf[N-i-1];
    for(int i=0;i<N;i++)
        buf[i] = tmp[i];
}

//swap halves
void permute2(char *buf) {
    char tmp[N];
    for(int i=0;i<N/2;i++)
        tmp[i] = buf[N/2+i];
    for(int i=N/2;i<N;i++)
        tmp[i] = buf[i-N/2];
    for(int i=0;i<N;i++)
        buf[i] = tmp[i];
}

//left rotation
void permute3(char *buf) {
    char tmp[N];
    for(int i=0;i<N-LR_AMOUNT;i++)
        tmp[i] = buf[i+LR_AMOUNT];
    for(int i=N-LR_AMOUNT;i<N;i++)
        tmp[i] = buf[i-N+LR_AMOUNT];
    for(int i=0;i<N;i++)
        buf[i] = tmp[i];
}

//right rotation
void permute4(char *buf) {
    char tmp[N];
    for(int i=0;i<RR_AMOUNT;i++)
        tmp[i] = buf[N-RR_AMOUNT+i];
    for(int i=RR_AMOUNT;i<N;i++)
        tmp[i] = buf[i-RR_AMOUNT];
    for(int i=0;i<N;i++)
        buf[i] = tmp[i];
}

//pairwise swap
void permute5(char *buf) {
    char tmp[N];
    for(int i=0;i<N;i+=2) {
        tmp[i] = buf[i+1];
        tmp[i+1] = buf[i];
    }
    for(int i=0;i<N;i++)
        buf[i] = tmp[i];
}

//left rotate groups
void permute6(char *buf) {
    char tmp[N];
    for(int i=0;i<N;i+=LRG_SIZE) {
        for(int j=i;j<i+LRG_SIZE-1;j++) {
            tmp[j] = buf[j+1];
        }
        tmp[i+LRG_SIZE-1] = buf[i];
    }
    for(int i=0;i<N;i++)
        buf[i] = tmp[i];
}

//right rotate groups
void permute7(char *buf) {
    char tmp[N];
    for(int i=0;i<N;i+=RRG_SIZE) {
        tmp[i] = buf[i+RRG_SIZE-1];
        for(int j=i+1;j<i+RRG_SIZE;j++) {
            tmp[j] = buf[j-1];
        }
    }
    for(int i=0;i<N;i++)
        buf[i] = tmp[i];
}

//reverse groups
void permute8(char *buf) {
    char tmp[N];
    for(int i=0;i<N;i+=RG_SIZE) {
        for(int j=i;j<i+RG_SIZE;j++) {
            tmp[j] = buf[i+i+RG_SIZE-1-j];
        }
    }
    for(int i=0;i<N;i++)
        buf[i] = tmp[i];
}

void permute(char *buf) {
    PERMUTATION1
    PERMUTATION2
    PERMUTATION3
    PERMUTATION4
    PERMUTATION5
    PERMUTATION6
    PERMUTATION7
    PERMUTATION8
}

int main(int argc, char **argv) {
    char buf[N+2] = {};
    fgets(buf,N+2,stdin);
    permute(buf);
    printf(buf);
    exit(exit_code);
}
