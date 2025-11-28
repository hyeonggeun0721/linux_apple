#include <stdio.h>
#include <stdlib.h>
#include <utime.h>     // utime() 함수 사용
#include <sys/types.h> // open() 함수 사용
#include <sys/stat.h>  // open() 함수 사용
#include <fcntl.h>     // open() 플래그 (O_CREAT, O_WRONLY)
#include <unistd.h>    // close() 함수 사용
#include <errno.h>     // errno 전역 변수 사용

int main(int argc, char *argv[]) {

    // 1. 인자 개수 확인
    // ./mtouch <file-name> (총 2개)
    if (argc != 2) {
        fprintf(stderr, "사용법: %s <file-name>\n", argv[0]);
        exit(1); // 오류 종료
    }

    // 2. "파일이 존재할 경우"의 로직 시도
    // utime() 함수에 시간 정보로 NULL을 전달하면, 
    // 해당 파일의 시간을 현재 시간으로 설정합니다.
    if (utime(argv[1], NULL) == 0) {
        // utime()이 0을 반환하면 성공한 것입니다.
        // 즉, 파일이 이미 존재했고, 시간 변경을 완료했습니다.
        return 0; // 정상 종료
    }

    // 3. utime() 실패 시, 실패 원인(errno) 확인
    // 만약 실패 원인이 'ENOENT' (Error NO ENTry) 라면,
    // "파일이 존재하지 않기 때문"입니다.
    if (errno == ENOENT) {
        
        // 4. "파일이 존재하지 않을 경우"의 로직 수행
        // O_CREAT: 파일이 없으면 새로 생성합니다.
        // O_WRONLY: 쓰기 전용으로 엽니다. (O_CREAT는 단독 사용 불가)
        // 0644: 생성될 파일의 권한 (rw-r--r--)
        int fd = open(argv[1], O_CREAT | O_WRONLY, 0644);

        if (fd == -1) {
            // 파일 생성(open) 자체도 실패한 경우 (예: 상위 디렉터리 권한 없음)
            perror("open");
            exit(1);
        }

        // 5. 파일 생성 성공 시, 파일 디스크립터 닫기
        close(fd);

        // 파일은 생성되는 순간 자동으로
        // 접근 시간과 수정 시간이 현재 시간으로 설정됩니다.
        return 0; // 정상 종료

    } else {
        // 6. utime() 실패 원인이 ENOENT가 아닌 다른 경우
        // (예: 파일이 존재하지만, 권한이 없어서 시간 변경 실패 - EACCES)
        perror("utime");
        exit(1);
    }
}