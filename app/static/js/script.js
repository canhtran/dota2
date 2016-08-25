$( document ).ready(function(){
    $('#addPlayer').submit(function(event){
        event.preventDefault();
        var postData = $(this).serializeArray();
	    var formURL = $(this).attr("action");
        $('body').addClass('loaded');
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