#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

int main() {
    char type[100];
    char format[100];
    puts("What kind of data do you have?");
    gets(type);
    if(strcmp(type, "big data") == 0) {
        strcat(format, "% 20s");
    }
    else if(strcmp(type, "smol data") == 0) {
        strcat(format, "% 5s");
    }
    else {
        puts("Error");
    }
    char data[100];
    puts("Give me your data");
    gets(data);

    printf(format, data);
    printf("\n");
    
    return 0;
}

void get_flag() {
  char*  args[2] = {"/bin/sh", NULL};
  execve(args[0], args, NULL);
}
