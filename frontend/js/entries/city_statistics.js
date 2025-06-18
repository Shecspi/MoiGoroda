const neighboringCitiesByUsers = JSON.parse(document.getElementById('neighboringCitiesDataByUsers').textContent);
const neighboringCitiesByVisits = JSON.parse(document.getElementById('neighboringCitiesDataByVisits').textContent);
const neighboringCitiesInRegionByUsers = JSON.parse(document.getElementById('neighboringCitiesInRegionDataByUsers').textContent);
const neighboringCitiesInRegionByVisits = JSON.parse(document.getElementById('neighboringCitiesInRegionDataByVisits').textContent);

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
  backgroundColors: neighboringCitiesByUsers.map(city => city.id === window.CITY_ID ? '#5c7cfa' : '#c1c7fb'),
  borderColors: neighboringCitiesByUsers.map(city => city.id === window.CITY_ID ? '#3f55c9' : '#9da4e8')
}
const chartRankByVisits = {
  elementId: 'rankBarChartByVisits',
  data: neighboringCitiesByVisits.map(city => city.visits),
  labels: neighboringCitiesByVisits.map(city => city.title),
  label: 'Количество посещений',
  backgroundColors: neighboringCitiesByVisits.map(city => city.id === window.CITY_ID ? '#5c7cfa' : '#c1c7fb'),
  borderColors: neighboringCitiesByVisits.map(city => city.id === window.CITY_ID ? '#3f55c9' : '#9da4e8')
}

createMultiBarChart(chartRankByUsers);
createMultiBarChart(chartRankByVisits);

if (window.HAS_REGION) {
  const chartRankInRegionByVisits = {
    elementId: 'rankBarInRegionChartByVisits',
    data: neighboringCitiesInRegionByVisits.map(city => city.visits),
    labels: neighboringCitiesInRegionByVisits.map(city => city.title),
    label: 'Количество посещений',
    backgroundColors: neighboringCitiesInRegionByVisits.map(city => city.id === window.CITY_ID ? '#38a169' : '#b9dcb6'),
    borderColors: neighboringCitiesInRegionByVisits.map(city => city.id === window.CITY_ID ? '#2c7a50' : '#8ab17e')
  }
  const chartRankInRegionByUsers = {
    elementId: 'rankBarInRegionChartByUsers',
    data: neighboringCitiesInRegionByUsers.map(city => city.visits),
    labels: neighboringCitiesInRegionByUsers.map(city => city.title),
    label: 'Количество пользователей',
    backgroundColors: neighboringCitiesInRegionByUsers.map(city => city.id === window.CITY_ID ? '#38a169' : '#b9dcb6'),
    borderColors: neighboringCitiesInRegionByUsers.map(city => city.id === window.CITY_ID ? '#2c7a50' : '#8ab17e')
  }
  createMultiBarChart(chartRankInRegionByVisits);
  createMultiBarChart(chartRankInRegionByUsers);
}