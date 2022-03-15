/*
 * Various tricks to detect GDB or any related GNU tools
 *
 */


#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>

#define check_strings(str_buff) (strstr(str_buff, "gdb") || strstr(str_buff, "ltrace") || strstr(str_buff, "strace"))

/*
 * Detect GDB by the mean of /proc/$PID/cmdline, which should no be "gdb"
 */
int dbg_cmdline(){
    char buff [24], tmp [16];
    FILE* f;
		int ppid = getppid();

    snprintf(buff, 24, "/proc/%d/cmdline", ppid);
    f = fopen(buff, "r");
    fgets(tmp, 16, f);
    fclose(f);

		if (check_strings(tmp)) {
			kill(ppid, SIGILL);
			return 1;
		} else return 0;
}

/*
 * Check the parent's name
 */
int dbg_getppid_name(){
    char buff1[24], buff2[16];
    FILE* f;
		int ppid = getppid();

    snprintf(buff1, 24, "/proc/%d/status", ppid);
    f = fopen(buff1, "r");
    fgets(buff2, 16, f);
    fclose(f);

		if (check_strings(buff2)) {
			kill(ppid, SIGBUS);
			return 1;
		} else return 0;
}

