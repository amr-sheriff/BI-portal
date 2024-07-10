/* Set the width of the sidebar to 250px and the left margin of the page content to 250px */
// function openNav() {
//   document.getElementById("sidebar").style.width = "264px";
//   document.getElementById("wrapper").style.marginLeft = "264px";
// }
//
// /* Set the width of the sidebar to 0 and the left margin of the page content to 0 */
// function closeNav() {
//   document.getElementById("sidebar").style.width = "50px";
//   document.getElementById("wrapper").style.marginLeft = "50px";
// }


document.getElementById("nav-button").addEventListener("click", toggleNav);

function toggleNav(){
    navSize = document.getElementById("sidebar").style.width;
    if (navSize == "264px") {
        return close();
    }
    return open();
}
function open() {
        document.getElementById("sidebar").style.width = "264px";
        document.getElementById("wrapper").style.marginLeft = "264px";
        document.getElementById("footer-text").style.textIndent = "0px";
        sessionStorage.setItem('sidebarshow', 'true');
        // document.body.style.backgroundColor = "rgba(0,0,0,0.4)";
}
function close() {
        document.getElementById("sidebar").style.width = "50px";
        document.getElementById("wrapper").style.marginLeft = "50px";
        document.getElementById("footer-text").style.textIndent = "-420px";
        sessionStorage.setItem('sidebarshow', 'false');
        // document.body.style.backgroundColor = "white";
}

function sidebarLoad(){
    let sidebarshow = sessionStorage.sidebarshow;
    if (sidebarshow == "true") {
        return open();
    }
    // return close();
}
