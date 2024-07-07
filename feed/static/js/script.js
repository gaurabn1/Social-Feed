


function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
// ------------- get csrf token End--------------------//


$(document).ready(function () {

    // Add Comment on Posts

    $(document).ready(function(){
        $('button[id^="post_comment-"]').on('click', function(e){
          e.preventDefault()
          let post_id = $(this).data('post-id')
          let comment_text = $(`#comment_form-${post_id} textarea[name='text']`).val()
          
          $.ajax({
            type : 'post',
            url : `/post/add-comment/${post_id}`,
            headers: {
              "X-CSRFToken" : getCookie('csrftoken')
            },
            data: {
                'post_id' : post_id,
                'text': comment_text,
            },
            success: function(response){
                let comments = response.comments
                let commentSection = $(`#comments-${post_id}`);
                commentSection.empty();

                comments.forEach(function(comment){
                    console.log(comment)
                    let userImage = comment.user_image ? comment.user_image : 'static/images/avatar.jpg';
                    let authorUsername = comment.author_username;
                    let censoredText = comment.censored_text;
            
                    let commentHTML = `
                           <div class="card-footer py-3 border-0" style="background-color: rgba(255, 255, 255, 0.05);">
                               <div class="d-flex align-items-center">
                                   <img class="rounded-circle shadow-1-strong me-3" src="${userImage}"  alt="avatar" width="40" height="40" style="object-fit: cover;" />
                                   <div class="w-100">
                                       <h6 class="fw-bold text-primary mb-1">
                                           <a href="{% url 'profile' comment.fields.author.pk %}" style="color: #c8c8c8;">
                                               ${authorUsername}
                                           </a>
                                       </h6>
                                       <p class="small mb-0" style="color: #afacac;">
                                           ${censoredText}
                                       </p>
                                   </div>
                               </div>
                           </div>
                       `;
                        commentSection.prepend(commentHTML);
                })

                commentSection.slideDown();``


            },
            error: function(error){
                console.log(error)
            }
          })
        })
  
      })

    //   Logout

    $('.option').on('click', 'a:not(#logout)', function(e){
        e.preventDefault();
        $('.option a').removeClass('active');
        $(this).addClass('active');
        window.location.href = $(this).attr('href');
    });

    // console.log('Connecting WebSocket...')
    // let ws =  connectWebSocket();

     //-----------Websocket connection----------------//
     function connectWebSocket(){
        let ws_scheme = window.location.protocol === "https" ? "wss" : "ws";
        let ws_url = `${ws_scheme}://${window.location.host}/ws/like-update/`;
        ws = new WebSocket(ws_url);

        ws.onopen = function(){
            console.log('WebSocket connection established.');
            ws.send(JSON.stringify({
                'message' : 'connection requesting...'
            }));
        };

        ws.onmessage = function(event){
            console.log('Message from server:', event.data);
            data = JSON.parse(event.data)
            postid = data['postid']
            likes = data['likes']
            
            if(postid && likes){
                var likeCounter = $(`.like-counter[data-post-id='${postid}']`);
                likeCounter.text(likes);
            }
        };

        ws.onclose = function (event) {
            console.log('WebSocket connection closed:', event);
            setTimeout(connectWebSocket, 1000);
        };

        ws.onerror = function (error) {
            console.error('WebSocket error:', error);
        };
        return ws;
    }
     //-----------Websocket connection End----------------//

     let ws = null;
if (window.location.pathname === '/' || window.location.pathname.startsWith('/profile/')) {
    ws = connectWebSocket();
}
  

    // -------------Update Like on Own Page------------//
    $(".like-button").on('click', function (e) {
        e.preventDefault();

        var postid = $(this).data('post-id');
        console.log(postid)
        var likeCounter = $(this).closest('.interact').find('.like-counter');
        var likes = parseInt(likeCounter.text());

        $.ajax({
            type: "POST",
            url: '/like-counter/',
            data: {
                "id": postid
            },
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function (response) {
                if (response.liked == true) {
                    likes += 1;
                } else {
                    if(likes !== 0){
                        likes -= 1;
                    }
                }
                likeCounter.text(likes);

                if(ws && ws.readyState === WebSocket.OPEN){
                    ws.send(JSON.stringify({
                        'postid'  : postid,
                        'likes' : likes
                    }))
                }
            },
            error: function (xhr, status, error) {
                console.log(xhr, " ", status);
            }
        });

    });
    // ---------Update Like on Page End--------------------//



     //---------------Logout----------------------//
     $('#logout').click( function(e){
        e.preventDefault();
        if(!confirm("Are you sure?")){

        }
        else{
            window.location.href = '/logout/';
        }
     //---------------Logout End----------------------//

    });

    //---------------------Search Form------------------------//

    $('#searchFormButton').on('click', function(e){
        e.preventDefault();
        search_user = $('#searchField').val();

        $.ajax({
            url: `/search-user/${search_user}/`,
            type: 'GET',
            headers: {
                'X-CSRFToken' : getCookie('csrftoken')
            },
            success: function(response){
                $('.search-results').empty();
                if(response.users.length > 0){
                    $.each(response.users, function(index, user){
                        let profileUrl = `/profile/${user.id}/`
                        if(user.first_name){
                            $('.search-results').append(
                                `<a href="${profileUrl}" ><p>` + user.first_name + ' ' + user.last_name + `</p></a>`
                            )
                        }else if(user.username){
                            $('.search-results').append(
                                `<a href="${profileUrl}"><p class="text-capitalize">` + user.username +'</p></a>'
                            )
                        }
                    })
                }else{
                    $('.search-results').append('<p> Users not found.</p>');
                }
            }
        })
    })


    //---------------------Search Form End------------------------//





});