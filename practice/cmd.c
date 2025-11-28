#include <sys/types.h>
#include <sys/wait.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

/* 명령줄 인수로 받은 명령을 실행시킨다. */
// 지정된 명령어 프로그램을 n번 수행(fork() -> exec())하는 프로그램을 작성하시오.
int main(int argc, char *argv[]) {
    int child, pid, status;
    pid = fork();
    if (pid == 0) {
        execvp(argv[1], &argv[1]);
        fprintf(stderr, "%s:실행 불가\n", argv[1]);
    } else {
        child = wait(&status);
        pritnf("[%d] 자식 프로세스 %d 종료 \n", getpid(), pid);
        pritnf("\t종료 코드 : %d \n", status>>0);
    }
}