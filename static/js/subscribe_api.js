async function send_to_server() {
    const url = document.getElementById('subscribe_button').dataset.url;
    const data = {
        'subscribe': true
    }
    
    let response = await fetch(url);
    if (response.ok) {
      const subscribe_button = document.getElementById('subscribe_button')
      const unsubscribe_button = document.getElementById('unsubscribe_button')

      let json = await response.json();
      if (json.status == 'subscribed') {
        subscribe_button.hidden = true;
        unsubscribe_button.hidden = false;

        const element = document.getElementById('toast_subscribe_api_ok');
        const toast = new bootstrap.Toast(element)
        toast.show()
      }
      else if (json.status == 'unsubscribed') {
        subscribe_button.hidden = false;
        unsubscribe_button.hidden = true;

        const element = document.getElementById('toast_unsubscribe_api_ok');
        const toast = new bootstrap.Toast(element)
        toast.show()
      }
    } else {
      alert("Ошибка отправки HTTP-запроса");
    }

    return false;
}
