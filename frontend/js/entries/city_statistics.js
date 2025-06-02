const ctx = document.getElementById('userProgressChart').getContext('2d');
const ctxNumberOfVisits = document.getElementById('numberOfVisitsChart').getContext('2d');
const neighboringCitiesByUsers = JSON.parse(document.getElementById('neighboringCitiesDataByUsers').textContent);
const neighboringCitiesByVisits = JSON.parse(document.getElementById('neighboringCitiesDataByVisits').textContent);
console.log(window.CITY_ID);

new Chart(ctx, {
  type: 'bar',
  data: {
    labels: [''],
    datasets: [{
      data: [window.NUMBER_OF_USERS_WHO_VISIT_CITY],
      backgroundColor: '#00b894'
    }, {
      data: [window.NUMBER_OF_USERS - window.NUMBER_OF_USERS_WHO_VISIT_CITY],
      backgroundColor: '#dfe6e9'
    }]
  },
  options: {
    indexAxis: 'y', // горизонтальный
    responsive: false,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        mode: 'index',
        yAlign: 'top', // top, center, bottom
        xAlign: 'center',
        callbacks: {
          beforeBody: function () {
            return `Посетило город ${window.NUMBER_OF_USERS_WHO_VISIT_CITY} из ${window.NUMBER_OF_USERS}`;
          },
          label: function() {
            return null; // Убираем стандартные подписи
          }
        }
      }
    },
    scales: {
      x: {
        display: false,
        stacked: true,
        max: window.NUMBER_OF_USERS
      },
      y: {
        display: false,
        stacked: true
      }
    }
  }
});

new Chart(ctxNumberOfVisits, {
  type: 'bar',
  data: {
    labels: [''],
    datasets: [{
      data: [window.NUMBER_OF_VISITS],
      backgroundColor: '#00b894'
    }, {
      data: [window.TOTAL_NUMBER_OF_CITIES - window.NUMBER_OF_VISITS],
      backgroundColor: '#dfe6e9'
    }]
  },
  options: {
    indexAxis: 'y', // горизонтальный
    responsive: false,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        mode: 'index',
        yAlign: 'top', // top, center, bottom
        xAlign: 'center',
        callbacks: {
          beforeBody: function () {
            return `Всего посещений города ${window.NUMBER_OF_VISITS} из ${window.TOTAL_NUMBER_OF_CITIES}`;
          },
          label: function() {
            return null; // Убираем стандартные подписи
          }
        }
      }
    },
    scales: {
      x: {
        display: false,
        stacked: true,
        max: window.TOTAL_NUMBER_OF_CITIES
      },
      y: {
        display: false,
        stacked: true
      }
    }
  }
});

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
      borderWidth: 1,
      borderRadius: 5,
    }]
  },
  options: {
    indexAxis: 'y',
    scales: {
      x: {
        beginAtZero: true,
      }
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        position: 'nearest',
        yAlign: 'center',
        xAlign: 'left',
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
  backgroundColors: neighboringCitiesByUsers.map(city => city.id === window.CITY_ID ? '#FF6B6B' : '#A0C4FF'),
  borderColor: neighboringCitiesByUsers.map(city => city.id === window.CITY_ID ? '#C73636' : '#5C9EFF')
}
const chartRankByVisits = {
  elementId: 'rankBarChartByVisits',
  data: neighboringCitiesByVisits.map(city => city.visits),
  labels: neighboringCitiesByVisits.map(city => city.title),
  label: 'Количество посещений',
  backgroundColors: neighboringCitiesByVisits.map(city => city.id === window.CITY_ID ? '#FF6B6B' : '#A0C4FF'),
  borderColor: neighboringCitiesByVisits.map(city => city.id === window.CITY_ID ? '#C73636' : '#5C9EFF')
}

createMultiBarChart(chartRankByUsers);
createMultiBarChart(chartRankByVisits);