/*
 * CI Message Bus (Unix Domain Socket Version)
 * 
 * Provides non-blocking message queues for CI-CI communication
 * using Unix domain sockets for macOS compatibility.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <fcntl.h>
#include <errno.h>
#include <signal.h>
#include <time.h>
#include <sys/stat.h>

#define MAX_MSG_SIZE 8192
#define SOCKET_DIR "/tmp/ci_queues"
#define SOCKET_PREFIX "ci_"

typedef struct {
    char sender[64];
    char type[32];
    int priority;
    time_t timestamp;
    int content_len;
    char content[MAX_MSG_SIZE - 128];
} CIMessage;

// Ensure socket directory exists
void ensure_socket_dir() {
    mkdir(SOCKET_DIR, 0777);
}

// Get socket path for a CI
void get_socket_path(const char *ci_name, char *path, size_t path_size) {
    snprintf(path, path_size, "%s/%s%s.sock", SOCKET_DIR, SOCKET_PREFIX, ci_name);
}

// Create a listening socket for a CI
int create_ci_socket(const char *ci_name) {
    ensure_socket_dir();
    
    char socket_path[256];
    get_socket_path(ci_name, socket_path, sizeof(socket_path));
    
    // Remove existing socket
    unlink(socket_path);
    
    int sock = socket(AF_UNIX, SOCK_DGRAM, 0);
    if (sock < 0) {
        perror("socket");
        return -1;
    }
    
    // Make non-blocking
    int flags = fcntl(sock, F_GETFL, 0);
    fcntl(sock, F_SETFL, flags | O_NONBLOCK);
    
    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, socket_path, sizeof(addr.sun_path) - 1);
    
    if (bind(sock, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("bind");
        close(sock);
        return -1;
    }
    
    // Set permissions
    chmod(socket_path, 0666);
    
    return sock;
}

// Send message to a CI
int send_message_to_ci(const char *target_ci, const CIMessage *msg) {
    char socket_path[256];
    get_socket_path(target_ci, socket_path, sizeof(socket_path));
    
    // Check if target socket exists
    if (access(socket_path, F_OK) != 0) {
        fprintf(stderr, "Target CI '%s' queue does not exist\n", target_ci);
        return -1;
    }
    
    int sock = socket(AF_UNIX, SOCK_DGRAM, 0);
    if (sock < 0) return -1;
    
    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, socket_path, sizeof(addr.sun_path) - 1);
    
    int ret = sendto(sock, msg, sizeof(CIMessage), 0,
                     (struct sockaddr*)&addr, sizeof(addr));
    
    if (ret < 0) {
        perror("sendto");
    }
    
    close(sock);
    return ret > 0 ? 0 : -1;
}

// Receive message (non-blocking)
int receive_message_from_socket(int sock, CIMessage *msg) {
    ssize_t ret = recv(sock, msg, sizeof(CIMessage), 0);
    
    if (ret == -1) {
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            return 0;  // No messages
        }
        return -1;  // Error
    }
    
    return ret > 0 ? 1 : 0;
}

// List all CI queues
void list_queues() {
    printf("CI Queues in %s:\n", SOCKET_DIR);
    
    char cmd[512];
    snprintf(cmd, sizeof(cmd), "ls -la %s/%s*.sock 2>/dev/null | awk '{print $9}' | xargs -I {} basename {} .sock | sed 's/^%s//'", 
             SOCKET_DIR, SOCKET_PREFIX, SOCKET_PREFIX);
    system(cmd);
}

// Main test program
int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <command> [args...]\n", argv[0]);
        fprintf(stderr, "Commands:\n");
        fprintf(stderr, "  create <ci_name>              - Create queue for CI\n");
        fprintf(stderr, "  send <target> <msg> [sender]  - Send message\n");
        fprintf(stderr, "  recv <ci_name> [timeout_ms]   - Receive messages\n");
        fprintf(stderr, "  destroy <ci_name>             - Remove queue\n");
        fprintf(stderr, "  list                          - List all queues\n");
        return 1;
    }
    
    const char *cmd = argv[1];
    
    if (strcmp(cmd, "create") == 0 && argc >= 3) {
        int sock = create_ci_socket(argv[2]);
        if (sock >= 0) {
            printf("Created queue for %s\n", argv[2]);
            close(sock);
            return 0;
        }
        return 1;
    }
    
    if (strcmp(cmd, "send") == 0 && argc >= 4) {
        CIMessage msg;
        memset(&msg, 0, sizeof(msg));
        
        strncpy(msg.sender, argc >= 5 ? argv[4] : "cli", sizeof(msg.sender)-1);
        strncpy(msg.type, "user_message", sizeof(msg.type)-1);
        strncpy(msg.content, argv[3], sizeof(msg.content)-1);
        msg.content_len = strlen(msg.content);
        msg.priority = 10;
        msg.timestamp = time(NULL);
        
        if (send_message_to_ci(argv[2], &msg) == 0) {
            printf("Sent message to %s\n", argv[2]);
            return 0;
        }
        fprintf(stderr, "Failed to send message\n");
        return 1;
    }
    
    if (strcmp(cmd, "recv") == 0 && argc >= 3) {
        int sock = create_ci_socket(argv[2]);
        if (sock < 0) return 1;
        
        int timeout_ms = argc >= 4 ? atoi(argv[3]) : 0;
        
        CIMessage msg;
        int count = 0;
        time_t start = time(NULL);
        
        while (1) {
            if (receive_message_from_socket(sock, &msg) > 0) {
                printf("Message %d:\n", ++count);
                printf("  From: %s\n", msg.sender);
                printf("  Type: %s\n", msg.type);
                printf("  Priority: %d\n", msg.priority);
                printf("  Time: %s", ctime(&msg.timestamp));
                printf("  Content: %s\n", msg.content);
                printf("\n");
            }
            
            if (timeout_ms > 0 && (time(NULL) - start) * 1000 >= timeout_ms) {
                break;
            }
            
            if (timeout_ms == 0 && count == 0) {
                printf("No messages in queue\n");
                break;
            }
            
            usleep(10000);  // 10ms
        }
        
        close(sock);
        return 0;
    }
    
    if (strcmp(cmd, "destroy") == 0 && argc >= 3) {
        char socket_path[256];
        get_socket_path(argv[2], socket_path, sizeof(socket_path));
        unlink(socket_path);
        printf("Destroyed queue for %s\n", argv[2]);
        return 0;
    }
    
    if (strcmp(cmd, "list") == 0) {
        list_queues();
        return 0;
    }
    
    fprintf(stderr, "Unknown command: %s\n", cmd);
    return 1;
}