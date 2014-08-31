function prepareDocument() {

    jQuery("form#search").submit(function () {
        text = jQuery("#id_q").val();
        if (text === "" || text === "Search") {
            alert("Enter a search term.");
        }});

    jQuery("#submit_review").click(addProductReview);
    jQuery("#review_form").addClass('hidden');
    jQuery("#add_review").click(slideToggleReviewForm);
    jQuery("#add_review").addClass('visible');
    jQuery("#cancel_review").click(slideToggleReviewForm);

}
function slideToggleReviewForm(){
    jQuery("#review_form").slideToggle();
    jQuery("#add_review").slideToggle();
}
function addProductReview(){

    var review = {title: jQuery("#id_title").val(), content: jQuery("#id_content").val(), rating: jQuery("#id_rating").val(), slug: jQuery("#id_slug").val()};

    jQuery.post("/review/product/add/", review, function(response){jQuery("#review_errors").empty();

    if(response.success == "True"){
        jQuery("#submit_review").attr('disabled', 'disabled');
        jQuery("#no_reviews").empty();
        jQuery("#reviews").prepend(response.html).slideDown();
        new_review = jQuery("#reviews").children(":first");
        new_review.addClass('new_review');
        jQuery("#review_form").slideToggle();
    }
    else{
        jQuery("#review_errors").append(response.html);
    }
    }, "json");
}
jQuery(document).ready(prepareDocument);