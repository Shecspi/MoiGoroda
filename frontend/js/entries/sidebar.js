/**
 * ----------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

document.addEventListener('DOMContentLoaded', () => {
  const sidebar = document.getElementById('sidebar');
  const sidebarToggle = document.getElementById('sidebar-toggle');
  const sidebarClose = document.getElementById('sidebar-close');
  const sidebarBackdrop = document.getElementById('sidebar-backdrop');
  const body = document.body;

  // Проверка наличия необходимых элементов
  if (!sidebar) {
    console.warn('Sidebar element not found');
    return;
  }
  
  if (!sidebarToggle) {
    console.warn('Sidebar toggle button not found');
    return;
  }

  /**
   * Открывает сайдбар на маленьких экранах
   */
  function openSidebar() {
    console.log('=== openSidebar called ===', {
      width: window.innerWidth,
      isLarge: window.innerWidth >= 1280,
      sidebar: sidebar,
      sidebarClasses: sidebar ? sidebar.className : 'N/A'
    });
    
    if (window.innerWidth >= 1280) {
      console.log('Large screen, sidebar should be visible via CSS');
      return;
    }

    if (!sidebar) {
      console.error('Sidebar element not found!');
      return;
    }

    console.log('Before opening:', {
      classes: sidebar.className,
      hasTranslateXFull: sidebar.classList.contains('-translate-x-full'),
      computedTransform: window.getComputedStyle(sidebar).transform,
      computedLeft: window.getComputedStyle(sidebar).left,
      inlineStyle: sidebar.style.cssText
    });

    // Удаляем все классы translate, которые могут конфликтовать
    sidebar.classList.remove('-translate-x-full', 'translate-x-0');
    
    // Получаем текущее состояние transform
    const currentTransform = window.getComputedStyle(sidebar).transform;
    const isCurrentlyHidden = currentTransform && currentTransform !== 'none' && currentTransform.includes('-300');
    
    // Если сайдбар уже открыт, не делаем ничего
    if (!isCurrentlyHidden && sidebar.getAttribute('data-sidebar-state') === 'open') {
      console.log('Sidebar is already open');
      return;
    }
    
    // Сохраняем оригинальный transition из класса Tailwind
    const originalTransition = 'transform 300ms cubic-bezier(0.4, 0, 0.2, 1)';
    
    // Устанавливаем начальное состояние БЕЗ transition (мгновенно)
    sidebar.style.transition = 'none';
    sidebar.style.setProperty('transform', 'translateX(-100%)', 'important');
    
    // Принудительный reflow для применения начального состояния
    sidebar.offsetHeight;
    
    // Обновляем backdrop синхронно
    if (sidebarBackdrop) {
      sidebarBackdrop.style.transition = 'none';
      sidebarBackdrop.classList.remove('opacity-0', 'pointer-events-none');
      sidebarBackdrop.classList.add('opacity-100', 'pointer-events-auto');
      sidebarBackdrop.setAttribute('aria-hidden', 'false');
      sidebarBackdrop.style.opacity = '0';
      sidebarBackdrop.offsetHeight; // Force reflow
    }
    
    sidebarToggle.setAttribute('aria-expanded', 'true');
    body.style.overflow = 'hidden';
    
    // Используем requestAnimationFrame для начала анимации в следующем кадре
    requestAnimationFrame(() => {
      // Включаем transition для плавной анимации
      sidebar.style.transition = originalTransition;
      
      // Устанавливаем конечное состояние - браузер анимирует переход
      sidebar.style.setProperty('transform', 'translateX(0)', 'important');
      
      // Анимируем backdrop
      if (sidebarBackdrop) {
        sidebarBackdrop.style.transition = 'opacity 300ms cubic-bezier(0.4, 0, 0.2, 1)';
        sidebarBackdrop.style.opacity = '1';
      }
      
      sidebar.setAttribute('data-sidebar-state', 'open');
    });
    
    console.log('Opening animation started');
  }

  /**
   * Закрывает сайдбар на маленьких экранах
   */
  function closeSidebar() {
    if (window.innerWidth >= 1280) {
      // На больших экранах сайдбар должен оставаться открытым
      // Но если по какой-то причине он закрыт, открываем его
      if (sidebar.getAttribute('data-sidebar-large') === 'true') {
        sidebar.classList.remove('-translate-x-full', 'translate-x-0');
        const currentStyle = sidebar.style.cssText;
        const cleanedStyle = currentStyle.replace(/transform[^;]*;?/g, '').trim();
        sidebar.style.cssText = cleanedStyle + '; transform: translateX(0) !important;';
        sidebar.style.setProperty('transform', 'translateX(0)', 'important');
        sidebar.setAttribute('data-sidebar-state', 'open');
      }
      return;
    }

    console.log('Closing sidebar...');
    
    // Удаляем все классы translate
    sidebar.classList.remove('-translate-x-full', 'translate-x-0');
    
    // Убеждаемся, что transition включен для плавной анимации
    const transition = 'transform 300ms cubic-bezier(0.4, 0, 0.2, 1)';
    if (!sidebar.style.transition || sidebar.style.transition === 'none') {
      sidebar.style.transition = transition;
    }
    
    // Анимируем backdrop
    if (sidebarBackdrop) {
      if (!sidebarBackdrop.style.transition || sidebarBackdrop.style.transition === 'none') {
        sidebarBackdrop.style.transition = 'opacity 300ms cubic-bezier(0.4, 0, 0.2, 1)';
      }
      sidebarBackdrop.style.opacity = '0';
    }
    
    // Устанавливаем конечное состояние (закрыто) - браузер анимирует переход
    sidebar.style.setProperty('transform', 'translateX(-100%)', 'important');
    
    sidebar.setAttribute('data-sidebar-state', 'closed');
    sidebarToggle.setAttribute('aria-expanded', 'false');
    
    // Ждем окончания анимации перед разблокировкой body
    setTimeout(() => {
      body.style.overflow = '';
      if (sidebarBackdrop) {
        sidebarBackdrop.classList.remove('opacity-100', 'pointer-events-auto');
        sidebarBackdrop.classList.add('opacity-0', 'pointer-events-none');
        sidebarBackdrop.setAttribute('aria-hidden', 'true');
      }
    }, 300); // Длительность анимации
    
    console.log('Closing animation started');
  }

  /**
   * Проверяет, является ли экран большим (xl и выше)
   */
  function isLargeScreen() {
    return window.innerWidth >= 1280;
  }

  /**
   * Обработчик изменения размера окна
   */
  let wasLargeScreen = isLargeScreen();
  
  function handleResize() {
    const nowLargeScreen = isLargeScreen();
    
    if (nowLargeScreen && !wasLargeScreen) {
      // Переход с маленького на большой экран
      // Показываем сайдбар
      sidebar.classList.remove('-translate-x-full', 'translate-x-0');
      const currentStyle = sidebar.style.cssText;
      const cleanedStyle = currentStyle.replace(/transform[^;]*;?/g, '').trim();
      sidebar.style.cssText = cleanedStyle + '; transform: translateX(0) !important;';
      sidebar.style.setProperty('transform', 'translateX(0)', 'important');
      sidebar.setAttribute('data-sidebar-state', 'open');
      sidebar.setAttribute('data-sidebar-large', 'true');
      
      if (sidebarBackdrop) {
        sidebarBackdrop.classList.remove('opacity-100', 'pointer-events-auto');
        sidebarBackdrop.classList.add('opacity-0', 'pointer-events-none');
        sidebarBackdrop.setAttribute('aria-hidden', 'true');
      }
      sidebarToggle.setAttribute('aria-expanded', 'false');
      body.style.overflow = '';
    } else if (!nowLargeScreen && wasLargeScreen) {
      // Переход с большого на маленький экран
      // Закрываем сайдбар
      closeSidebar();
      sidebar.removeAttribute('data-sidebar-large');
    }
    
    wasLargeScreen = nowLargeScreen;
  }
  
  /**
   * Инициализирует состояние сайдбара в зависимости от размера экрана
   */
  function initializeSidebar() {
    console.log('Initializing sidebar...', {
      width: window.innerWidth,
      isLarge: isLargeScreen()
    });
    
    if (isLargeScreen()) {
      // На больших экранах показываем сайдбар
      sidebar.style.setProperty('transform', 'translateX(0)', 'important');
      sidebar.setAttribute('data-sidebar-state', 'open');
      sidebar.setAttribute('data-sidebar-large', 'true');
    } else {
      // На маленьких экранах сайдбар уже скрыт через inline стиль в HTML
      // Просто убеждаемся, что он скрыт (на случай, если что-то изменилось)
      sidebar.style.setProperty('transform', 'translateX(-100%)', 'important');
      sidebar.setAttribute('data-sidebar-state', 'closed');
      sidebar.removeAttribute('data-sidebar-large');
    }
  }

  // Инициализация при загрузке
  initializeSidebar();

  // Обработчики событий
  console.log('Setting up event listeners...', {
    sidebarToggle: !!sidebarToggle,
    sidebarClose: !!sidebarClose,
    sidebarBackdrop: !!sidebarBackdrop
  });
  
  sidebarToggle.addEventListener('click', (e) => {
    console.log('Toggle button clicked!', e);
    e.preventDefault();
    e.stopPropagation();
    openSidebar();
  });
  
  if (sidebarClose) {
    sidebarClose.addEventListener('click', closeSidebar);
  }
  
  if (sidebarBackdrop) {
    sidebarBackdrop.addEventListener('click', closeSidebar);
  }

  // Закрытие при изменении размера экрана
  let resizeTimeout;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(handleResize, 100);
  });

  // Закрытие при нажатии Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !isLargeScreen()) {
      const sidebarState = sidebar.getAttribute('data-sidebar-state');
      if (sidebarState === 'open' || sidebar.style.transform === 'translateX(0)') {
        closeSidebar();
      }
    }
  });

  // Закрытие сайдбара при клике на ссылку внутри сайдбара на маленьких экранах
  const sidebarLinks = sidebar.querySelectorAll('a[href]');
  sidebarLinks.forEach((link) => {
    link.addEventListener('click', () => {
      if (!isLargeScreen()) {
        // Небольшая задержка для плавного перехода
        setTimeout(() => {
          closeSidebar();
        }, 100);
      }
    });
  });

});
