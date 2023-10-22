
function controlFromSlider(fromSlider, toSlider, fromLabel, minDate) {
  const [from, to] = getParsed(fromSlider, toSlider);
  fillSlider(fromSlider, toSlider, toSlider);
  if (from > to) {
    fromSlider.value = to;
  }
  fromLabel.innerText = serializeDate(getSelectedDateRange(fromSlider, toSlider, minDate)[0]);
}

function controlToSlider(fromSlider, toSlider, toLabel, minDate) {
  const [from, to] = getParsed(fromSlider, toSlider);
  fillSlider(fromSlider, toSlider, toSlider);
  setToggleAccessible(toSlider);
  if (from > to) {
    toSlider.value = from;
  }
  toLabel.innerText = serializeDate(getSelectedDateRange(fromSlider, toSlider, minDate)[1]);
}

function getParsed(currentFrom, currentTo) {
  const from = parseInt(currentFrom.value, 10);
  const to = parseInt(currentTo.value, 10);
  return [from, to];
}

const rangeColor = 'var(--accent-color)';
const sliderColor = 'var(--card-color)';

function fillSlider(from, to, controlSlider) {
    const rangeDistance = to.max-to.min;
    const fromPosition = from.value - to.min;
    const toPosition = to.value - to.min;
    controlSlider.style.background = `linear-gradient(
      to right,
      ${sliderColor} 0%,
      ${sliderColor} ${(fromPosition)/(rangeDistance)*100}%,
      ${rangeColor} ${((fromPosition)/(rangeDistance))*100}%,
      ${rangeColor} ${(toPosition)/(rangeDistance)*100}%, 
      ${sliderColor} ${(toPosition)/(rangeDistance)*100}%, 
      ${sliderColor} 100%)`;
}

function setToggleAccessible(currentTarget) {
  const toSlider = document.querySelector('#toSlider');
  if (Number(currentTarget.value) <= 0 ) {
    toSlider.style.zIndex = 2;
  } else {
    toSlider.style.zIndex = 0;
  }
}

function getProtocolDates() {
  const protocols = document.querySelectorAll('.container');
  const procolDates = {};

  protocols.forEach((container) => {
    const dateElement = container.querySelector('.date');
    const dateString = dateElement.textContent;

    if (dateString === 'Datum unbekannt') {
      return;
    }
    const [day, month, year] = dateString.split('.');
    const date = new Date(year, month - 1, day)

    const containerId = container.id;
    const protocolNum = containerId.split('_')[1];
    procolDates[protocolNum] = date;
  });
  return procolDates;
}

function setMonthSliderRange(fromSlider, toSlider, minDate, maxDate, fromLabel, toLabel) {
  const monthCount = (maxDate.getFullYear() - minDate.getFullYear()) * 12 + (maxDate.getMonth() - minDate.getMonth());
  fromSlider.max = monthCount;
  toSlider.max = monthCount;
  fromSlider.value = 0;
  toSlider.value = monthCount;
  dateRange = getSelectedDateRange(fromSlider, toSlider, minDate);
  fromLabel.innerText = serializeDate(dateRange[0]);
  toLabel.innerText = serializeDate(dateRange[1]);
}

const formatter = new Intl.DateTimeFormat('de', { month: 'short' });

function serializeDate(date) {
  const month = formatter.format(date);
  const year = date.getFullYear();
  return `${month} ${year}`;
}

function getSelectedDateRange(fromSlider, toSlider, minDate) {
  const fromMonth = new Date(minDate.getFullYear(), minDate.getMonth() + parseInt(fromSlider.value));
  const toMonth = new Date(minDate.getFullYear(), minDate.getMonth() + parseInt(toSlider.value));
  return [fromMonth, toMonth];
}

const procolDates = getProtocolDates();
const dates = Object.values(procolDates);
const minDate = new Date(Math.min(...dates));
const maxDate = new Date(Math.max(...dates));
const monthCount = (maxDate.getFullYear() - minDate.getFullYear()) * 12 + (maxDate.getMonth() - minDate.getMonth());


const fromSlider = document.querySelector('#fromSlider');
const toSlider = document.querySelector('#toSlider');
const fromLabel = document.querySelector('#fromLabel');
const toLabel = document.querySelector('#toLabel');

console.log(minDate, maxDate, monthCount);

setMonthSliderRange(fromSlider, toSlider, minDate, maxDate, fromLabel, toLabel);  
fillSlider(fromSlider, toSlider, toSlider);
setToggleAccessible(toSlider);

fromSlider.oninput = () => controlFromSlider(fromSlider, toSlider, fromLabel, minDate);
toSlider.oninput = () => controlToSlider(fromSlider, toSlider, toLabel, minDate);