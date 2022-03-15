game.gb: *.c *.h Makefile
	lcc -o game.gb -Wl-yt1 -Wl-yo4 -Wl-ya0 *.c

run: game.gb
	java.exe -cp ../pb/src org.the429ers.gameboy.GameBoy game.gb

sameboy: game.gb
	open game.gb
