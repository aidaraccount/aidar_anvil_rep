function navbar_noModel_noSubs(visible) {
  var s = document.querySelector('.sidebar');
  var b = document.querySelector('.nav-button');
  var content = document.querySelector('.main-content-move')
  var contentNav = document.querySelector('.main-content-move-nav')
  console.log(s)
  console.log(b)
  console.log(content)
  console.log(contentNav)
  
  if (s) {
  s.style.display = visible ? "block" : "none";
  b.style.display = visible ? "block" : "none";
  content.style.display = visible ? "block" : "none";
  contentNav.style.display = visible ? "block" : "none";
  }
}