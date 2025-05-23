export class Button {
    constructor(element, style_on, style_off) {
        this.button = document.getElementById(element);
        this.style_on = style_on;
        this.style_off = style_off;
    }

    get_element() {
        return this.button;
    }

    off() {
        this.button.dataset.type = 'show';
        this.button.classList.remove(this.style_on);
        this.button.classList.add(this.style_off);
    }

    on() {
        this.button.dataset.type = 'hide';
        this.button.classList.remove(this.style_off);
        this.button.classList.add(this.style_on);
    }

    disable() {
        this.button.classList.add('disabled');
    }

    enable() {
        this.button.classList.remove('disabled')
    }
}