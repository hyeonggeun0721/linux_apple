/*
 * 리눅스 wc 명령어와 동일한 기능을 수행하는 프로그램
 * 작성자 : 202245811 김형근
 * 작성일 : 2025.11.06
*/

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h> 
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>

int main(int argc, char *argv[]) {
    int i;
    int fd;              // 파일 디스크립터
    int lcnt;            // 라인 수
    int wcnt;            // 단어 수
    int ccnt;            // 바이트/글자 수
    int is_waiting;      // 단어 경계 상태 변수
    ssize_t len;         // read()가 실제로 읽어온 바이트 수를 저장
    char buf[1024];      // 파일에서 읽은 데이터를 임시 저장할 버퍼 (크기 1KB)

    // === 인자 개수 확인 ===
    if (argc != 2) {
        fprintf(stderr, "사용법: %s file \n", argv[0]);
        exit(1); // 오류 코드 1 종료
    }

    // === 파일 열기 (open) ===
    if ((fd = open(argv[1], O_RDONLY)) == -1) {
        perror(argv[1]);
        exit(2); // 오류 코드 2 종료
    }

    lcnt = wcnt = ccnt = 0; // 모든 카운터 0으로 초기화
    is_waiting = 1; // 상태 변수 초기화

    // === 파일 읽기 및 처리 (read, while) ===
    while ((len = read(fd, buf, sizeof(buf))) > 0) {
        ccnt += len;
        
        for (i=0; i<len; i++) {
            // 라인 수 계산
            if (buf[i] == '\n')
                lcnt++;

            // 단어 수 계산
            if (!isspace(buf[i])) { // 공백이 아닌 문자를 만났을 때
                if (is_waiting) {
                    wcnt++;
                    is_waiting = 0;  // 상태를 '단어 내부'(0)로 변경
                }
                // (만약 is_waiting이 0이었다면, 이미 단어 내부이므로 아무것도 안 함)
            }
            else {
                is_waiting = 1; // 공백 문자를 만났을 때 '공백 상태'(1)로 리셋
            }
        }
    }

    // while 루프가 끝난 이유가 파일 끝(len == 0)이 아니라 읽기 오류(len == -1)일 수 있으므로 확인
    if (len == -1) {
        perror("read");
        close(fd); // 오류가 발생했어도 파일 디스크립터는 닫아줘야 함
        exit(3); // 오류 코드 3 종료
    }

    close(fd); // 사용이 끝난 파일 디스크립터를 닫아서 자원 반납

    printf("%2d %2d %2d %s \n", lcnt, wcnt, ccnt, argv[1]); // wc 명령어 형식으로 라인, 단어, 바이트 수, 파일명 출력
    
    return 0;
}