# Web: HTML2PDF
In this problem, you're sent to a PDF renderer that accepts HTML as input. Additionally, there's a
link to a "super secret" admin login page. If you try including local files, with a payload like
`<iframe src="file:///etc/passwd"></iframe>`, you'll see that a PDF is rendered, although the
contents of the file don't show up in this case (the reason for this is that the wkhtmltopdf utility
can't infer the filetype of `/etc/passwd`). This result might confuse you, but if you try including
a non-existent local file, like `/foo`, you'll see the same result, implying you might need to try 
something different. If you try a more generic payload such as,
```html
<script>
x=new XMLHttpRequest;
x.onload=function() { document.write(this.responseText);};
x.onerror=function() { document.write("The page you are trying to reach is not available."); };
x.open("GET","file:///etc/passwd");
x.send();
</script>
```
you'll see that the file gets displayed properly. You can see other alternatives in [this blog
post](http://hassankhanyusufzai.com/SSRF-to-LFI/) by Hassan Yusufzai.

Looking at `/etc/passwd`, you'll see a user named "WeakPasswordAdmin", suggesting you should try to
crack this user's password to login to the admin page. To crack the user's password, you need to
grab `/etc/passwd` and `/etc/shadow` using the LFI vulnerability. To crack the password using the
John-the-Ripper utility, you need to first unshadow the passwords, i.e. `unshadow passwd shadow >
unshadow.txt`. Then, running `john --users=WeakPasswordAdmin unshadow.txt` should quickly find the
user's password "sunshine".

Entering this password into the admin login page then yields the flag.

