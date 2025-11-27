const neighboringCitiesByUsers = JSON.parse(document.getElementById('neighboringCitiesDataByUsers').textContent);
const neighboringCitiesByVisits = JSON.parse(document.getElementById('neighboringCitiesDataByVisits').textContent);
const neighboringCitiesInRegionByUsers = JSON.parse(document.getElementById('neighboringCitiesInRegionDataByUsers').textContent);
const neighboringCitiesInRegionByVisits = JSON.parse(document.getElementById('neighboringCitiesInRegionDataByVisits').textContent);

const isDarkMode = document.documentElement.classList.contains('dark');
const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
const textColor = isDarkMode ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)';

function createMultiBarChart(dataObj) {
  const ctx = document.getElementById(dataObj.elementId).getContext('2d');

  new Chart(ctx, {
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
}

const chartRankByUsers = {
  elementId: 'rankBarChartByUsers',
  data: neighboringCitiesByUsers.map(city => city.visits),
  labels: neighboringCitiesByUsers.map(city => city.title),
  label: 'Количество пользователей',
  backgroundColors: neighboringCitiesByUsers.map(city => {
    if (city.id === window.CITY_ID) {
      return isDarkMode ? 'rgba(37, 99, 235, 0.8)' : 'rgba(37, 99, 235, 0.6)';
    }
    return isDarkMode ? 'rgba(37, 99, 235, 0.2)' : 'rgba(37, 99, 235, 0.15)';
  }),
  borderColors: neighboringCitiesByUsers.map(city => {
    if (city.id === window.CITY_ID) {
      return isDarkMode ? 'rgba(37, 99, 235, 1)' : 'rgba(37, 99, 235, 0.8)';
    }
    return isDarkMode ? 'rgba(37, 99, 235, 0.4)' : 'rgba(37, 99, 235, 0.3)';
  })
}
const chartRankByVisits = {
  elementId: 'rankBarChartByVisits',
  data: neighboringCitiesByVisits.map(city => city.visits),
  labels: neighboringCitiesByVisits.map(city => city.title),
  label: 'Количество посещений',
  backgroundColors: neighboringCitiesByVisits.map(city => {
    if (city.id === window.CITY_ID) {
      return isDarkMode ? 'rgba(37, 99, 235, 0.8)' : 'rgba(37, 99, 235, 0.6)';
    }
    return isDarkMode ? 'rgba(37, 99, 235, 0.2)' : 'rgba(37, 99, 235, 0.15)';
  }),
  borderColors: neighboringCitiesByVisits.map(city => {
    if (city.id === window.CITY_ID) {
      return isDarkMode ? 'rgba(37, 99, 235, 1)' : 'rgba(37, 99, 235, 0.8)';
    }
    return isDarkMode ? 'rgba(37, 99, 235, 0.4)' : 'rgba(37, 99, 235, 0.3)';
  })
}

createMultiBarChart(chartRankByUsers);
createMultiBarChart(chartRankByVisits);

if (window.HAS_REGION) {
  const chartRankInRegionByVisits = {
    elementId: 'rankBarInRegionChartByVisits',
    data: neighboringCitiesInRegionByVisits.map(city => city.visits),
    labels: neighboringCitiesInRegionByVisits.map(city => city.title),
    label: 'Количество посещений',
    backgroundColors: neighboringCitiesInRegionByVisits.map(city => {
      if (city.id === window.CITY_ID) {
        return isDarkMode ? 'rgba(16, 185, 129, 0.8)' : 'rgba(16, 185, 129, 0.6)';
      }
      return isDarkMode ? 'rgba(16, 185, 129, 0.2)' : 'rgba(16, 185, 129, 0.15)';
    }),
    borderColors: neighboringCitiesInRegionByVisits.map(city => {
      if (city.id === window.CITY_ID) {
        return isDarkMode ? 'rgba(16, 185, 129, 1)' : 'rgba(16, 185, 129, 0.8)';
      }
      return isDarkMode ? 'rgba(16, 185, 129, 0.4)' : 'rgba(16, 185, 129, 0.3)';
    })
  }
  const chartRankInRegionByUsers = {
    elementId: 'rankBarInRegionChartByUsers',
    data: neighboringCitiesInRegionByUsers.map(city => city.visits),
    labels: neighboringCitiesInRegionByUsers.map(city => city.title),
    label: 'Количество пользователей',
    backgroundColors: neighboringCitiesInRegionByUsers.map(city => {
      if (city.id === window.CITY_ID) {
        return isDarkMode ? 'rgba(16, 185, 129, 0.8)' : 'rgba(16, 185, 129, 0.6)';
      }
      return isDarkMode ? 'rgba(16, 185, 129, 0.2)' : 'rgba(16, 185, 129, 0.15)';
    }),
    borderColors: neighboringCitiesInRegionByUsers.map(city => {
      if (city.id === window.CITY_ID) {
        return isDarkMode ? 'rgba(16, 185, 129, 1)' : 'rgba(16, 185, 129, 0.8)';
      }
      return isDarkMode ? 'rgba(16, 185, 129, 0.4)' : 'rgba(16, 185, 129, 0.3)';
    })
  }
  createMultiBarChart(chartRankInRegionByVisits);
  createMultiBarChart(chartRankInRegionByUsers);
}