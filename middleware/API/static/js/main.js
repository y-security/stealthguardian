function loadContent(pageName) {
    $('#loading-overlay').show();
    $('#overlay').hide();
    fetch(`/template/${pageName}`)
        .then(response => response.text())
        .then(data => {
           
            const contentElement = document.getElementById("content");
            contentElement.innerHTML = data;

            $.fn.dataTable.tables({ api: true }).each(function() {
                $(this).DataTable().destroy(true);
            });
            
            // Extract and execute scripts from the loaded HTML
            const scripts = contentElement.querySelectorAll('script');
            scripts.forEach(script => {
                const newScript = document.createElement('script');
                newScript.textContent = script.textContent;
                document.head.appendChild(newScript).parentNode.removeChild(newScript);
            });
            const pagetitleElement = document.getElementById("page-title");

            if(window.location.hash && $(window.location.hash+'-link')[0])
                pagetitleElement.innerText = $(window.location.hash+'-link')[0].innerText;
            else
                pagetitleElement.innerText = "Dashboard";
        });
}

function escapeHtml(str) {
    var text = document.createTextNode(str);
    var div = document.createElement('div');
    div.appendChild(text);
    return div.innerHTML;
}


$(document).ready(function() {
    $(window).on('hashchange', handleHashChange);
    handleHashChange(); 
});


function activateMenuItem(itemId) {
    $('.nav-link').removeClass('active');
    $(`#${itemId}`).addClass('active');
}

function handleHashChange() {
    activateMenuItem(window.location.href.split('#')[1]+'-link');
    loadContent(window.location.href.split('#')[1])

}

function showOverlay(content) {
    $('#overlay .overlay-content').html(content);
    $('#overlay').css('display', 'flex');
    $('#overlay').show();
}

function closeOverlay() {
    $('#overlay').hide();
}

function convertTimestamp(timestamp) {
    try {
        // Convert timestamp to integer
        let tsInt = parseInt(timestamp);
        // Convert to readable date
        let date = new Date(tsInt * 1000);
        if (isNaN(date.getTime())) {
            throw new Error("Invalid date");
        }
        let readableDate = date.toISOString().replace('T', ' ').substring(0, 19);
        return readableDate;
    } catch (error) {
        // If conversion fails, return the raw value
        return String(timestamp);
    }
}