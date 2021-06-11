const lanIP = `${window.location.hostname}:5000`;
const socket = io(lanIP);
var chart;
var chart2;
const clearClassList = function (el) {
  el.classList.remove('green');
};

function openModal(jsonObject) {
  titel = document.querySelector('.js-titel');
  modal = document.querySelector('.js-modal');
  overlay = document.getElementById('overlay');
  console.log(jsonObject);
  titel.innerHTML = `Heb je ${jsonObject.message.name} ingescand of uitgescand?`;
  modal.classList.add('active');
  overlay.classList.add('active');

  const btns = document.querySelectorAll('.js-scan');

  btns[0].addEventListener('click', function () {
    socket.emit('F2B_inscan', { barcode: jsonObject });
    btns[0].replaceWith(btns[0].cloneNode(true));
    btns[1].replaceWith(btns[1].cloneNode(true));
    closeModal();
  });
  btns[1].addEventListener('click', function () {
    socket.emit('F2B_uitscan', { barcode: jsonObject });
    btns[0].replaceWith(btns[0].cloneNode(true));
    btns[1].replaceWith(btns[1].cloneNode(true));
    closeModal();
  });
}

function closeModal() {
  modal = document.querySelector('.js-modal');
  overlay = document.getElementById('overlay');
  modal.classList.remove('active');
  overlay.classList.remove('active');
}

function drawLinechart(tijdstip, hoeveelheid) {
  var options = {
    series: [
      {
        name: 'Mililiter',
        data: hoeveelheid,
      },
    ],
    chart: {
      height: '80%',
      width: '92%',
      type: 'line',
      zoom: {
        enabled: false,
      },
    },
    dataLabels: {
      enabled: false,
    },
    stroke: {
      curve: 'straight',
    },
    grid: {
      row: {
        colors: ['#f3f3f3', 'transparent'],
        opacity: 0.5,
      },
    },
    xaxis: {
      categories: tijdstip,
    },
  };
  chart = new ApexCharts(document.querySelector('.js-linechart'), options);
  chart.render();
}

function drawPiechart(hoeveelheid_cat, uniek_cat) {
  var options = {
    series: hoeveelheid_cat,
    chart: {
      width: '185px',
      height: '84%',
      type: 'pie',
    },
    labels: uniek_cat,
    legend: {
      fontSize: '10px',
      position: 'bottom',
      width: 200,
    },
  };
  chart2 = new ApexCharts(document.querySelector('.js-piechart'), options);
  chart2.render();
}
//# endregion

//# region ***  Callback-Visualisation - show___         ***********
const showProducten = function (jsonObject) {
  let html = '';
  for (let product of jsonObject.product) {
    if (product.aantal == 1) {
      html += `<li class="red">${product.naam}(${product.aantal})</li>`;
    } else {
      html += `<li>${product.naam}(${product.aantal})</li>`;
    }
  }
  document.querySelector('.js-producten').innerHTML = html;
};

const showTemperatuur = function (jsonObject) {
  document.querySelector('.js-temperatuur').innerHTML = `${jsonObject.temperatuur.waarde} °C`;
};

const showHistoriek = function (jsonObject) {
  let html = `<tr class="tussentitel">
  <th>Datum</th>
  <th>Waarde</th>
  <th>Actie</th>
</tr>`;
  for (let meting of jsonObject.historiek) {
    datum = meting.datum.split(',').pop();
    datum = datum.replace('GMT', ' ');
    html += `<tr class="onderverdeling">
    <td>${datum}</td>
    <td class="column-center">${meting.waarde}</td>
    <td>${meting.commentaar}</td>
  </tr>`;
  }
  document.querySelector('.js-historiek').innerHTML = html;
};

const showCharts = function (jsonObject) {
  console.log(jsonObject);
  if (jsonObject.message.hoeveelheden != 0) {
    drawPiechart(jsonObject.message.hoeveelheid_cat, jsonObject.message.uniek_cat);
    drawLinechart(jsonObject.message.tijdstip, jsonObject.message.hoeveelheden);
  }
};

//# endregion

//# region ***  Callback-No Visualisation - callback___  ***********

//# endregion

//# region ***  Data Access - get___                     ***********
const getTemperatuur = function () {
  handleData(`http://${lanIP}/temperatuur`, showTemperatuur);
};

const getHistoriek = function () {
  handleData(`http://${lanIP}/historiek`, showHistoriek);
};

const getProducten = function () {
  handleData(`http://${lanIP}/producten`, showProducten);
};

const getChartData = function () {
  handleData(`http://${lanIP}/chartdata`, showCharts);
};

const updateCharts = function () {
  var url = `http://${lanIP}/chartdata`;
  $.getJSON(url, function (response) {
    console.log(response);
    chart.updateOptions({
      series: [
        {
          data: response.message.hoeveelheden,
        },
      ],
      xaxis: {
        categories: response.message.tijdstip,
      },
    });
    chart2.updateOptions({
      series: response.message.hoeveelheid_cat,
      labels: response.message.uniek_cat,
    });
  });
};
//# endregion

//# region ***  Event Listeners - listenTo___            ***********
const listenToSocket = function () {
  console.log('listen to socket functie');
  socket.on('connect', function () {
    console.log('verbonden met socketwebserver');
  });

  socket.on('B2F_scan', function (jsonObject) {
    openModal(jsonObject);
  });
  socket.on('B2F_lock', function (jsonObject) {
    clearClassList(document.querySelector(`.js-button`));
    document.querySelector('.js-button').innerHTML = `<img src="lock_closed_black_24dp.svg" alt="open lock">`;
    document.querySelector('.js-button').setAttribute('data-button', '1');
  });
};

const listenToUI = function () {
  knop = document.querySelector('.js-button');
  powerbtn = document.querySelector('.js-power');
  knop.addEventListener('click', function () {
    status = this.dataset.button;
    if (status == 1) {
      clearClassList(document.querySelector(`.js-button`));
      document.querySelector(`.js-button`).classList.add('green');
      document.querySelector('.js-button').innerHTML = `<img src="lock_open_black_24dp.svg" alt="open lock">`;
      socket.emit('F2B_unlock', { status: status });
      this.dataset.button = 0;
    } else if (status == 0) {
      clearClassList(document.querySelector(`.js-button`));
      document.querySelector('.js-button').innerHTML = `<img src="lock_closed_black_24dp.svg" alt="open lock">`;
      socket.emit('F2B_lock', { status: status });
      this.dataset.button = 1;
    }
  });
  powerbtn.addEventListener('click', function () {
    console.log('shutdown');
    socket.emit('F2B_shutdown', { shutdown: 'shutdown' });
  });
};
//# endregion

//# region ***  Init / DOMContentLoaded                  ***********

const init = function () {
  console.log('dom loaded');
  refreshTemp();
  refreshHistoriek();
  refreshProducten();
  getChartData();
  listenToUI();
  listenToSocket();
};
function refreshTemp() {
  getTemperatuur();
}
function refreshHistoriek() {
  getHistoriek();
}
function refreshProducten() {
  getProducten();
}
function refreshCharts() {
  updateCharts();
}

setInterval(refreshTemp, 5000);
setInterval(refreshHistoriek, 5000);
setInterval(refreshProducten, 5000);
setInterval(refreshCharts, 5000);
document.addEventListener('DOMContentLoaded', init);
//# endregion
