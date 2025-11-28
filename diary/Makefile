CC	= gcc
CFLAGS	= -W -Wall
TARGET	= diary

all : $(TARGET)

$(TARGET) : memo.o calendar.o main.o
	$(CC) $(CFLAGS) -o $@ $^

memo.o : memo.c
	$(CC) $(CFLAGS) -c -o $@ $^

calendar.o : calendar.c
	$(CC) $(CFLAGS) -c -o $@ $^

main.o : main.c
	$(CC) $(CFLAGS) -c -o $@ $^

clean :
	rm -rf *.o diary

