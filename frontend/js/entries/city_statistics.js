// Загрузка статистики города через AJAX при открытии модального окна

const isDarkMode = document.documentElement.classList.contains('dark');
const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
const textColor = isDarkMode ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)';

// Хранилище для Chart объектов (для корректного уничтожения)
const chartInstances = {};
// Кэш загруженных данных
let cachedStatisticsData = null;

function createMultiBarChart(dataObj) {
  const canvas = document.getElementById(dataObj.elementId);
  if (!canvas) {
    console.warn(`Canvas element not found: ${dataObj.elementId}`);
    return null;
  }

  // Скрываем спиннер и показываем canvas
  const spinner = canvas.parentElement.querySelector('.chart-spinner');
  if (spinner) {
    spinner.classList.add('hidden');
  }
  canvas.classList.remove('hidden');

  // Уничтожаем старый график, если он существует
  if (chartInstances[dataObj.elementId]) {
    chartInstances[dataObj.elementId].destroy();
  }

  const ctx = canvas.getContext('2d');

  const chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: dataObj.labels,
      datasets: [{
        label: dataObj.label,
        data: dataObj.data,
        backgroundColor: dataObj.backgroundColors,
        borderColor: dataObj.borderColors,
        borderWidth: 2,
        borderRadius: 6,
        borderSkipped: false,
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: true,
      scales: {
        x: {
          beginAtZero: true,
          grid: {
            color: gridColor,
            drawBorder: false
          },
          ticks: {
            color: textColor,
            font: {
              size: 11
            }
          }
        },
        y: {
          grid: {
            color: gridColor,
            drawBorder: false
          },
          ticks: {
            color: textColor,
            font: {
              size: 11
            }
          }
        }
      },
      plugins: {
        legend: { 
          display: false 
        },
        tooltip: {
          backgroundColor: isDarkMode ? 'rgba(23, 23, 23, 0.98)' : 'rgba(255, 255, 255, 0.98)',
          titleColor: isDarkMode ? 'rgba(255, 255, 255, 1)' : 'rgba(0, 0, 0, 1)',
          bodyColor: isDarkMode ? 'rgba(255, 255, 255, 0.9)' : 'rgba(0, 0, 0, 0.9)',
          borderColor: isDarkMode ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.2)',
          borderWidth: 1,
          padding: 12,
          cornerRadius: 8,
          boxPadding: 6,
          titleFont: {
            weight: 'bold',
            size: 13
          },
          bodyFont: {
            size: 12
          },
          displayColors: true,
          position: 'nearest',
          yAlign: 'center',
          xAlign: 'left',
          callbacks: {
            label: function(context) {
              return context.dataset.label + ': ' + context.parsed.x;
            }
          }
        }
      }
    }
  });

  // Сохраняем ссылку на график
  chartInstances[dataObj.elementId] = chart;
  return chart;
}

function createChartConfig(elementId, neighboringCities, label, baseColorRgb) {
  return {
    elementId: elementId,
    data: neighboringCities.map(city => city.visits),
    labels: neighboringCities.map(city => city.title),
    label: label,
    backgroundColors: neighboringCities.map(city => {
      if (city.id === window.CITY_ID) {
        return isDarkMode ? `rgba(${baseColorRgb}, 0.8)` : `rgba(${baseColorRgb}, 0.6)`;
      }
      return isDarkMode ? `rgba(${baseColorRgb}, 0.2)` : `rgba(${baseColorRgb}, 0.15)`;
    }),
    borderColors: neighboringCities.map(city => {
      if (city.id === window.CITY_ID) {
        return isDarkMode ? `rgba(${baseColorRgb}, 1)` : `rgba(${baseColorRgb}, 0.8)`;
      }
      return isDarkMode ? `rgba(${baseColorRgb}, 0.4)` : `rgba(${baseColorRgb}, 0.3)`;
    })
  };
}

