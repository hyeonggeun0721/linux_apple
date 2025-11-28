#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

#define PORT 8080       // 서버 포트 번호
#define BUFFER_SIZE 1024

int main() {
    int server_fd, client_fd;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_addr_len = sizeof(client_addr);
    char buffer[BUFFER_SIZE];
    int opt = 1;

    // 1. 소켓 생성
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    // [중요] 서버 재실행 시 'Address already in use' 에러 방지 옵션
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt))) {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }

    // 2. 주소 설정
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY; // 모든 인터페이스에서 접속 허용
    server_addr.sin_port = htons(PORT);

    // 3. 바인딩 (Bind)
    if (bind(server_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) == -1) {
        perror("bind failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    // 4. 리슨 (Listen)
    if (listen(server_fd, 5) == -1) {
        perror("listen failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    printf("Server listening on port %d...\n", PORT);

    // 5. 메인 루프 (서버가 죽지 않고 계속 손님을 받음)
    while (1) {
        printf("\nWaiting for new connection...\n");

        // 연결 수락 (Accept)
        if ((client_fd = accept(server_fd, (struct sockaddr *)&client_addr, &client_addr_len)) == -1) {
            perror("accept failed");
            continue; // 에러가 나도 서버를 끄지 않고 다시 대기
        }

        printf("Client connected from %s:%d\n", inet_ntoa(client_addr.sin_addr), ntohs(client_addr.sin_port));

        // 내부 루프: 클라이언트와 대화 (Echo)
        while (1) {
            memset(buffer, 0, BUFFER_SIZE);
            
            // 클라이언트로부터 데이터 읽기
            int bytes_read = read(client_fd, buffer, BUFFER_SIZE);
            
            if (bytes_read <= 0) {
                // 읽은 값이 0이면 클라이언트가 연결을 끊은 것임
                printf("Client disconnected.\n");
                break; // 내부 루프 탈출 -> 외부 루프(accept)로 돌아감
            }

            printf("Received: %s", buffer);

            // 클라이언트에게 답장 보내기
            const char *msg = "Message Received\n";
            write(client_fd, msg, strlen(msg));
        }

        // 대화가 끝난 클라이언트 소켓 닫기
        close(client_fd);
    }

    // (여기까지 도달하지 않음)
    close(server_fd);
    return 0;
}