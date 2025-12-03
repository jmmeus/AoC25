CC = gcc
CFLAGS = -O3 -Wall -Wextra

all: main main_parallel

main: main.c
	@mkdir -p bin
	$(CC) $(CFLAGS) -o bin/main main.c

main_parallel: main_parallel.c
	@mkdir -p bin
	$(CC) $(CFLAGS) -pthread -o bin/main_parallel main_parallel.c

clean:
	rm -f bin/main bin/main_parallel