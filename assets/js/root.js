function currentTime() {
    var date = new Date()
    date = convertTZ(date, "Asia/Qyzylorda")
    var hour = date.getHours();
    var min = date.getMinutes();
    var sec = date.getSeconds();
    hour = updateTime(hour);
    min  = updateTime(min);
    sec  = updateTime(sec);
    document.getElementById("clock").innerText = hour + " : " + min + " : " + sec;
    var t = setTimeout(currentTime, 1000); /* setting timer */
}

function convertTZ(date, tzString) {
    return new Date((typeof date === "string" ? new Date(date) : date).toLocaleString("en-US", {timeZone: tzString}));   
}

function updateTime(k) { 
    return k < 10 ? "0" + k : k;
}
  
currentTime();