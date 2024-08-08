function updateGauge(value) {
  console.log("updateGauge called with value: " + value);
  // Ensure the value is between 0 and 100
  value = Math.min(100, Math.max(0, value));
  // Calculate the percentage for the gauge
  let percentage = value + '%';
  // Get the gauge element
  let gaugeElement = document.querySelector('.anvil-role-score-tile-background .gauge-background');
  // Update the gauge's percentage
  gaugeElement.style.setProperty('--gauge-percentage', percentage);
}