console.log('static is here')
window.addEventListener('load', function(){
	document.getElementById('send-account-message').onclick = function(e) {
			var userName = document.querySelector('#special').value;
			var roomName = document.querySelector('#room_name').value;
			window.location.replace(roomName)
			console.log(userName, roomName)
		}
})
