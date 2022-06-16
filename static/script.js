let currentTime = function () {
    //Create Date object to retrive the time => hours, minutes, seconds
    const time = new Date();
    let date = time.getDate();
    let month = time.getMonth();
    let year = time.getFullYear();
    let hours = time.getHours();
    let minutes = String(time.getMinutes()).padStart(2, '0');
    let seconds = time.getSeconds();
    let meridian = ((hours) => 12) ? "PM" : "AM";
  
    //timeContent will hold the current time
    let timeContent = `${month}/${date}/${year} - ${hours}:${minutes}:${seconds} ${meridian}`;
  
    return timeContent;
  };
  
  function updateClockTime() {
    //Grab the HTML element
    let clockContent = document.getElementById("clock");
    //update the inner text of the HTML element
    clockContent.innerText = currentTime();
  }
  
  let intervalTime = 1000;
  
  setInterval(updateClockTime, intervalTime);