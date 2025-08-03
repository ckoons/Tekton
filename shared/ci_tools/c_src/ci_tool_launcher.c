/*
 * CI Tool Launcher
 * 
 * A simple, reliable C program to launch CI tools with proper
 * stdin/stdout/stderr handling and socket bridge connection.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <signal.h>
#include <errno.h>
#include <fcntl.h>

#define MAX_ARGS 64
#define BUFFER_SIZE 4096

typedef struct {
    char *tool_name;
    char *executable;
    char **args;
    int port;
    int socket_mode;  // 0 = stdio only, 1 = socket bridge
} LaunchConfig;

static pid_t child_pid = -1;

// Signal handler for clean shutdown
void handle_signal(int sig) {
    (void)sig;  // Suppress unused parameter warning
    if (child_pid > 0) {
        kill(child_pid, SIGTERM);
        waitpid(child_pid, NULL, 0);
    }
    exit(0);
}

// Parse command line arguments
LaunchConfig* parse_args(int argc, char *argv[]) {
    LaunchConfig *config = calloc(1, sizeof(LaunchConfig));
    if (!config) {
        perror("calloc");
        exit(1);
    }
    
    config->args = calloc(MAX_ARGS, sizeof(char*));
    if (!config->args) {
        perror("calloc");
        exit(1);
    }
    
    int arg_count = 0;
    
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--tool") == 0 && i + 1 < argc) {
            config->tool_name = argv[++i];
        } else if (strcmp(argv[i], "--executable") == 0 && i + 1 < argc) {
            config->executable = argv[++i];
        } else if (strcmp(argv[i], "--port") == 0 && i + 1 < argc) {
            config->port = atoi(argv[++i]);
            config->socket_mode = 1;
        } else if (strcmp(argv[i], "--args") == 0) {
            // Rest of arguments are tool args
            i++;
            while (i < argc && arg_count < MAX_ARGS - 1) {
                config->args[arg_count++] = argv[i++];
            }
            break;
        }
    }
    
    if (!config->executable) {
        fprintf(stderr, "Error: --executable required\n");
        exit(1);
    }
    
    // Set up args array with executable as first element
    char **final_args = calloc(arg_count + 2, sizeof(char*));
    final_args[0] = config->executable;
    for (int i = 0; i < arg_count; i++) {
        final_args[i + 1] = config->args[i];
    }
    free(config->args);
    config->args = final_args;
    
    return config;
}

// Bridge between socket and stdio
void socket_bridge(int sock_fd, int stdin_fd, int stdout_fd) {
    fd_set read_fds;
    char buffer[BUFFER_SIZE];
    int max_fd = (sock_fd > stdout_fd) ? sock_fd : stdout_fd;
    
    while (1) {
        FD_ZERO(&read_fds);
        FD_SET(sock_fd, &read_fds);
        FD_SET(stdout_fd, &read_fds);
        
        if (select(max_fd + 1, &read_fds, NULL, NULL, NULL) < 0) {
            if (errno == EINTR) continue;
            perror("select");
            break;
        }
        
        // Socket -> stdin
        if (FD_ISSET(sock_fd, &read_fds)) {
            ssize_t n = recv(sock_fd, buffer, BUFFER_SIZE, 0);
            if (n <= 0) break;
            
            if (write(stdin_fd, buffer, n) != n) {
                perror("write to stdin");
                break;
            }
        }
        
        // Stdout -> socket
        if (FD_ISSET(stdout_fd, &read_fds)) {
            ssize_t n = read(stdout_fd, buffer, BUFFER_SIZE);
            if (n <= 0) break;
            
            if (send(sock_fd, buffer, n, 0) != n) {
                perror("send to socket");
                break;
            }
        }
    }
}

int main(int argc, char *argv[]) {
    LaunchConfig *config = parse_args(argc, argv);
    
    // Set up signal handlers
    signal(SIGTERM, handle_signal);
    signal(SIGINT, handle_signal);
    signal(SIGPIPE, SIG_IGN);
    
    // Create pipes for child process
    int stdin_pipe[2], stdout_pipe[2], stderr_pipe[2];
    
    if (pipe(stdin_pipe) < 0 || pipe(stdout_pipe) < 0 || pipe(stderr_pipe) < 0) {
        perror("pipe");
        exit(1);
    }
    
    // Fork child process
    child_pid = fork();
    if (child_pid < 0) {
        perror("fork");
        exit(1);
    }
    
    if (child_pid == 0) {
        // Child process
        
        // Set up stdio
        dup2(stdin_pipe[0], STDIN_FILENO);
        dup2(stdout_pipe[1], STDOUT_FILENO);
        dup2(stderr_pipe[1], STDERR_FILENO);
        
        // Close unused pipe ends
        close(stdin_pipe[1]);
        close(stdout_pipe[0]);
        close(stderr_pipe[0]);
        
        // Close pipe fds
        close(stdin_pipe[0]);
        close(stdout_pipe[1]);
        close(stderr_pipe[1]);
        
        // Execute the tool
        execvp(config->executable, config->args);
        perror("execvp");
        exit(1);
    }
    
    // Parent process
    
    // Close unused pipe ends
    close(stdin_pipe[0]);
    close(stdout_pipe[1]);
    close(stderr_pipe[1]);
    
    // Set environment for child
    if (config->port > 0) {
        char port_env[32];
        snprintf(port_env, sizeof(port_env), "TEKTON_CI_PORT=%d", config->port);
        putenv(port_env);
    }
    
    if (config->tool_name) {
        char name_env[256];
        snprintf(name_env, sizeof(name_env), "TEKTON_CI_TOOL=%s", config->tool_name);
        putenv(name_env);
    }
    
    if (config->socket_mode) {
        // Connect to socket bridge
        int sock_fd = socket(AF_INET, SOCK_STREAM, 0);
        if (sock_fd < 0) {
            perror("socket");
            exit(1);
        }
        
        struct sockaddr_in addr;
        memset(&addr, 0, sizeof(addr));
        addr.sin_family = AF_INET;
        addr.sin_port = htons(config->port);
        addr.sin_addr.s_addr = inet_addr("127.0.0.1");
        
        // Wait for socket bridge to be ready
        int retries = 50;  // 5 seconds
        while (retries-- > 0) {
            if (connect(sock_fd, (struct sockaddr*)&addr, sizeof(addr)) == 0) {
                break;
            }
            usleep(100000);  // 100ms
        }
        
        if (retries <= 0) {
            fprintf(stderr, "Failed to connect to socket bridge on port %d\n", config->port);
            kill(child_pid, SIGTERM);
            exit(1);
        }
        
        fprintf(stderr, "Connected to socket bridge on port %d\n", config->port);
        
        // Bridge socket and stdio
        socket_bridge(sock_fd, stdin_pipe[1], stdout_pipe[0]);
        
        close(sock_fd);
    } else {
        // Direct stdio mode - just relay between parent and child
        fd_set read_fds;
        char buffer[BUFFER_SIZE];
        
        // Make stdout non-blocking
        int flags = fcntl(stdout_pipe[0], F_GETFL, 0);
        fcntl(stdout_pipe[0], F_SETFL, flags | O_NONBLOCK);
        
        // Also handle stderr
        flags = fcntl(stderr_pipe[0], F_GETFL, 0);
        fcntl(stderr_pipe[0], F_SETFL, flags | O_NONBLOCK);
        
        while (1) {
            FD_ZERO(&read_fds);
            FD_SET(STDIN_FILENO, &read_fds);
            FD_SET(stdout_pipe[0], &read_fds);
            FD_SET(stderr_pipe[0], &read_fds);
            
            int max_fd = stdout_pipe[0];
            if (stderr_pipe[0] > max_fd) max_fd = stderr_pipe[0];
            
            if (select(max_fd + 1, &read_fds, NULL, NULL, NULL) < 0) {
                if (errno == EINTR) continue;
                perror("select");
                break;
            }
            
            // Parent stdin -> child stdin
            if (FD_ISSET(STDIN_FILENO, &read_fds)) {
                ssize_t n = read(STDIN_FILENO, buffer, BUFFER_SIZE);
                if (n <= 0) {
                    // Close child's stdin on EOF
                    close(stdin_pipe[1]);
                    stdin_pipe[1] = -1;
                } else {
                    if (stdin_pipe[1] >= 0) {
                        write(stdin_pipe[1], buffer, n);
                    }
                }
            }
            
            // Child stdout -> parent stdout
            if (FD_ISSET(stdout_pipe[0], &read_fds)) {
                ssize_t n = read(stdout_pipe[0], buffer, BUFFER_SIZE);
                if (n > 0) {
                    write(STDOUT_FILENO, buffer, n);
                } else if (n == 0) {
                    // Child closed stdout
                    break;
                }
            }
            
            // Child stderr -> parent stderr
            if (FD_ISSET(stderr_pipe[0], &read_fds)) {
                ssize_t n = read(stderr_pipe[0], buffer, BUFFER_SIZE);
                if (n > 0) {
                    write(STDERR_FILENO, buffer, n);
                }
            }
            
            // Check if child is still running
            int status;
            if (waitpid(child_pid, &status, WNOHANG) > 0) {
                // Child exited
                break;
            }
        }
    }
    
    // Clean up
    close(stdin_pipe[1]);
    close(stdout_pipe[0]);
    close(stderr_pipe[0]);
    
    // Wait for child
    int status;
    waitpid(child_pid, &status, 0);
    
    return WEXITSTATUS(status);
}