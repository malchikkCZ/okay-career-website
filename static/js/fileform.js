let input = document.getElementById("file");
let label = document.getElementById("file-label");

let file = input.files[0];
if (file) {
    label.innerHTML = "Váš životopis: " + file.name;
}

label.onclick = ()=>{
    input.click()
}

input.addEventListener("change", ()=>{
    file = input.files[0];
    if (file) {
        label.innerHTML = "Váš životopis: " + file.name;
    }
});
