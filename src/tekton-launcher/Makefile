# Makefile for tekton-clean-launch

CC = cc
CFLAGS = -Wall -O2
TARGET = tekton-clean-launch

all: $(TARGET)

$(TARGET): tekton-clean-launch.c
	$(CC) $(CFLAGS) -o $(TARGET) tekton-clean-launch.c

clean:
	rm -f $(TARGET)

install: $(TARGET)
	@echo "To install, copy or symlink $(TARGET) to your PATH"
	@echo "Example: ln -s $(PWD)/$(TARGET) ~/utils/tekton"

.PHONY: all clean install