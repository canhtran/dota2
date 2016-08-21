$( document ).ready(function(){
    $('#addPlayer').submit(function(event){
        event.preventDefault();
        var postData = $(this).serializeArray();
	    var formURL = $(this).attr("action");
        $.ajax({
            type:'post',
            url : formURL,
            data: postData,
            success: function(result) {
                if (result = 'done') {
                    window.location.href = "/";
                }
            },
        });
    });
});

/* Open */
function openNav() {
    document.getElementById("myNav").style.height = "100%";
}

/* Close */
function closeNav() {
    document.getElementById("myNav").style.height = "0%";
}
