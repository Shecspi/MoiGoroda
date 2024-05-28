async function send_to_server() {
    const url = document.getElementById('subscribe_button').dataset.url;
    const data = {
        'subscribe': true
    }

    let response = await fetch(url);
    if (response.ok) { // если HTTP-статус в диапазоне 200-299
        // получаем тело ответа (см. про этот метод ниже)
        let json = await response.json();
        alert(json.status);
      } else {
        alert("Ошибка HTTP: " + response.status);
      }
}
