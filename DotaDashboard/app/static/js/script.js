$( document ).ready(function(){
    // Add player Ajax function
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
                if (result == 'done') {
                    window.location.href = "/";
                } else {
                    $('body').removeClass('loaded');
                    alert(result);
                }
            },
        });
    });

    // Update entire database function
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
                if (result == 'done') {
                    window.location.href = "/";
                } else {
                    $('body').removeClass('loaded');
                    alert(result);
                }
            },
        });
    });
});