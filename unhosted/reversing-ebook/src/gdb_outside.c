/*
 * Various tricks to detect GDB or any related GNU tools
 *
 */


#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ptrace.h>

#ifndef DEBUG
/*
 * Classic self ptrace trick: a program can only be ptraced by ONE other.
 */
__attribute__((constructor)) void dbg_ptrace() {
    if(ptrace(PTRACE_TRACEME, 0, 0, 0) == -1) {
			kill(getppid(), SIGTERM);
			exit(1);
		}
    ptrace(PTRACE_DETACH, 0, 0, 0);
}
#endif
