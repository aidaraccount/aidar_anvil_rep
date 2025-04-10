function navbar_noModel_noSubs(visible) {
  var s = document.querySelector('.sidebar');
  var b = document.querySelector('.nav-button');
  var content = document.querySelector('.main-content-move');
  var contentNav = document.querySelector('.main-content-move-nav');
  
  // Log for debugging
  console.log("navbar_noModel_noSubs called with:", visible);
  console.log("Elements found:", {s, b, content, contentNav});
  
  // Check each element individually before modifying its style
  if (s) {
    s.style.display = visible ? "block" : "none";
  }
  
  if (b) {
    b.style.display = visible ? "block" : "none";
  }
  
  if (content) {
    content.style.display = visible ? "block" : "none";
  }
  
  if (contentNav) {
    contentNav.style.display = visible ? "block" : "none";
  }
}