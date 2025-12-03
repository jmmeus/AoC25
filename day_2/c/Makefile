CC = gcc
CFLAGS = -O3 -Wall -Wextra

all: main main_parallel

main: main.c
	$(CC) $(CFLAGS) -o main main.c

main_parallel: main_parallel.c
	$(CC) $(CFLAGS) -pthread -o main_parallel main_parallel.c

clean:
	rm -f main main_parallel