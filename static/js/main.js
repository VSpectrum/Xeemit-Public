$( document ).ready(function() {
    $('.home-header').fadeTo(1500, 1);

    $('.myAccount-btn').fadeTo(1000, 1);
    //nextrow.children('#cabinet-slot-machines-screen-2').show("slide", { direction: "right" }, 250);

    $('.navbar-nav > li > a').click(function(){
    	$('.navbar-nav > li > a').removeClass('nav-active');
    	$(this).addClass('nav-active');
    	location.href=$(this).attr("href");
        //$('.g-recaptcha').children().children().css('height','20px');
    });

});

$('.login-btn').click(function(){
    var datastring = $("#login-form").serialize();
    $.ajax({
        type: "POST",
        url: "/user-login/",
        data: datastring,
        dataType: "text",
        success: function(data) {
            window.location = "/";
        },
        error: function(data) {
            console.log('Error');
            console.log(data);
        }
    });
});


$('.register-btn').click(function(){
    if(grecaptcha.getResponse() != "") {
        var datastring = $("#registration-form").serialize();
        $.ajax({
            type: "POST",
            url: "/user-registration/",
            data: datastring,
            dataType: "text",
            success: function (data) {
                window.location = "/";
            },
            error: function (data) {
                console.log('Error');
                console.log(data);
            }
        });
    }
    else {
        console.log('Captcha not solved.');
    }
});

$("input[name='confirmpassword']").keyup(function() {
    if ($(this).val() != $("input[name='password']").val()) {
        $('.pass-invalid').css('display', 'inline');
        $("input[name='confirmpassword']").css('border', '1px solid red');
        $("input[name='password']").css('border', '1px solid red');
    }
    else {
        $('.pass-invalid').css('display', 'none');
        $("input[name='confirmpassword']").css('border', '1px solid #ccc');
        $("input[name='password']").css('border', '1px solid #ccc');
    }
});

$('.md-close').click(function(event){
    event.preventDefault();
    console.log('modal closed.');
    return;
});

$('#sendMoneyForm .nav-tabs li').click(function(){
    if ($(this).hasClass('cashtab')) {
        $.when( $('#sendMoneyForm .modal-dialog').animate({width:'1200px'}, 400)).done(function(){
            $('#mymap').locationpicker('autosize');
        });
        $('.requestdetails').removeClass('col-md-12');
        $('.requestdetails').addClass('col-md-6');
    }
    else {
        $('#sendMoneyForm .modal-dialog').animate({width:'600px'}, 400);
        $('.requestdetails').removeClass('col-md-6');
        $('.requestdetails').addClass('col-md-12');
    }

});
