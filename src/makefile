.PHONY = all clean

CC = python3
CC2 = spim

FLAGNAME = -f

FILE = main.py

SRCS := $(wildcard ./tests/*.cl)
BINS := $(SRCS:%.cl=%)

all: ${BINS}

%: %.mips
	${CC2} ${FLAGNAME} $< > $@

%.mips: %.cl
	${CC} ${FILE} $< $@


clean:
	rm -rvf *.mips
