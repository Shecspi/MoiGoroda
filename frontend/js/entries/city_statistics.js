const ctx = document.getElementById('userProgressChart').getContext('2d');
const ctxNumberOfVisits = document.getElementById('numberOfVisitsChart').getContext('2d');
const neighboringCities = JSON.parse(document.getElementById('neighboringCitiesData').textContent);
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

const ctx1 = document.getElementById('rankBarChart').getContext('2d');

  const labels = neighboringCities.map(c => c.title);
  const data = neighboringCities.map(c => c.visits);

  new Chart(ctx1, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Количество посещений',
        data: data,
        backgroundColor: neighboringCities.map(c => c.id === window.CITY_ID ? '#2eaf30' : '#00b894')
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
      }
    }
  });