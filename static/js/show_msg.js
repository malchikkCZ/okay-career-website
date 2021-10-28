function show_message(id) {
    let anchor = document.getElementById("anchor_" + id);
    let msg = document.getElementById("message_" + id);
    
    if (msg.style.display == "none") {
        msg.style.display = "table-row";
        anchor.innerHTML = "Skrýt";
    } else {
        msg.style.display = "none";
        anchor.innerHTML = "Zobrazit";
    }
}