function updateStatisticsUI(data) {
  // Сохраняем данные в кэш
  cachedStatisticsData = data;

  const rankInCountryByUsersEl = document.getElementById('rankInCountryByUsers');
  const rankInCountryByVisitsEl = document.getElementById('rankInCountryByVisits');

  // Обновляем ранги в стране
  if (rankInCountryByUsersEl) {
    rankInCountryByUsersEl.textContent = 
      `${data.rank_in_country_by_users} из ${data.number_of_cities_in_country}`;
  }
  if (rankInCountryByVisitsEl) {
    rankInCountryByVisitsEl.textContent = 
      `${data.rank_in_country_by_visits} из ${data.number_of_cities_in_country}`;
  }
  
  // Создаём графики для страны
  const chartRankByUsers = createChartConfig(
    'rankBarChartByUsers',
    data.neighboring_cities_by_rank_in_country_by_users,
    'Количество пользователей',
    '37, 99, 235'
  );
  const chartRankByVisits = createChartConfig(
    'rankBarChartByVisits',
    data.neighboring_cities_by_rank_in_country_by_visits,
    'Количество посещений',
    '37, 99, 235'
  );
  
  createMultiBarChart(chartRankByUsers);
  createMultiBarChart(chartRankByVisits);
  
  // Обновляем ранги в регионе (если есть)
  if (window.HAS_REGION) {
    const rankInRegionByUsersEl = document.getElementById('rankInRegionByUsers');
    const rankInRegionByVisitsEl = document.getElementById('rankInRegionByVisits');

    if (rankInRegionByUsersEl) {
      rankInRegionByUsersEl.textContent = 
        `${data.rank_in_region_by_users} из ${data.number_of_cities_in_region}`;
    }
    if (rankInRegionByVisitsEl) {
      rankInRegionByVisitsEl.textContent = 
        `${data.rank_in_region_by_visits} из ${data.number_of_cities_in_region}`;
    }
    
    const chartRankInRegionByUsers = createChartConfig(
      'rankBarInRegionChartByUsers',
      data.neighboring_cities_by_rank_in_region_by_users,
      'Количество пользователей',
      '16, 185, 129'
    );
    const chartRankInRegionByVisits = createChartConfig(
      'rankBarInRegionChartByVisits',
      data.neighboring_cities_by_rank_in_region_by_visits,
      'Количество посещений',
      '16, 185, 129'
    );
    
    createMultiBarChart(chartRankInRegionByUsers);
    createMultiBarChart(chartRankInRegionByVisits);
  }
}

async function loadStatistics() {
  // Если данные уже загружены, просто перерисовываем графики
  if (cachedStatisticsData) {
    updateStatisticsUI(cachedStatisticsData);
    return;
  }

  try {
    const response = await fetch(window.CITY_STATISTICS_API_URL);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    updateStatisticsUI(data);
  } catch (error) {
    console.error('Ошибка загрузки статистики:', error);
    const statisticsContent = document.getElementById('statisticsContent');
    if (statisticsContent) {
      statisticsContent.innerHTML = 
        '<div class="text-center text-red-500 py-8">Ошибка загрузки статистики. Попробуйте позже.</div>';
    }
  }
}

// Слушаем событие открытия модального окна
document.addEventListener('DOMContentLoaded', function() {
  const modal = document.getElementById('cityStatisticModal');
  if (!modal) {
    return;
  }

  let statisticsLoaded = false;
  
  // Preline UI использует класс hs-overlay-open для открытых модалок
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
        if (modal.classList.contains('open') || modal.classList.contains('hs-overlay-open')) {
          if (!statisticsLoaded) {
            loadStatistics();
            statisticsLoaded = true;
          } else if (cachedStatisticsData) {
            // При повторном открытии просто перерисовываем графики
            updateStatisticsUI(cachedStatisticsData);
          }
        }
        // НЕ сбрасываем statisticsLoaded при закрытии — данные уже загружены
      }
    });
  });
  
  observer.observe(modal, { attributes: true });
  
  // Альтернативный способ — через клик на кнопку открытия
  const openButtons = document.querySelectorAll('[data-hs-overlay="#cityStatisticModal"]');
  openButtons.forEach(button => {
    button.addEventListener('click', function() {
      if (!statisticsLoaded) {
        // Небольшая задержка, чтобы модалка успела открыться
        setTimeout(loadStatistics, 100);
        statisticsLoaded = true;
      } else if (cachedStatisticsData) {
        // При повторном открытии просто перерисовываем графики
        setTimeout(() => updateStatisticsUI(cachedStatisticsData), 100);
      }
    });
  });
});
