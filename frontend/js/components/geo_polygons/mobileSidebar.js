const MOBILE_MQ = window.matchMedia('(max-width: 767px)')

/**
 * Мобильная панель объектов: полноэкранный overlay поверх страницы.
 * @param {HTMLElement} viewerEl
 * @param {HTMLElement} sidebarEl
 */
export function initMobileSidebar(viewerEl, sidebarEl) {
    const openBtn = document.getElementById('geo-sidebar-open-btn')
    const closeBtn = document.getElementById('geo-sidebar-close-btn')
    const backdrop = document.getElementById('geo-sidebar-backdrop')

    function isMobile() {
        return MOBILE_MQ.matches
    }

    function applySidebarTransform(isOpen) {
        if (!isMobile()) {
            sidebarEl.style.transform = ''
            return
        }
        sidebarEl.style.transform = isOpen ? 'translateX(0)' : 'translateX(100%)'
    }

    function setBackdropVisible(visible) {
        if (!backdrop) return
        if (visible && isMobile()) {
            backdrop.removeAttribute('hidden')
        } else {
            backdrop.setAttribute('hidden', '')
        }
        backdrop.classList.toggle('is-visible', visible && isMobile())
    }

    function setOpen(isOpen) {
        if (!isMobile()) {
            viewerEl.classList.remove('is-geo-sidebar-open')
            sidebarEl.classList.remove('is-open')
            document.body.classList.remove('is-geo-mobile-sidebar-open')
            setBackdropVisible(false)
            openBtn?.setAttribute('aria-expanded', 'false')
            applySidebarTransform(false)
            return
        }

        viewerEl.classList.toggle('is-geo-sidebar-open', isOpen)
        sidebarEl.classList.toggle('is-open', isOpen)
        document.body.classList.toggle('is-geo-mobile-sidebar-open', isOpen)
        setBackdropVisible(isOpen)
        openBtn?.setAttribute('aria-expanded', isOpen ? 'true' : 'false')
        applySidebarTransform(isOpen)
    }

    function open() {
        setOpen(true)
    }

    function close() {
        setOpen(false)
    }

    function openIfMobile() {
        if (isMobile()) open()
    }

    openBtn?.addEventListener('click', open)
    closeBtn?.addEventListener('click', close)
    backdrop?.addEventListener('click', close)

    MOBILE_MQ.addEventListener('change', () => setOpen(false))

    setOpen(false)

    return {
        isMobile,
        open,
        close,
        openIfMobile,
    }
}
