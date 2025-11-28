#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h> // stat, S_I... 매크로 사용

int main(int argc, char *argv[]) {
    
    struct stat buf; // 파일 정보를 저장할 구조체

    // 1. 인자 확인
    if (argc != 2) {
        fprintf(stderr, "사용법: %s <파일이름>\n", argv[0]);
        exit(1);
    }

    // 2. 파일 정보 가져오기 (stat 시스템 호출)
    if (stat(argv[1], &buf) < 0) {
        perror("stat()");
        exit(1);
    }

    // 3. st_mode 값 해석 및 출력 (이미지 형식에 맞게 수정)
    printf("Result: ");

    // 3-1. 소유자(User) 권한 확인
    printf( (buf.st_mode & S_IRUSR) ? "r" : "-");
    printf( (buf.st_mode & S_IWUSR) ? "w" : "-");
    printf( (buf.st_mode & S_IXUSR) ? "x" : "-");

    // 3-2. 그룹(Group) 권한 확인
    printf( (buf.st_mode & S_IRGRP) ? "r" : "-");
    printf( (buf.st_mode & S_IWGRP) ? "w" : "-");
    printf( (buf.st_mode & S_IXGRP) ? "x" : "-");

    // 3-3. 그 외(Others) 권한 확인
    printf( (buf.st_mode & S_IROTH) ? "r" : "-");
    printf( (buf.st_mode & S_IWOTH) ? "w" : "-");
    printf( (buf.st_mode & S_IXOTH) ? "x" : "-");

    // 4. 줄바꿈
    printf("\n");

    return 0;
}