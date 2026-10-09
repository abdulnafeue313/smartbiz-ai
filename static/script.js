// Message bhejne ka function
function sendMessage() {
    var input = document.getElementById("userInput");
    var message = input.value.trim();
    
    if (!message) return;

    var messages = document.getElementById("messages");
    messages.innerHTML += '<div class="message user">' + message + '</div>';
    input.value = "";
    messages.scrollTop = messages.scrollHeight;

    fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: message})
    })
    .then(response => response.json())
    .then(data => {
        messages.innerHTML += '<div class="message bot">' + data.reply + '</div>';
        messages.scrollTop = messages.scrollHeight;
    })
    .catch(error => {
        messages.innerHTML += '<div class="message bot">Sorry, kuch problem aa gayi.</div>';
    });
}

// Order form dikhao
function showOrderForm() {
    document.getElementById("orderModal").classList.add("active");
}

// Order form band karo
function closeOrderForm() {
    document.getElementById("orderModal").classList.remove("active");
}

// Order submit karo
function submitOrder() {
    var name = document.getElementById("orderName").value.trim();
    var phone = document.getElementById("orderPhone").value.trim();
    var address = document.getElementById("orderAddress").value.trim();
    var items = document.getElementById("orderItems").value.trim();

    if (!name || !phone || !items) {
        alert("Please naam, phone aur order items zaroor likhein.");
        return;
    }

    fetch("/order", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            name: name,
            phone: phone,
            address: address,
            items: items
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            closeOrderForm();
            document.getElementById("orderName").value = "";
            document.getElementById("orderPhone").value = "";
            document.getElementById("orderAddress").value = "";
            document.getElementById("orderItems").value = "";
        } else {
            alert("Error: " + data.message);
        }
    })
    .catch(error => {
        alert("Kuch problem aa gayi. Dobara try karein.");
    });
}