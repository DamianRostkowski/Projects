
//Display comment form after click to add comment
function openCommentForm(postId){
    $('.commentFormBg').css({ display : "block" });
    $('#commentedPostId').val(postId);
}

//Closing comment form after click a cronn
function closeCommentForm(){
    $('.commentFormBg').css({ display : "none" })
    $('#commentedPostId').val("");
    $('#commentArea').val("");
}

//turn on or off editing name
function editNameBtn(currentName){
    var field= $('#editName');
    if(field.prop('disabled') === true)
    {
        field.prop('disabled', false);
    }
    else{
        field.prop('disabled', true);
        field.val(currentName);
    }
}

//turn on or off changing password
function editPasswordBtn(){
    field = $('#editPasswords');
    if(field.css('visibility') == 'hidden')
    {
        field.css('visibility', 'visible')
    }
    else{
        field.css('visibility', 'hidden');
        $('#curPas').val('');
        $('#newPas').val('');
    }
}

//turn on or off changing photo
function editImageBtn(){
    field = $('.newImg');
    if(field.css('visibility') == 'hidden')
    {
        field.css('visibility', 'visible')
    }
    else{
        field.css('visibility', 'hidden');
        $('#imgInput').val('');
    }
}

//using DOM to add  eventBindings
document.addEventListener('DOMContentLoaded', function(){
    //hide and delete messege box after 1 second
    setTimeout(function() {
        $('.messageBox').addClass("hide");
      }, 1000);
      setTimeout(function() {
        $('.messageBox').css('display', 'none');
      }, 3000);
    //make dislike logic
    $(document).on('click', '[name="dislike"]', function() {
        var postId = $(this).closest('.post').attr('id');
        var thisButton = $(this);
        var secondButton = $(this).siblings('[name="like"]');
        //use ajax to send our rating without refreshing a site
        $.ajax({
            method:"post",
            url:"/likeDislike",
            data:{like: "false", post_id: postId},
            success:function(res)
            {
                if(res=="dislike")
                    thisButton.css('background-color', 'orangered');
                if(res=="unDislike")
                    thisButton.css('background-color', 'white');
                if(res=="likeToDislike")
                {
                    thisButton.css('background-color', 'orangered');
                    secondButton.css('background-color', 'white');
                }
            }
        });
    });
    //make like logic
    $(document).on('click', '[name="like"]', function() {
        var postId = $(this).closest('.post').attr('id');
        var thisButton = $(this);
        var secondButton = $(this).siblings([name="dislike"]);
        //use ajax to send our rating without refreshing a site
        $.ajax({
            method:"post",
            url:"/likeDislike",
            data:{like: "true", post_id: postId},
            success:function(res)
            {
                if(res=="like")
                    thisButton.css('background-color', 'lime');
                if(res=="unLike")
                    thisButton.css('background-color', 'white');
                if(res=="dislikeToLike")
                {
                    thisButton.css('background-color', 'lime');
                    secondButton.css('background-color', 'white');
                }

            }
        });
    });
    //Set container's height to be equal to height of all posts
    const postsSiteHeight = $('.postsSite').height();
    if(postsSiteHeight > $('main').height())
    {
        $('main').css('height', postsSiteHeight + 100);
    }
    $.ajax({
        method:"post",
        url:"/livesearch",
        data:{text:document.getElementById("findPerson").value},
        success:function(res){
            var data = '<option value="showAll">Show all</option>';
            $.each(res, function(index, row){
                data += '<option value="' + row.name + '">' + row.name +'</option>';
            });
            document.getElementById("searchPersonList").innerHTML = data;
        }
    });
    //live search person in searchbar using ajax to avoid refreshing site
    document.getElementById("findPerson").addEventListener("input", (event) =>{
        text = document.getElementById("findPerson").value;
        $.ajax({
            method:"post",
            url:"/livesearch",
            data:{text:document.getElementById("findPerson").value},
            success:function(res){
                var data = '<option value="showAll">Show all</option>';
                $.each(res, function(index, row){
                    data += '<option value="' + row.name + '">' + row.name +'</option>';
                });
                document.getElementById("searchPersonList").innerHTML = data;
            }
        });
    });
})

document.addEventListener('DOMContentLoaded', function(){
    //Adding few fields when user chose donate type in post maker.
    document.getElementById("postTypes").addEventListener("change", (event) =>
    {
        if(document.getElementById("postTypes").value == "Donate")
        {
            document.getElementById("goal").style.display = "inline-block";
            document.getElementById("dolarSign").style.display = "inline";
        }
        else
        {
            document.getElementById("goal").style.display = "none";
            document.getElementById("dolarSign").style.display = "none";
        }
    });
})