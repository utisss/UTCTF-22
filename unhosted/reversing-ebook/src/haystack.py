with open("haystack.in", "w") as out:
    for i in range(0, 2000000):
        out.write("This is not the needle you are looking for (move along).\n")
        if (i == 1789674):
            out.write("utflag{ghidra_isnt_always_the_answer}\n")
