document.querySelector("input[type=submit]").addEventListener("click", checkPassword);

function checkPassword(evt) {
	evt.preventDefault();
	const socket = new WebSocket("ws://" + window.location.host + "/internal/ws")
	socket.addEventListener('message', (event) => {
		if (event.data == "begin") {
			socket.send("begin");
			socket.send("user " + document.querySelector("input[name=username]").value)
			socket.send("pass " + document.querySelector("input[name=password]").value)
		} else if (event.data == "baduser") {
			document.querySelector(".error").innerHTML = "Unknown user";
			socket.close()
		} else if (event.data == "badpass") {
			document.querySelector(".error").innerHTML = "Incorrect PIN";
			socket.close()
		} else if (event.data.startsWith("session ")) {
			document.cookie = "flask-session=" + event.data.replace("session ", "") + ";";
			socket.send("goodbye")
			socket.close()
			window.location = "/internal/user";
		} else {
			document.querySelector(".error").innerHTML = "Unknown error";
			socket.close()
		} 
	})
}

