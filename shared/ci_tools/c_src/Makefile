CC = gcc
CFLAGS = -Wall -Wextra -O2 -g
LDFLAGS = 

# Platform-specific settings
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    LDFLAGS += -lrt
endif

TARGETS = ci_tool_launcher ci_message_bus

all: $(TARGETS)

ci_tool_launcher: ci_tool_launcher.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

ci_message_bus: ci_message_bus_unix.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

clean:
	rm -f $(TARGETS)

install: all
	mkdir -p ../bin
	cp $(TARGETS) ../bin/

test: all
	./test_launcher.sh

.PHONY: all clean install test