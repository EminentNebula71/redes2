CC = gcc -pedantic -pthread
CFLAGS =  -g
SRC=./codigo
OBJ=./obj
LIB=./libreria

all: create_dir clean ${OBJ}/picohttpparser.o ${OBJ}/processrequest.o  practica1_cliente

practica1_cliente: ${OBJ}/practica1_cliente.o
	$(CC) $(CFLAGS) -o server ${OBJ}/practica1_cliente.o ${LIB}/processrequest.a  ${LIB}/picoparserlib.a

${OBJ}/processrequest.o: codigo/processrequest.c codigo/processrequest.h
	$(CC) $(CFLAGS) -I./codigo -c $< -o $@
	ar rcs ${LIB}/processrequest.a ${OBJ}/processrequest.o

${OBJ}/picohttpparser.o: codigo/picohttpparser.c codigo/picohttpparser.h
	$(CC) $(CFLAGS) -c $< -o $@
	ar rcs ${LIB}/picoparserlib.a ${OBJ}/picohttpparser.o
${OBJ}/practica1_cliente.o: ${SRC}/practica1_cliente.c
	$(CC) $(CFLAGS) -I./src -c $< -o $@


clean:
	rm -rf obj/*.o lib/*.a server

create_dir:
	mkdir -p $(OBJ) $(LIB)

