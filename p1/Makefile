CC = gcc -pedantic -pthread
CFLAGS =  -g
SRC=./codigo
OBJ=./obj
SRCLIB=./librerias
LIB=./lib

all: create_dir clean ${OBJ}/picohttpparser.o ${OBJ}/processrequest.o  main

main: ${OBJ}/main.o
	$(CC) $(CFLAGS) -o server ${OBJ}/main.o ${LIB}/processrequest.a  ${LIB}/picoparserlib.a

${OBJ}/processrequest.o: codigo/processrequest.c codigo/processrequest.h
	$(CC) $(CFLAGS) -I./codigo -c $< -o $@
	ar rcs ${LIB}/processrequest.a ${OBJ}/processrequest.o

${OBJ}/picohttpparser.o: librerias/picohttpparser.c librerias/picohttpparser.h
	$(CC) $(CFLAGS) -c $< -o $@
	ar rcs ${LIB}/picoparserlib.a ${OBJ}/picohttpparser.o
${OBJ}/main.o: ${SRC}/main.c
	$(CC) $(CFLAGS) -I./srclib -c $< -o $@


clean:
	rm -rf obj/*.o lib/*.a server

create_dir:
	mkdir -p $(OBJ) $(LIB)

