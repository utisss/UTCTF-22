# Networking: Malformed Query
In this problem, you're given a packet capture and prompted to look at some malformed packets. If
you look through the capture, the only malformed packets are some weird-looking DNS requests to a
non-standard DNS server. If you look at the first of these queries, you'll see that an RSA public is
being exchanged, and then later requests have completely gibberish names. This should make you
realize that subsequent requests are being encrpyted. However, you should see that the answers to 
later requests are sent in the clear, and appear to be the output of commands. If you get the
public key from the server and send your own encrypted commands, you should be able to leak the
flag.

