/*
 * CI Message Bus
 * 
 * Provides non-blocking message queues for CI-CI communication.
 * Uses POSIX message queues for reliability and performance.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <mqueue.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <errno.h>
#include <signal.h>
#include <time.h>

#define MAX_MSG_SIZE 8192
#define MAX_QUEUE_NAME 256
#define QUEUE_PREFIX "/ci_queue_"

typedef struct {
    char sender[64];
    char type[32];
    int priority;
    time_t timestamp;
    char content[MAX_MSG_SIZE - 128];
} CIMessage;

// Create a message queue for a CI
mqd_t create_queue(const char *ci_name) {
    char queue_name[MAX_QUEUE_NAME];
    snprintf(queue_name, sizeof(queue_name), "%s%s", QUEUE_PREFIX, ci_name);
    
    struct mq_attr attr;
    attr.mq_flags = 0;
    attr.mq_maxmsg = 100;
    attr.mq_msgsize = sizeof(CIMessage);
    attr.mq_curmsgs = 0;
    
    // Create queue with read/write permissions
    mqd_t mq = mq_open(queue_name, O_CREAT | O_RDWR | O_NONBLOCK, 0666, &attr);
    if (mq == (mqd_t)-1) {
        perror("mq_open");
        return -1;
    }
    
    return mq;
}

// Open existing queue
mqd_t open_queue(const char *ci_name, int flags) {
    char queue_name[MAX_QUEUE_NAME];
    snprintf(queue_name, sizeof(queue_name), "%s%s", QUEUE_PREFIX, ci_name);
    
    mqd_t mq = mq_open(queue_name, flags | O_NONBLOCK);
    if (mq == (mqd_t)-1) {
        perror("mq_open");
        return -1;
    }
    
    return mq;
}

// Send message to a CI
int send_message(const char *target_ci, const CIMessage *msg) {
    mqd_t mq = open_queue(target_ci, O_WRONLY);
    if (mq == -1) return -1;
    
    // Set priority (0-31, higher is more urgent)
    unsigned int prio = msg->priority;
    if (prio > 31) prio = 31;
    
    int ret = mq_send(mq, (const char*)msg, sizeof(CIMessage), prio);
    mq_close(mq);
    
    return ret;
}

// Receive message (non-blocking)
int receive_message(mqd_t mq, CIMessage *msg) {
    unsigned int prio;
    ssize_t ret = mq_receive(mq, (char*)msg, sizeof(CIMessage), &prio);
    
    if (ret == -1) {
        if (errno == EAGAIN) {
            // No messages available
            return 0;
        }
        return -1;
    }
    
    return 1;  // Message received
}

// Broadcast to all CIs
int broadcast_message(const CIMessage *msg) {
    // TODO: Implement by reading registry and sending to all queues
    return 0;
}

// Clean up queue
void destroy_queue(const char *ci_name) {
    char queue_name[MAX_QUEUE_NAME];
    snprintf(queue_name, sizeof(queue_name), "%s%s", QUEUE_PREFIX, ci_name);
    mq_unlink(queue_name);
}

// Simple command-line interface for testing
int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <command> [args...]\n", argv[0]);
        fprintf(stderr, "Commands:\n");
        fprintf(stderr, "  create <ci_name>              - Create queue for CI\n");
        fprintf(stderr, "  send <target> <msg> [sender]  - Send message\n");
        fprintf(stderr, "  recv <ci_name>                - Receive messages\n");
        fprintf(stderr, "  destroy <ci_name>             - Remove queue\n");
        return 1;
    }
    
    const char *cmd = argv[1];
    
    if (strcmp(cmd, "create") == 0 && argc >= 3) {
        mqd_t mq = create_queue(argv[2]);
        if (mq != -1) {
            printf("Created queue for %s\n", argv[2]);
            mq_close(mq);
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
        msg.priority = 10;
        msg.timestamp = time(NULL);
        
        if (send_message(argv[2], &msg) == 0) {
            printf("Sent message to %s\n", argv[2]);
            return 0;
        }
        return 1;
    }
    
    if (strcmp(cmd, "recv") == 0 && argc >= 3) {
        mqd_t mq = open_queue(argv[2], O_RDONLY);
        if (mq == -1) return 1;
        
        CIMessage msg;
        int count = 0;
        
        while (receive_message(mq, &msg) > 0) {
            printf("Message %d:\n", ++count);
            printf("  From: %s\n", msg.sender);
            printf("  Type: %s\n", msg.type);
            printf("  Priority: %d\n", msg.priority);
            printf("  Content: %s\n", msg.content);
            printf("\n");
        }
        
        if (count == 0) {
            printf("No messages in queue\n");
        }
        
        mq_close(mq);
        return 0;
    }
    
    if (strcmp(cmd, "destroy") == 0 && argc >= 3) {
        destroy_queue(argv[2]);
        printf("Destroyed queue for %s\n", argv[2]);
        return 0;
    }
    
    fprintf(stderr, "Unknown command: %s\n", cmd);
    return 1;
}