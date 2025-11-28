#include <sys/types.h>
#include <sys/stat.h>
#include <dirent.h> 
#include <pwd.h>
#include <grp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_FILE_COUNT 500
#define MAX_FILE_NAME 256

char type(mode_t);
char *perm(mode_t);
void printStat(char*, char*, struct stat*);

// 디렉토리 내용을 자세히 리스트 한다.
int main(int argc, char **argv) {
    DIR *dp;
    char *dir;
    struct stat st;
    struct dirent *d;
    char path[BUFSIZ+1], tmp[MAX_FILE_NAME];
    int cnt, i, j;
    // 파일 개수가 500개 이상일 수 있으므로
    // 동적 할당(malloc)을 쓰는 것이 더 안정적
    char fname[MAX_FILE_COUNT][MAX_FILE_NAME];

    if (argc == 1)
        dir = ".";
    else 
        dir = argv[1];

    if ((dp = opendir(dir)) == NULL) // 디렉토리 열기
        perror(dir);

    // copy all file-name to fname list
    cnt = 0;
    while ((d = readdir(dp)) != NULL) {
        if (cnt >= MAX_FILE_COUNT) {
            fprintf(stderr, "오류: 파일 개수가 너무 많습니다 (최대 %d개).\n", MAX_FILE_COUNT);
            break;
        }
        sprintf(fname[cnt], "%s", d->d_name);
        cnt++;
    }
    // sorting fname list
    for (i=0; i<cnt-1; i++) {
        for (j=0; j<cnt-1-i; j++) {
            if (strcmp(fname[j], fname[j+1]) > 0) {
                strcpy(tmp, fname[j]);
                strcpy(fname[j], fname[j+1]);
                strcpy(fname[j+1], tmp);
            }
        }
    }
    for (i=0; i<cnt; i++) {
        sprintf(path, "%s/%s", dir, fname[i]);
        if (lstat(path, &st) < 0)  // 파일 상태 정보 가져오기
            perror(path);
        else
            printStat(path, fname[i], &st);  // 상태 정보 출력
    }

    closedir(dp);
    exit(0);
}

void printStat(char *pathname, char *file, struct stat *st) {
    printf("%5d ", (int)st->st_blocks);
    printf("%c%s ", type(st->st_mode), perm(st->st_mode));
    printf("%3d ", (int)st->st_nlink);
    printf("%s %s ", 
        getpwuid(st->st_uid)->pw_name,
        getgrgid(st->st_gid)->gr_name);
    printf("%9d ", (int)st->st_size);
    printf("%.12s ", ctime(&st->st_mtime)+4);
    printf("%s\n", file);
}

char type(mode_t mode) {
    if (S_ISREG(mode)) return '-';
    if (S_ISDIR(mode)) return 'd';
    if (S_ISCHR(mode)) return 'c';
    if (S_ISBLK(mode)) return 'b';
    if (S_ISFIFO(mode)) return 'p';
    if (S_ISLNK(mode)) return 'l';
    if (S_ISSOCK(mode)) return 's';
    return '?'; // 알 수 없는 타입
}

char* perm(mode_t mode) {
    int i;
    static char perms[10];
    strcpy(perms, "---------");

    for (i=0; i<3; i++) {
        if (mode & (S_IRUSR >> i*3)) perms[i*3] = 'r';
        if (mode & (S_IWUSR >> i*3)) perms[i*3 + 1] = 'w';
        if (mode & (S_IXUSR >> i*3)) perms[i*3 + 2] = 'x';
    }
    return perms;
}